"""Behaviour tests for watch-video. Every fixture is generated with a known answer, then the scripts run as the skill runs them.

Usage: uv run --no-project --with numpy python {{SKILL_DIR}}/tests/test_watch_video.py
Speech-model tests need the cached Parakeet model and Windows speech synthesis; they skip without them.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import wave
from pathlib import Path

import numpy

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL_FOLDER = Path(__file__).resolve().parent.parent
PERCEIVE = SKILL_FOLDER / "scripts" / "perceive.py"
VOICE = SKILL_FOLDER / "scripts" / "voice.py"
CAPTIONS = SKILL_FOLDER / "scripts" / "captions.py"
BUNDLED_TRANSCRIBE = SKILL_FOLDER / "scripts" / "transcribe.py"  # the public pack ships a copy here
TRANSCRIBE = BUNDLED_TRANSCRIBE if BUNDLED_TRANSCRIBE.exists() else Path.home() / ".agents" / "tools" / "transcribe.py"
PARAKEET_FOLDER = Path.home() / ".cache" / "asr-models" / "nemo-parakeet-tdt-0.6b-v2"
SAMPLE_RATE = 16000
STAMP_STRIP = 24  # perceive.py STAMP_STRIP_PIXELS: the time stamp strip under each tile
GRAY_PER_SECOND = 20 * 255 / 219  # the clock video adds 20 luma levels per second; JPEG decoding expands limited range


def run_script(script, *arguments):
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run([sys.executable, str(script), *map(str, arguments)], capture_output=True, env=environment)
    output = completed.stdout.decode("utf-8", "replace") + completed.stderr.decode("utf-8", "replace")
    if completed.returncode != 0:
        raise AssertionError(f"{script.name} failed:\n{output[-1500:]}")
    return output


def ffmpeg(*arguments):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, arguments)], check=True, capture_output=True)


def write_wave(path, samples):
    clipped = numpy.clip(samples, -1.0, 1.0)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes((clipped * 32767).astype(numpy.int16).tobytes())


def voiced_tone(seconds, pitch_hz, amplitude=0.5, end_pitch_hz=None, syllables_per_second=5.0):
    """A voice-like sound: stacked harmonics, gated into syllables, with pitch gliding from start to end."""
    time = numpy.arange(int(seconds * SAMPLE_RATE)) / SAMPLE_RATE
    pitch = numpy.linspace(pitch_hz, end_pitch_hz or pitch_hz, len(time))
    phase = 2 * numpy.pi * numpy.cumsum(pitch) / SAMPLE_RATE
    harmonics = sum(numpy.sin(number * phase) / number for number in range(1, 9))
    gate = 0.5 - 0.5 * numpy.cos(2 * numpy.pi * syllables_per_second * time)
    return amplitude * harmonics / 2.7 * numpy.sqrt(gate)


def speech_with_pauses(amplitude=0.5):
    """Five 3 s phrases, each followed by a 1 s pause. Returns the samples and the pause spans."""
    pieces = []
    pauses = []
    position = 0.0
    for _ in range(5):
        pieces.append(voiced_tone(3.0, 140.0, amplitude))
        position += 3.0
        pieces.append(numpy.zeros(SAMPLE_RATE))
        pauses.append((position, position + 1.0))
        position += 1.0
    return numpy.concatenate(pieces), pauses


def tile_gray_levels(sheet_path, tile_width, tile_height, count):
    """The mean gray of the centre of each tile in a sheet, in reading order. The time stamp sits in a strip below."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(sheet_path), "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    picture = numpy.frombuffer(raw, dtype=numpy.uint8).reshape(-1, tile_width * 5)
    levels = []
    for index in range(count):
        row, column = divmod(index, 5)
        centre_y = row * tile_height + tile_height // 2
        centre_x = column * tile_width + tile_width // 2
        levels.append(float(picture[centre_y - 4:centre_y + 4, centre_x - 4:centre_x + 4].mean()))
    return levels


class Workspace(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp(prefix="watch-video-test-"))
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)


class FrameTimes(Workspace):
    def clock_video(self):
        """Brightness encodes time, so a tile's real moment can be read back from its pixels."""
        path = self.folder / "clock.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=black:s=160x90:r=30:d=10", "-vf", "format=yuv420p,geq=lum='16+T*20':cb=128:cr=128",
               "-c:v", "libx264", "-crf", "8", "-preset", "ultrafast", path)
        return path

    def assert_stamps_true(self, frames_per_second, expected_times):
        output = self.folder / "perceived"
        run_script(PERCEIVE, self.clock_video(), "--out", output, "--fps", frames_per_second, "--tile-width", 100)
        levels = tile_gray_levels(output / "sheet_01.jpg", 100, 56 + STAMP_STRIP, len(expected_times))
        for stamp, level in zip(expected_times, levels):
            shown_time = level / GRAY_PER_SECOND
            self.assertLess(abs(shown_time - stamp), 0.1, f"tile stamped {stamp} s shows the picture at {shown_time:.2f} s")

    def test_stamp_matches_picture_at_two_per_second(self):
        self.assert_stamps_true(2, [0.5 * index for index in range(10)])

    def test_stamp_matches_picture_when_frames_are_sparse(self):
        self.assert_stamps_true(0.2, [0.0, 5.0])


class Reruns(Workspace):
    def test_second_window_does_not_inherit_old_sheets(self):
        video = self.folder / "plain.mp4"
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=160x90:r=10:d=30", "-f", "lavfi", "-i", "sine=f=300:d=30", "-shortest", video)
        output = self.folder / "perceived"
        run_script(PERCEIVE, video, "--out", output)
        self.assertTrue((output / "sheet_02.jpg").exists())
        run_script(PERCEIVE, video, "--out", output, "--from", 20, "--to", 22)
        manifest = (output / "MANIFEST.txt").read_text(encoding="utf-8")
        self.assertFalse((output / "sheet_02.jpg").exists(), "a sheet from the earlier window is still in the folder")
        self.assertNotIn("sheet_02", manifest)
        self.assertEqual(len(list(output.glob("spectrogram_*.png"))), 1)


class Silences(Workspace):
    def perceive_audio(self, samples):
        path = self.folder / "audio.wav"
        write_wave(path, samples)
        output = self.folder / "perceived"
        run_script(PERCEIVE, path, "--out", output)
        return json.loads((output / "perception.json").read_text(encoding="utf-8"))

    def test_one_loud_hit_does_not_turn_quiet_speech_into_silence(self):
        samples, pauses = speech_with_pauses(amplitude=0.02)
        samples[SAMPLE_RATE * 5:SAMPLE_RATE * 5 + 3200] += 0.95 * numpy.sin(2 * numpy.pi * 120 * numpy.arange(3200) / SAMPLE_RATE)
        perception = self.perceive_audio(samples)
        silent_seconds = sum(gap["end"] - gap["start"] for gap in perception["silences"])
        true_pause_seconds = sum(end - start for start, end in pauses)
        self.assertLess(silent_seconds, true_pause_seconds + 1.5, "speech was reported as silence")
        self.assertGreaterEqual(len(perception["sounds"]), 4)

    def test_real_silence_is_still_silence(self):
        samples, pauses = speech_with_pauses()
        perception = self.perceive_audio(samples)
        for start, end in pauses[:-1]:
            self.assertTrue(any(gap["start"] < start + 0.3 and gap["end"] > end - 0.3 for gap in perception["silences"]),
                            f"the pause at {start} s was not reported")

    def assert_pauses_found_under_a_bed(self, bed):
        samples, pauses = speech_with_pauses()
        perception = self.perceive_audio(samples + bed)
        self.assertEqual(perception["silences"], [], "a steady bed leaves no true silence")
        for start, end in pauses[:-1]:
            self.assertTrue(any(dip["start"] < end and dip["end"] > start for dip in perception["dips"]),
                            f"the pause at {start} s is hidden: {perception['dips']}")

    def test_pauses_are_found_under_noise(self):
        # The voice sits about 11 dB above this noise. Closer than 9 dB is a known limit: the pause no longer stands out.
        random = numpy.random.default_rng(7)
        self.assert_pauses_found_under_a_bed(0.03 * random.standard_normal(SAMPLE_RATE * 20))

    def test_pauses_are_found_under_a_held_note(self):
        time = numpy.arange(SAMPLE_RATE * 20) / SAMPLE_RATE
        self.assert_pauses_found_under_a_bed(0.06 * numpy.sin(2 * numpy.pi * 220 * time))


class LongAudio(Workspace):
    def test_ten_minutes_of_steady_clicks_keeps_tempo_and_stays_fast(self):
        samples = numpy.zeros(SAMPLE_RATE * 600, dtype=numpy.float64)
        click = 0.8 * numpy.sin(2 * numpy.pi * 1000 * numpy.arange(160) / SAMPLE_RATE)
        for position in range(0, len(samples) - 160, SAMPLE_RATE // 2):
            samples[position:position + 160] = click
        path = self.folder / "clicks.wav"
        write_wave(path, samples)
        began = time.time()
        run_script(PERCEIVE, path, "--out", self.folder / "perceived")
        perception = json.loads((self.folder / "perceived" / "perception.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(perception["tempo"], 120.0, delta=1.0)
        self.assertLess(time.time() - began, 60.0)


class CutFrames(Workspace):
    def flash_video(self):
        path = self.folder / "flash.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=0x223344:s=160x90:r=30:d=30", "-f", "lavfi", "-i", "color=c=white:s=160x90:r=30:d=30",
               "-filter_complex", "[0][1]overlay=enable='between(t,12.1,12.3)'", "-c:v", "libx264", "-preset", "ultrafast", path)
        return path

    def test_short_shot_between_sparse_frames_is_shown(self):
        output = self.folder / "perceived"
        run_script(PERCEIVE, self.flash_video(), "--out", output, "--fps", 0.1, "--tile-width", 100)
        perception = json.loads((output / "perception.json").read_text(encoding="utf-8"))
        self.assertTrue(any(abs(cut - 12.1) < 0.04 for cut in perception["cuts"]), perception["cuts"])
        sheets = sorted(output.glob("cuts_*.jpg"))
        self.assertTrue(sheets, "no frames were saved at the cuts")
        levels = tile_gray_levels(sheets[0], 100, 56 + STAMP_STRIP, 1)
        self.assertGreater(levels[0], 200, "the frame at the cut does not show the white flash")
        self.assertIn("cuts_01.jpg", (output / "MANIFEST.txt").read_text(encoding="utf-8"))

    def test_cut_between_two_dark_shots_is_found(self):
        # Scene score 0.18 here, under the bright-cut threshold; the frame eval missed two such cuts before 2026-11-07.
        path = self.folder / "dark.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=0x181a1e:s=640x360:r=30:d=2,drawbox=x=40:y=40:w=200:h=60:color=white:t=fill",
               "-f", "lavfi", "-i", "color=c=0x181a1e:s=640x360:r=30:d=2,drawbox=x=380:y=240:w=120:h=90:color=yellow:t=fill",
               "-filter_complex", "[0][1]concat=n=2:v=1", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", path)
        output = self.folder / "perceived"
        run_script(PERCEIVE, path, "--out", output)
        perception = json.loads((output / "perception.json").read_text(encoding="utf-8"))
        self.assertEqual([round(cut, 1) for cut in perception["cuts"]], [2.0])


class OddFiles(Workspace):
    def test_non_ascii_file_name_through_a_pipe(self):
        path = self.folder / "Interview für Köln.wav"
        write_wave(path, voiced_tone(3.0, 140.0))
        self.assertIn("für Köln", run_script(PERCEIVE, path, "--out", self.folder / "perceived"))

    def test_silent_video_has_no_audio_files(self):
        video = self.folder / "silent.mp4"
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=160x90:r=10:d=4", video)
        output = self.folder / "perceived"
        self.assertIn("audio: none", run_script(PERCEIVE, video, "--out", output))


class VoiceMeasures(Workspace):
    SENTENCES = (("Plain opening line here.", 120.0, 0.25, 120.0, 0.0, 3.0),
                 ("Second plain line here.", 120.0, 0.25, 120.0, 0.3, 3.0),
                 ("Third plain line here.", 120.0, 0.25, 120.0, 0.3, 3.0),
                 ("This one is much higher.", 170.0, 0.25, 170.0, 0.3, 3.0),
                 ("This one is much louder.", 120.0, 0.60, 120.0, 0.3, 3.0),
                 ("After a very long wait.", 120.0, 0.25, 120.0, 2.0, 3.0),
                 ("Does this one rise up?", 120.0, 0.25, 300.0, 0.3, 3.0))

    def build(self):
        pieces = []
        words = []
        position = 0.0
        for text, pitch, amplitude, end_pitch, pause, seconds in self.SENTENCES:
            pieces.append(numpy.zeros(int(pause * SAMPLE_RATE)))
            position += pause
            pieces.append(voiced_tone(seconds, pitch, amplitude, end_pitch))
            tokens = text.split()
            step = seconds / len(tokens)
            for index, token in enumerate(tokens):
                words.append({"start": round(position + index * step, 2), "end": round(position + (index + 1) * step, 2), "text": token})
            position += seconds
        audio = self.folder / "voice.wav"
        write_wave(audio, numpy.concatenate(pieces))
        words_path = self.folder / "words.json"
        words_path.write_text(json.dumps(words), encoding="utf-8")
        output = self.folder / "voice"
        run_script(VOICE, audio, "--words", words_path, "--out", output)
        return json.loads((output / "voice.json").read_text(encoding="utf-8")), (output / "voice.txt").read_text(encoding="utf-8")

    def test_each_change_is_measured_against_the_speaker_baseline(self):
        sentences, table = self.build()
        self.assertEqual(len(sentences), len(self.SENTENCES))
        plain, _, _, higher, louder, waited, rising = sentences
        self.assertLess(abs(plain["pitch_semitones"]), 1.0)
        self.assertAlmostEqual(higher["pitch_semitones"], 12 * math.log2(170 / 120), delta=1.0)
        self.assertLess(abs(louder["pitch_semitones"]), 1.0)
        self.assertAlmostEqual(louder["loudness_decibels"], 20 * math.log10(0.60 / 0.25), delta=1.5)
        self.assertAlmostEqual(waited["pause_seconds"], 2.0, delta=0.15)
        self.assertEqual(rising["ending"], "rising")
        self.assertEqual(plain["ending"], "level")
        self.assertIn("* ", table, "stand-out sentences are not marked")
        self.assertIn("not an emotion", table.lower())


class VoiceOnLivelySpeech(Workspace):
    def test_only_real_outliers_stand_out_when_every_sentence_varies(self):
        """Real speech moves around all the time: a mark on nearly every sentence tells the reader nothing."""
        random = numpy.random.default_rng(11)
        pieces = []
        words = []
        position = 0.0
        outliers = {12: 2.2, 27: 2.2}
        for index in range(40):
            pitch = 130.0 * 2 ** (random.normal(0.0, 2.0) / 12) * outliers.get(index, 1.0)
            amplitude = 0.25 * 10 ** (random.normal(0.0, 2.0) / 20)
            seconds = float(random.uniform(1.6, 2.4))
            pieces.append(voiced_tone(seconds, pitch, amplitude))
            tokens = ["word"] * 7 + ["end."]
            step = seconds / len(tokens)
            for token_index, token in enumerate(tokens):
                words.append({"start": round(position + token_index * step, 2), "end": round(position + (token_index + 1) * step, 2), "text": token})
            position += seconds
        audio = self.folder / "lively.wav"
        write_wave(audio, numpy.concatenate(pieces))
        words_path = self.folder / "words.json"
        words_path.write_text(json.dumps(words), encoding="utf-8")
        run_script(VOICE, audio, "--words", words_path, "--out", self.folder)
        sentences = json.loads((self.folder / "voice.json").read_text(encoding="utf-8"))
        marked = [index for index, sentence in enumerate(sentences) if sentence["stands_out"]]
        self.assertIn(12, marked)
        self.assertIn(27, marked)
        self.assertIn("pitch", sentences[12]["stands_out"])
        self.assertLessEqual(len(marked), 10, f"{len(marked)} of 40 sentences marked")

    def test_octave_errors_do_not_inflate_pitch_range(self):
        samples = voiced_tone(3.0, 120.0)
        samples[SAMPLE_RATE:SAMPLE_RATE + 8000] = voiced_tone(0.5, 240.0)
        audio = self.folder / "octave.wav"
        write_wave(audio, samples)
        words_path = self.folder / "words.json"
        words_path.write_text(json.dumps([{"start": 0.0, "end": 3.0, "text": "steady."}]), encoding="utf-8")
        run_script(VOICE, audio, "--words", words_path, "--out", self.folder)
        sentence = json.loads((self.folder / "voice.json").read_text(encoding="utf-8"))[0]
        self.assertLess(sentence["pitch_range_semitones"], 3.0)

    def test_rate_is_not_judged_on_a_two_word_sentence(self):
        audio = self.folder / "short.wav"
        write_wave(audio, numpy.concatenate([voiced_tone(2.0, 120.0), voiced_tone(0.3, 120.0), voiced_tone(2.0, 120.0)]))
        words = [{"start": 0.25 * index, "end": 0.25 * (index + 1), "text": "word"} for index in range(7)]
        words.append({"start": 1.75, "end": 2.0, "text": "end."})
        words += [{"start": 2.0, "end": 2.15, "text": "No"}, {"start": 2.15, "end": 2.3, "text": "way."}]
        words += [{"start": 2.3 + 0.25 * index, "end": 2.3 + 0.25 * (index + 1), "text": "word"} for index in range(7)]
        words.append({"start": 4.05, "end": 4.3, "text": "end."})
        words_path = self.folder / "words.json"
        words_path.write_text(json.dumps(words), encoding="utf-8")
        run_script(VOICE, audio, "--words", words_path, "--out", self.folder)
        short = json.loads((self.folder / "voice.json").read_text(encoding="utf-8"))[1]
        self.assertIsNone(short["rate_change"])
        self.assertIn("rate n/a", (self.folder / "voice.txt").read_text(encoding="utf-8"))


class Captions(Workspace):
    ROLLING = """WEBVTT
Kind: captions
Language: de

00:00:01.000 --> 00:00:03.000 align:start position:0%
 
guten<00:00:01.500><c> morgen</c><00:00:02.000><c> liebe</c><00:00:02.500><c> grüße</c>

00:00:03.000 --> 00:00:03.010 align:start position:0%
guten morgen liebe grüße


00:00:03.010 --> 00:00:05.000 align:start position:0%
guten morgen liebe grüße
heute<00:00:03.500><c> ist</c><00:00:04.000><c> schönes</c><00:00:04.500><c> wetter</c>

00:00:08.000 --> 00:00:09.000
tschüss köln
"""

    def test_rolling_captions_become_one_clean_transcript(self):
        path = self.folder / "video.de.vtt"
        path.write_text(self.ROLLING, encoding="utf-8")
        output = self.folder / "out"
        run_script(CAPTIONS, path, "--out", output)
        words = json.loads((output / "words.json").read_text(encoding="utf-8"))
        self.assertEqual(" ".join(word["text"] for word in words), "guten morgen liebe grüße heute ist schönes wetter tschüss köln")
        self.assertEqual(words[-2]["text"], "tschüss")
        self.assertAlmostEqual(words[-2]["start"], 8.0, delta=0.01)
        self.assertIn("[00:08] tschüss köln", (output / "transcript.txt").read_text(encoding="utf-8"))
        starts = {word["text"]: word["start"] for word in words}
        # YouTube's inline times win over an even spread: "morgen" is stamped 1.5 s, "wetter" 4.5 s.
        self.assertAlmostEqual(starts["morgen"], 1.5, delta=0.01)
        self.assertAlmostEqual(starts["grüße"], 2.5, delta=0.01)
        self.assertAlmostEqual(starts["heute"], 3.01, delta=0.01)
        self.assertAlmostEqual(starts["wetter"], 4.5, delta=0.01)

    def test_sound_tags_stay_in_the_transcript_but_not_in_the_words(self):
        path = self.folder / "tagged.vtt"
        path.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nnow<00:00:02.000><c> [Music]</c><00:00:03.000><c> again</c>\n", encoding="utf-8")
        output = self.folder / "out"
        run_script(CAPTIONS, path, "--out", output)
        words = json.loads((output / "words.json").read_text(encoding="utf-8"))
        self.assertEqual([(word["text"], word["start"]) for word in words], [("now", 1.0), ("again", 3.0)])
        self.assertIn("[Music]", (output / "transcript.txt").read_text(encoding="utf-8"))


@unittest.skipUnless(PARAKEET_FOLDER.exists() and sys.platform == "win32", "needs the Parakeet model and Windows speech synthesis")
class SpeechModel(Workspace):
    TEXT = ("We shipped the new engine on Tuesday, and honestly nobody expected it to work. "
            "The first test failed after eleven seconds. Maria changed one number on Thursday morning. "
            "The third test ran for four hundred seconds without a problem.")

    def speak(self):
        path = self.folder / "speech.wav"
        script = ("Add-Type -AssemblyName System.Speech; $voice = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                  f"$voice.SetOutputToWaveFile('{path}'); $voice.Speak('{self.TEXT}'); $voice.Dispose()")
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], check=True, capture_output=True)
        return path

    def transcribe(self, media, output, *arguments):
        command = ["uv", "run", "--no-project", "--python", "3.12", "--with", "onnx-asr[cpu,hub]", "--with", "psutil",
                   "python", "-I", str(TRANSCRIBE), str(media), "--out", str(output), *map(str, arguments)]
        completed = subprocess.run(command, capture_output=True, check=True)
        return completed.stdout.decode("utf-8", "replace")

    def test_clean_speech_is_trusted_and_a_window_keeps_the_full_transcript(self):
        speech = self.speak()
        output = self.folder / "out"
        self.assertNotIn("UNRELIABLE", self.transcribe(speech, output))
        full = (output / "transcript.txt").read_text(encoding="utf-8")
        self.assertIn("Maria", full)
        self.assertNotIn("[unreliable]", full)
        self.assertIn("logprob", json.loads((output / "words.json").read_text(encoding="utf-8"))[0])
        self.transcribe(speech, output, "--from", 0, "--to", 3)
        self.assertEqual((output / "transcript.txt").read_text(encoding="utf-8"), full, "the window overwrote the full transcript")
        self.assertTrue((output / "transcript_0-3.txt").exists())
        self.assertTrue((output / "words_0-3.json").exists())

    def test_speech_the_model_cannot_understand_is_flagged(self):
        reversed_speech = self.folder / "reversed.wav"
        ffmpeg("-i", self.speak(), "-af", "areverse", reversed_speech)
        output = self.folder / "out"
        self.assertIn("UNRELIABLE", self.transcribe(reversed_speech, output, "--no-fallback"))
        self.assertIn("[unreliable]", (output / "transcript.txt").read_text(encoding="utf-8"))


def timed_words(text, start=0.0, step=0.4):
    return [{"start": round(start + index * step, 2), "end": round(start + (index + 1) * step, 2), "text": word}
            for index, word in enumerate(text.split())]


class TranscriptComparison(Workspace):
    def test_a_misheard_word_and_a_number_written_out_are_told_apart(self):
        compare = SKILL_FOLDER / "scripts" / "compare_transcripts.py"
        first = self.folder / "captions.json"
        second = self.folder / "model.json"
        first.write_text(json.dumps(timed_words("Der Zug fährt um 30 Minuten nach acht ab, sagte der Sprecher heute Morgen.")), encoding="utf-8")
        second.write_text(json.dumps(timed_words("Der Zug fährt um dreißig Minuten nach acht ab, sagte der Sprecher heute morgen.")
                                     + timed_words("noch ein Satz", start=40)), encoding="utf-8")
        output = run_script(compare, first, second)
        self.assertIn("0 word disagreements, 1 number spans", output)
        second.write_text(json.dumps(timed_words("Der Zug fährt um 30 Minuten nach Acht ab, sagte der Sprecher heute Abend.")), encoding="utf-8")
        output = run_script(compare, first, second, "--names", "captions", "model")
        self.assertIn("1 word disagreements, 0 number spans", output)
        self.assertIn("captions: Morgen.", output)
        self.assertIn("model   : Abend.", output)


class Subtitles(Workspace):
    def test_cues_respect_limits_and_a_translation_must_keep_every_time(self):
        make_srt = SKILL_FOLDER / "scripts" / "make_srt.py"
        words = timed_words("Guten Morgen zusammen. Heute bauen wir einen kleinen Tisch aus altem Holz und zeigen jeden Schritt ganz genau")
        words += timed_words("Zuerst messen wir.", start=12)
        words_path = self.folder / "words.json"
        words_path.write_text(json.dumps(words), encoding="utf-8")
        original = self.folder / "de.srt"
        run_script(make_srt, "build", words_path, "--out", original, "--max-characters", "30", "--max-seconds", "4")
        blocks = original.read_text(encoding="utf-8").strip().split("\n\n")
        texts = [block.splitlines()[2] for block in blocks]
        self.assertEqual(texts[0], "Guten Morgen zusammen.")
        self.assertEqual(texts[-1], "Zuerst messen wir.")
        self.assertTrue(all(len(text) <= 30 for text in texts), texts)
        self.assertEqual(" ".join(texts), " ".join(word["text"] for word in words))
        translated = self.folder / "en.srt"
        translated.write_text("\n\n".join("\n".join(block.splitlines()[:2] + [f"line {index}"]) for index, block in enumerate(blocks)) + "\n", encoding="utf-8")
        self.assertIn("ok", run_script(make_srt, "check", original, translated))
        broken = translated.read_text(encoding="utf-8").replace("00:00:00,000", "00:00:00,100", 1)
        translated.write_text(broken, encoding="utf-8")
        with self.assertRaises(AssertionError):
            run_script(make_srt, "check", original, translated)


class SpeakerTranscript(unittest.TestCase):
    def test_transcript_breaks_at_each_change_of_speaker(self):
        diarize = load_script_module("diarize")
        turns = [{"start": 0.0, "end": 2.0, "speaker": "S1"}, {"start": 2.5, "end": 5.0, "speaker": "S2"}, {"start": 61.0, "end": 63.0, "speaker": "S1"}]
        words = timed_words("Hallo und willkommen", 0.2, 0.5) + timed_words("danke schön", 2.6, 0.6) + timed_words("bis bald", 61.2, 0.5)
        words.append({"start": 2.05, "end": 2.2, "text": "äh"})  # in the gap, closest to S1's end
        words.sort(key=lambda word: word["start"])
        lines = diarize.transcript_by_speaker(turns, words)
        self.assertEqual(lines, ["[00:00] S1: Hallo und willkommen äh", "[00:02] S2: danke schön", "[01:01] S1: bis bald"])


def load_script_module(name):
    import importlib.util
    specification = importlib.util.spec_from_file_location(name, SKILL_FOLDER / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class QwenFallback(unittest.TestCase):
    """Segmenting and word spreading of transcribe_qwen.py, without loading the 1.9 GB model."""

    def setUp(self):
        import importlib.util
        bundled = SKILL_FOLDER / "scripts" / "transcribe_qwen.py"
        path = bundled if bundled.exists() else Path.home() / ".agents" / "tools" / "transcribe_qwen.py"
        specification = importlib.util.spec_from_file_location("transcribe_qwen", path)
        self.qwen = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(self.qwen)

    def test_long_audio_is_cut_at_pauses_and_no_segment_is_too_long(self):
        rate = self.qwen.SAMPLE_RATE
        speech, pauses = speech_with_pauses()
        waveform = numpy.concatenate([speech] * 3).astype(numpy.float32)
        boundaries = self.qwen.segment_boundaries(waveform)
        lengths = [(end - start) / rate for start, end in zip(boundaries, boundaries[1:])]
        self.assertTrue(all(length <= self.qwen.SEGMENT_SECONDS for length in lengths), lengths)
        pause_spans = [(start + 20 * repeat, end + 20 * repeat) for repeat in range(3) for start, end in pauses]
        for cut in boundaries[1:-1]:
            seconds = cut / rate
            self.assertTrue(any(start - 0.05 <= seconds <= end + 0.05 for start, end in pause_spans), f"cut at {seconds:.2f} s splits a phrase")

    def test_words_are_spread_and_unspaced_scripts_split_by_character(self):
        spaced = self.qwen.spread_words("guten morgen liebe grüße", "German", 10.0, 12.0)
        self.assertEqual([word["text"] for word in spaced], ["guten", "morgen", "liebe", "grüße"])
        self.assertEqual((spaced[0]["start"], spaced[-1]["end"]), (10.0, 12.0))
        unspaced = self.qwen.spread_words("こんにちは", "Japanese", 0.0, 1.0)
        self.assertEqual(len(unspaced), 5)


class TutorialPipeline(Workspace):
    def test_captions_import_without_running_and_drop_rolling_repeats(self):
        captions = load_script_module("captions")
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nadd a cube\n\n00:00:03.000 --> 00:00:05.000\nadd a cube\nthen bevel it\n"
        _, lines = captions.words_and_lines(vtt)
        self.assertEqual(lines, ["[00:01] add a cube", "[00:03] then bevel it"])

    def test_pick_filters_by_title_and_length_then_sorts_by_views(self):
        import argparse
        fetcher = load_script_module("fetch_tutorial_transcripts")
        videos = [
            {"id": "a", "title": "Fire shader tutorial", "seconds": 600, "views": 10, "date": "20240101"},
            {"id": "b", "title": "Lego geometry nodes", "seconds": 900, "views": 500, "date": "20230101"},
            {"id": "c", "title": "Channel update #shorts", "seconds": 50, "views": 9000, "date": "20250101"},
            {"id": "d", "title": "Three hour livestream", "seconds": 10800, "views": 800, "date": "20250101"},
        ]
        arguments = argparse.Namespace(include=None, exclude=r"#shorts|livestream", min_minutes=2, max_minutes=90, top=0, sort="views")
        self.assertEqual([video["id"] for video in fetcher.pick_videos(videos, arguments)], ["b", "a"])

    def test_batches_split_by_total_minutes(self):
        fetcher = load_script_module("fetch_tutorial_transcripts")
        videos = [{"id": str(index), "seconds": 1800} for index in range(5)]
        self.assertEqual(fetcher.write_batches(self.folder, videos, "demo", batch_minutes=60), 3)
        first = (self.folder / "batches" / "demo-1.txt").read_text(encoding="utf-8").split()
        self.assertEqual(len(first), 2)

    def test_name_check_flags_misheard_and_old_names_only(self):
        checker = load_script_module("check_blender_names")
        names = SKILL_FOLDER / "data" / "blender-names.json"
        if not names.exists():
            self.skipTest("data/blender-names.json missing; run blender_names_dump.py")
        known, _ = checker.load_known_names(names)
        notes = self.folder / "notes.md"
        notes.write_text(
            "Add a Distribute Points on Faces node, then Instance on Points -> Realize Instances.\n"
            "Use a Mix RGB node for the colour.\n"
            "Feed it into the Instants on Pointz node.\n"
            "Cloth Dynamics (Experimental) -> Custom Force.\n",
            encoding="utf-8",
        )
        flagged = {candidate: hint for _, _, candidate, hint in checker.check_file(notes, known)}
        self.assertEqual(set(flagged), {"Mix RGB", "Instants on Pointz"})
        self.assertIn("Mix (Color)", flagged["Mix RGB"])
        self.assertIn("instance on points", flagged["Instants on Pointz"])

    def test_spoken_transcript_old_names_are_found_in_lower_case(self):
        # A Blender 2.90 fog tutorial said "mix in the search mix rgb"; the Title Case check missed it (2026-11-07).
        checker = load_script_module("check_blender_names")
        transcript = self.folder / "transcript.txt"
        transcript.write_text("[03:54] rgb so mix in the search mix rgb\n[04:10] we invert it and add some bloom\n", encoding="utf-8")
        flagged = [(line, candidate) for _, line, candidate, _ in checker.check_spoken_file(transcript)]
        self.assertEqual(flagged, [(1, "mix rgb")])


class ScreenReading(unittest.TestCase):
    """read_screen.py pairing, change check and source names, on hand-made OCR lines (no OCR model needed)."""

    def setUp(self):
        self.reader = load_script_module("read_screen")

    def test_letter_vote_beats_every_single_reading(self):
        # Real slips from a fog tutorial: no single reading is right, the per-letter vote is.
        readings = [("irina-iriser-2Y4dE8sdhic-unsplash", 1), ("irina-iriser-2Y4dE8sdnlc-unsplash", 2),
                    ("irina-iriser-2Y4dE8sdhkc-unsplash", 2), ("irina-iriser-ZY4dE8sdhlc-unsplash", 2),
                    ("irina-iriser-2Y4dE8sdhlc-ursplash", 2)]
        voted, agreeing = self.reader.vote_name(readings)
        self.assertEqual(voted, "irina-iriser-2Y4dE8sdhlc-unsplash")
        self.assertEqual(agreeing, 0)

    def test_first_letter_beside_an_icon_survives_case_flips(self):
        # The fog run: PP-OCRv6 read irina, Irina and rina; Xiaomi-OCR-0 read urina and trina. Case-split votes lost to u.
        readings = [("irina-iriser-2Y4dE8sdhic-unsplash", 1), ("Irina-iriser-2Y4dE8sdhic-unsplash", 1),
                    ("rina-iriser-2Y4dE8sdhic-unsplash", 1), ("urina-iriser-2Y4dE8sdhlc-unsplash", 2),
                    ("trina-iriser-2Y4dE8sdhlc-unsplash", 2), ("irina-iriser-2Y4dE8sdhlc-unsplash", 2),
                    ("Irina-iriser-2Y4dE8sdhlc-unsplash", 2)]
        voted, agreeing = self.reader.vote_name(readings)
        self.assertEqual(voted, "irina-iriser-2Y4dE8sdhlc-unsplash")

    def test_slipped_readings_share_one_cluster_and_other_names_do_not(self):
        clusters = []
        first = self.reader.find_cluster(clusters, "uploads_files_909440_Bendy_Beect", "CGTrader")
        first["readings"].append(("uploads_files_909440_Bendy_Beect", 1))
        self.assertIs(self.reader.find_cluster(clusters, "uploads_fles_909440_Bendy_Beech", "CGTrader"), first)
        self.assertIsNot(self.reader.find_cluster(clusters, "uploads_files_123_Oak_Tree", "CGTrader"), first)

    def test_numbers_take_the_label_left_of_them_on_the_same_row(self):
        lines = [
            {"text": "Pos", "x0": 100, "y0": 50, "x1": 130, "y1": 62},
            {"text": "0.567", "x0": 150, "y0": 51, "x1": 190, "y1": 63},
            {"text": "Scale", "x0": 100, "y0": 90, "x1": 140, "y1": 102},
            {"text": "1.000", "x0": 300, "y0": 90, "x1": 340, "y1": 102},
            {"text": "Location X -0.35 m", "x0": 400, "y0": 200, "x1": 560, "y1": 212},
        ]
        fields = self.reader.pair_fields(lines, 1280)
        self.assertEqual(fields, {"Pos": "0.567", "Scale": "1.000", "Location X": "-0.35"})

    def test_a_small_value_change_counts_and_a_still_frame_does_not(self):
        still = numpy.full((360, 640), 40, dtype=numpy.uint8)
        edited = still.copy()
        edited[100:112, 300:330] = 230  # one value field redrawn, under 0.2% of the frame
        self.assertEqual(self.reader.changed_blocks(still, still.copy()), 0)
        self.assertGreaterEqual(self.reader.changed_blocks(still, edited), 1)

    def test_a_dropped_decimal_point_is_not_a_value_change(self):
        # Tutorial run, 2026-11-07: "W 1.320 -> 1320" and "Pos 0.000 -> 0000" were OCR slips, not edits.
        self.assertTrue(self.reader.same_digits("1.320", "1320"))
        self.assertTrue(self.reader.same_digits("0.000", "0000"))
        self.assertFalse(self.reader.same_digits("0.567", "0.484"))

    def test_source_names_are_recognised_through_ocr_slips(self):
        # Strings as RapidOCR read them from a tutorial Outliner (2026-11-07), letter slips included.
        meanings = [meaning for _, meaning in self.reader.find_sources("uploads_fles_909440_Bendy_Beect")]
        self.assertTrue(any("CGTrader" in meaning for meaning in meanings), meanings)
        self.assertTrue(self.reader.find_sources("rina-riser-2Y4dE8sdhic-unsplash"))
        self.assertTrue(self.reader.find_sources("kiara_1_dawn_4k (1).hdr"))
        self.assertFalse(self.reader.find_sources("Principled Volume"))


class ProfileComparison(unittest.TestCase):
    def setUp(self):
        self.profile = load_script_module("compare_profile")

    def test_fog_height_is_measured_against_the_base_shot(self):
        base = numpy.full((100, 160), 30.0, dtype=numpy.float32)
        video = base.copy()
        video[60:] += 80  # fog over the bottom 40%
        render = base.copy()
        render[90:] += 80  # fog over the bottom 10%
        report = self.profile.compare(video, render, base, base, bands=10)
        self.assertAlmostEqual(report["frame_reach"], 0.4)
        self.assertAlmostEqual(report["render_reach"], 0.1)

    def test_a_faint_wash_is_reported_as_no_visible_effect(self):
        base = numpy.full((100, 160), 30.0, dtype=numpy.float32)
        render = base + 6  # the over-thin fog of the 2026-11-07 rebuild added +8 at most
        report = self.profile.compare(render, render, base, base, bands=10)
        self.assertEqual(report["render_reach"], 0.0)


class WindowPicking(unittest.TestCase):
    """pick_windows.py on hand-made transcript, screen text, replay curve and cuts (no video needed)."""

    def setUp(self):
        self.picker = load_script_module("pick_windows")

    def windows_for(self, terms, seen=()):
        transcript = [(time, "so today we talk about the project") for time in range(0, 600, 15)]
        transcript += [(130, "the benchmark score is here"), (410, "and the project again")]
        screen = [(275, "SWE-bench 13.86%")]
        heatmap = [{"start_time": 500, "end_time": 520, "value": 1.0}]
        windows = self.picker.score_windows(600, terms, transcript, screen, [], heatmap, [5, 6, 7, 8], 20, list(seen))
        return self.picker.pick(windows, 3, 600, 20)

    def test_rare_terms_win_over_words_said_all_through(self):
        picked = self.windows_for(["project", "benchmark", "swe-bench"])
        starts = [item["start"] for item in picked]
        self.assertIn(120.0, starts)  # "benchmark" said once
        self.assertTrue(any(260 <= start <= 275 for start in starts))  # SWE-bench on screen
        self.assertIn(0.0, starts)  # the opening is always offered

    def test_seen_windows_are_not_offered_again(self):
        picked = self.windows_for(["benchmark"], seen=[(110, 150)])
        self.assertFalse(any(item["start"] < 150 and item["end"] > 110 for item in picked))

    def test_replay_peak_counts_without_terms(self):
        picked = self.windows_for([])
        self.assertTrue(any(490 <= item["start"] <= 500 for item in picked))


class PulseCounting(unittest.TestCase):
    def test_counts_blinks_faster_than_sheets_sample(self):
        counter = load_script_module("count_pulses")
        blink = [200] * 4 + [30] * 4  # 0.13 s on, 0.13 s off at 30 fps
        values = [30] * 10 + blink * 11 + [30] * 10
        pulses, threshold = counter.find_pulses(values, 30.0, 18.6, 0.5)
        self.assertEqual(len(pulses), 11)
        self.assertAlmostEqual(pulses[0][0], 18.6 + 10 / 30, places=2)

    def test_flat_region_has_no_pulses(self):
        counter = load_script_module("count_pulses")
        pulses, threshold = counter.find_pulses([100, 102, 101, 103] * 20, 30.0, 0.0, 0.5)
        self.assertEqual(pulses, [])


class WatchEntry(unittest.TestCase):
    """watch.py decisions that do not need a download or a model."""

    def setUp(self):
        self.watch = load_script_module("watch")

    def test_tutorial_titles_turn_screen_reading_on(self):
        self.assertTrue(self.watch.TUTORIAL_TITLE.search("Realistic Fog in Blender 4.2 | Tutorial"))
        self.assertTrue(self.watch.TUTORIAL_TITLE.search("Unity beginner course, part 3"))
        self.assertIsNone(self.watch.TUTORIAL_TITLE.search("Devin, the first AI software engineer"))

    def test_upload_age_flags_old_videos(self):
        import datetime
        long_ago = (datetime.date.today() - datetime.timedelta(days=400)).strftime("%Y%m%d")
        self.assertGreater(self.watch.upload_age_days(long_ago), self.watch.OLD_UPLOAD_DAYS)
        self.assertIsNone(self.watch.upload_age_days(None))


class Annotating(Workspace):
    def setUp(self):
        super().setUp()
        self.annotate = load_script_module("annotate")

    def test_text_notes_keep_the_words_and_read_the_kind(self):
        path = self.folder / "notes.md"
        path.write_text("Intro line\n- [01:02.5] Callout: \"Tango delta\" heard\n- [00:03.0] hard cut — measured\n",
                        encoding="utf-8")
        points, spans = self.annotate.parse_notes(path)
        self.assertEqual([note["t"] for note in points], [3.0, 62.5])
        self.assertEqual(points[1]["text"], "Callout: \"Tango delta\" heard")
        self.assertEqual(points[1]["kind"], "heard")
        self.assertEqual(spans, [])

    def test_json_notes_carry_spans_and_boxes(self):
        path = self.folder / "notes.json"
        path.write_text(json.dumps([{"t": 5, "text": "rover hangs", "kind": "seen", "box": [0.1, 0.1, 0.4, 0.5]},
                                    {"start": 31.5, "end": 165, "text": "camera: down-look"}]), encoding="utf-8")
        points, spans = self.annotate.parse_notes(path)
        self.assertEqual(points[0]["box"], [0.1, 0.1, 0.4, 0.5])
        self.assertEqual(spans[0]["end"], 165.0)

    def test_ocr_boxes_undo_crop_and_upscale(self):
        record = {"frame": [800, 400], "source": [1920, 1080], "crop": [100, 200, 400, 200]}
        line = {"x0": 400, "y0": 200, "x1": 800, "y1": 400}
        fraction = self.annotate.box_to_fraction(line, record, [1280, 720])
        self.assertAlmostEqual(fraction[0], 300 / 1920)
        self.assertAlmostEqual(fraction[3], 400 / 1080)
        self.assertAlmostEqual(self.annotate.box_to_fraction(line, {}, [1600, 800])[2], 0.5)

    def test_captions_break_on_pauses(self):
        words = [{"start": 0.0, "end": 0.3, "text": "Heat"}, {"start": 0.3, "end": 0.6, "text": "shield&nbsp;"},
                 {"start": 2.0, "end": 2.4, "text": "sep."}]
        lines = self.annotate.caption_lines(words)
        self.assertEqual([line["text"] for line in lines], ["Heat shield", "sep."])

    def test_panel_keeps_words_off_the_picture(self):
        painter = self.annotate.Painter(640, 360, 162)
        record = {"frame": [640, 360], "lines": [{"text": "LVS valid", "score": 0.99, "x0": 100, "y0": 50, "x1": 300, "y1": 90}]}
        note = {"t": 107.4, "text": "Callout: \"LVS valid\" heard", "kind": "heard", "box": None}
        image = numpy.asarray(painter.overlay(record, [640, 360], [note], [], "LVS valid"))
        picture_alpha = image[:360, :, 3]
        self.assertEqual(int(picture_alpha[60:80, 120:280].max()), 0)
        self.assertGreater(int(picture_alpha[50:53, 100:300].max()), 0)
        self.assertGreater(int((image[360:, :, 3] > 0).sum()), 1000)

    def test_notes_move_away_from_text(self):
        record = {"frame": [100, 100], "lines": [{"x0": 0, "y0": 0, "x1": 40, "y1": 20}]}
        self.assertTrue(self.annotate.Painter.text_heavier_on_left(record, [100, 100]))
        record["lines"][0].update({"x0": 60, "x1": 100})
        self.assertFalse(self.annotate.Painter.text_heavier_on_left(record, [100, 100]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
