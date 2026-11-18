"""Shared code for the design-sound scripts: library paths, audio measurements, the CLAP model and the search score.

Every script calls `lower_priority()` first and prints through a UTF-8 stdout, so a long job never lags the machine
and Vietnamese text never crashes a pipe on Windows.
"""
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy
import psutil

LIBRARY_DIRECTORY = Path(os.environ.get("SOUND_LIBRARY_DIR", str(Path.home() / "Documents" / "sound-library")))
SOURCES_FILE = LIBRARY_DIRECTORY / "sources.json"
INDEX_FILE = LIBRARY_DIRECTORY / "index.json"
EMBEDDINGS_FILE = LIBRARY_DIRECTORY / "embeddings.npz"
PREVIEW_DIRECTORY = LIBRARY_DIRECTORY / "previews"
VOCABULARY_FILE = Path(__file__).parent / "vocabulary.txt"

DEFAULT_SOURCES = [str(LIBRARY_DIRECTORY / "bank" / "sources")]
AUDIO_EXTENSIONS = {".wav", ".ogg", ".mp3", ".flac"}
MODEL_NAME = "laion/larger_clap_general"
CLAP_SAMPLE_RATE = 48000
CLAP_CLIP_SECONDS = 10
ANALYSIS_SECONDS = 30

BANDS = {"sub": (0, 80), "low": (80, 250), "mid": (250, 4000), "high": (4000, 24000)}
MUSIC_WORDS = {"music", "piano", "marimba", "pizz", "melody", "song", "chord", "loop", "trees", "violin", "cello", "guitar"}
# Stems: a query word that starts with one of these names an impact ("hitting", "bursting", "slammed").
IMPACT_WORDS = {"hit", "slam", "burst", "bang", "crash", "knock", "smash", "pop", "click", "snap", "crack", "thud",
                "clank", "drop", "clunk", "thump", "boom", "explo", "shut", "break", "tap", "impact", "land"}
STOP_WORDS = {"a", "an", "the", "of", "on", "in", "to", "and", "or", "with", "from", "into", "that", "is", "by", "at",
              "for", "someone", "something", "sound", "sounds", "person", "people"}
PUBLIC_SAFE_LICENCES = {"cc0", "cc-by", "elevenlabs"}

# Phrasings that are averaged into one text vector; eval.py measures which set helps.
QUERY_TEMPLATES_PLAIN = ["{}"]
QUERY_TEMPLATES_ENSEMBLE = ["{}", "the sound of {}", "a sound effect of {}", "a recording of {}"]


def lower_priority():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def normalize_path(path):
    return str(Path(path).resolve()).replace("\\", "/")


# ---------------------------------------------------------------- sources, manifests, tags

def load_sources():
    if SOURCES_FILE.exists():
        return json.loads(SOURCES_FILE.read_text(encoding="utf-8"))["folders"]
    return list(DEFAULT_SOURCES)


def save_sources(folders):
    """Writes the folder list; other keys of sources.json (the per-track "music" credits) are kept."""
    LIBRARY_DIRECTORY.mkdir(parents=True, exist_ok=True)
    existing = json.loads(SOURCES_FILE.read_text(encoding="utf-8")) if SOURCES_FILE.exists() else {}
    existing["folders"] = folders
    SOURCES_FILE.write_text(json.dumps(existing, indent=1), encoding="utf-8")


def read_manifest_entries(folder):
    """Map file basename -> manifest entry, from a manifest.json holding a list or a name-keyed dict."""
    manifest_path = Path(folder) / "manifest.json"
    if not manifest_path.exists():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = data if isinstance(data, list) else list(data.values())
    by_basename = {}
    for entry in entries:
        if isinstance(entry, dict) and entry.get("file"):
            by_basename[Path(entry["file"]).name] = entry
    return by_basename


def classify_licence(raw_licence):
    """cc0, cc-by, elevenlabs are clear for commercial use; restricted (NC, ND), other and unknown get a warning."""
    text = (raw_licence or "").lower()
    if not text or text.startswith("unknown"):
        return "unknown"
    if "cc0" in text or "public domain" in text:
        return "cc0"
    # Checked before cc-by: "CC BY-NC 4.0" contains "cc by" and was classed as cc-by until 2026-11-04.
    if re.search(r"\bnc\b|\bnd\b|non-?commercial|no-?deriv", text.replace("-", " ").replace("_", " ")):
        return "restricted"
    if "cc-by" in text or "cc by" in text:
        return "cc-by"
    if "elevenlabs" in text:
        return "elevenlabs"
    return "other"


LICENCE_WARNINGS = {
    "cc-by": "",
    "restricted": "non-commercial or no-derivatives licence: fine for a draft, a takedown or claim risk on a "
                  "monetised or client video",
    "other": "licence not recognised: read the page before a client or monetised use",
    "unknown": "no licence recorded (meme, YouTube or upload): Content ID claim or takedown risk on YouTube, "
               "mute risk on TikTok/IG; fine for drafts and the owner's own posts if accepted",
}


def licence_warning(licence_class):
    """Warn, never block (the owner's licence policy). Empty string means clear."""
    return LICENCE_WARNINGS.get(licence_class, "")


def split_words(text):
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    words = re.findall(r"[a-z]+", spaced.lower())
    return [word[:-1] if len(word) > 3 and word.endswith("s") and not word.endswith("ss") else word for word in words]


def build_tags(relative_path, entry):
    words = split_words(str(relative_path.with_suffix("")).replace("\\", "/"))
    for field in ("role", "library", "title", "music_tags"):
        if entry.get(field):
            words += split_words(str(entry[field]))
    return [word for word in dict.fromkeys(words) if word not in STOP_WORDS and len(word) > 1]


# ---------------------------------------------------------------- audio measurements

def load_mono(path, seconds=None, sample_rate=CLAP_SAMPLE_RATE, offset=0.0):
    import librosa
    samples, _ = librosa.load(path, sr=sample_rate, mono=True, offset=offset, duration=seconds)
    return samples


def to_db(value, floor=-120.0):
    return float(max(floor, 20 * math.log10(max(float(value), 1e-9))))


def integrated_loudness(samples, sample_rate):
    import pyloudnorm
    padded = samples if len(samples) >= sample_rate // 2 else numpy.pad(samples, (0, sample_rate // 2 - len(samples)))
    loudness = pyloudnorm.Meter(sample_rate).integrated_loudness(padded.astype(numpy.float64))
    return float(loudness) if math.isfinite(loudness) else -70.0


def true_peak_db(samples):
    from scipy.signal import resample_poly
    return to_db(numpy.abs(resample_poly(samples, 4, 1)).max())


def band_energy_shares(samples, sample_rate):
    spectrum = numpy.abs(numpy.fft.rfft(samples)) ** 2
    frequencies = numpy.fft.rfftfreq(len(samples), 1 / sample_rate)
    total = spectrum.sum() + 1e-12
    return {name: float(spectrum[(frequencies >= low) & (frequencies < high)].sum() / total)
            for name, (low, high) in BANDS.items()}


def measure_audio(samples, sample_rate, full_duration):
    """Everything the index stores about one file except its embedding."""
    import librosa
    peak = float(numpy.abs(samples).max()) if len(samples) else 0.0
    hop = 128
    envelope = librosa.feature.rms(y=samples, frame_length=256, hop_length=hop)[0]
    envelope_peak = float(envelope.max()) + 1e-12
    start_frame = int(numpy.argmax(envelope >= 0.1 * envelope_peak))
    top_frame = start_frame + int(numpy.argmax(envelope[start_frame:] >= 0.9 * envelope_peak))
    attack_ms = (top_frame - start_frame) * hop / sample_rate * 1000
    centroid = float(librosa.feature.spectral_centroid(y=samples, sr=sample_rate)[0].mean())

    window = sample_rate // 4
    window_count = max(1, len(samples) // window)
    window_db = numpy.array([to_db(numpy.sqrt(numpy.mean(samples[i * window:(i + 1) * window] ** 2) + 1e-12))
                             for i in range(window_count)])
    tail_drop_db = float(window_db.max() - window_db[-max(1, window_count // 5):].mean())
    return {
        "duration": round(float(full_duration), 3),
        "peak_db": round(to_db(peak), 1),
        "rms_db": round(to_db(numpy.sqrt(numpy.mean(samples ** 2) + 1e-12)), 1),
        "lufs": round(integrated_loudness(samples, sample_rate), 1),
        "attack_ms": round(float(attack_ms), 1),
        "lead_ms": round(start_frame * hop / sample_rate * 1000, 1),
        "centroid_hz": round(centroid),
        "band_share": {name: round(share, 4) for name, share in band_energy_shares(samples, sample_rate).items()},
        "tail_drop_db": round(tail_drop_db, 1),
    }


def guess_kind(measures, tags):
    if MUSIC_WORDS & set(tags):
        return "music"
    if measures["duration"] <= 3.0:
        return "oneshot"
    if measures["tail_drop_db"] > 15 and measures["duration"] < 12:
        return "oneshot"
    return "bed"


# ---------------------------------------------------------------- CLAP

def as_tensor(features):
    # Newer transformers return an output object instead of the projected tensor.
    import torch
    return features if isinstance(features, torch.Tensor) else features.pooler_output


class ClapBundle:
    def __init__(self):
        import torch
        from transformers import ClapModel, ClapProcessor
        torch.set_num_threads(4)
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = ClapModel.from_pretrained(MODEL_NAME).to(self.device).eval()
        self.processor = ClapProcessor.from_pretrained(MODEL_NAME)
        self.text_cache = {}

    def embed_clips(self, clips):
        inputs = self.processor(audio=clips, sampling_rate=CLAP_SAMPLE_RATE, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            vectors = as_tensor(self.model.get_audio_features(**inputs))
        return self.torch.nn.functional.normalize(vectors, dim=-1).cpu().numpy()

    def embed_texts(self, texts):
        missing = [text for text in dict.fromkeys(texts) if text not in self.text_cache]
        if missing:
            inputs = self.processor(text=missing, return_tensors="pt", padding=True).to(self.device)
            with self.torch.no_grad():
                vectors = as_tensor(self.model.get_text_features(**inputs))
            vectors = self.torch.nn.functional.normalize(vectors, dim=-1).cpu().numpy()
            self.text_cache.update(dict(zip(missing, vectors)))
        return numpy.stack([self.text_cache[text] for text in texts])

    def query_vector(self, query, templates):
        vectors = self.embed_texts([template.format(query) for template in templates])
        mean = vectors.mean(axis=0)
        return mean / numpy.linalg.norm(mean)

    def release(self):
        del self.model
        if self.device == "cuda":
            self.torch.cuda.empty_cache()


# ---------------------------------------------------------------- index storage

def load_windows():
    """Per-window CLAP vectors of music tracks: {path: (start seconds array, vectors)}. Empty when none are stored."""
    if not EMBEDDINGS_FILE.exists():
        return {}
    stored = numpy.load(EMBEDDINGS_FILE, allow_pickle=False)
    if "window_paths" not in stored.files:
        return {}
    windows = {}
    for path, start, vector in zip(stored["window_paths"], stored["window_starts"], stored["window_vectors"]):
        starts, vectors = windows.setdefault(str(path), ([], []))
        starts.append(float(start))
        vectors.append(vector)
    return {path: (numpy.array(starts), numpy.stack(vectors)) for path, (starts, vectors) in windows.items()}


def load_index():
    """Returns (records list, embedding matrix aligned with it). Empty when nothing is indexed yet."""
    if not INDEX_FILE.exists():
        return [], numpy.zeros((0, 512), dtype=numpy.float32)
    records = json.loads(INDEX_FILE.read_text(encoding="utf-8"))["files"]
    stored = numpy.load(EMBEDDINGS_FILE, allow_pickle=False)
    row_of_path = {path: row for row, path in enumerate(stored["paths"])}
    vectors = numpy.stack([stored["vectors"][row_of_path[record["path"]]] for record in records])
    return records, vectors


def save_index(records, vectors, windows=None):
    """`windows` is {path: (starts, vectors)} for music tracks; it is stored next to the whole-file vectors."""
    LIBRARY_DIRECTORY.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps({"model": MODEL_NAME, "files": records}, indent=1), encoding="utf-8")
    window_paths, window_starts, window_vectors = [], [], []
    for path, (starts, window_matrix) in (windows or {}).items():
        window_paths += [path] * len(starts)
        window_starts += list(starts)
        window_vectors += list(window_matrix)
    numpy.savez(EMBEDDINGS_FILE, paths=numpy.array([record["path"] for record in records]), vectors=vectors,
                window_paths=numpy.array(window_paths), window_starts=numpy.array(window_starts, dtype=numpy.float32),
                window_vectors=numpy.array(window_vectors, dtype=numpy.float32).reshape(-1, 512))


# ---------------------------------------------------------------- scoring

# Mood words a brief uses, mapped to the words the music sources tag with (Kevin MacLeod's "feel" and genre list).
MOOD_SYNONYMS = {
    "tense": ["suspenseful", "intense", "unnerving"], "tension": ["suspenseful", "intense", "unnerving"],
    "suspense": ["suspenseful"], "scary": ["eerie", "unnerving", "dark"], "creepy": ["eerie", "unnerving"],
    "calm": ["calming", "relaxed"], "peaceful": ["calming", "relaxed"], "gentle": ["calming", "relaxed"],
    "playful": ["humorous", "bouncy"], "fun": ["humorous", "bouncy", "bright"], "quirky": ["humorous", "bouncy"],
    "epic": ["epic", "intense", "action"], "heroic": ["epic", "uplifting"], "cinematic": ["soundtrack", "epic"],
    "sad": ["somber"], "melancholy": ["somber"], "sorrow": ["somber"],
    "mysterious": ["mystical", "eerie"], "mystery": ["mysterious", "mystical"],
    "upbeat": ["bright", "uplifting", "bouncy"], "happy": ["bright", "uplifting"], "cheerful": ["bright", "uplifting"],
    "electronic": ["electronica"], "synth": ["electronica"],
    "ambient": ["calming", "relaxed", "mystical"], "documentary": ["soundtrack", "relaxed", "contemporary"],
    "dark": ["dark"], "driving": ["driving", "action"], "energetic": ["driving", "action", "grooving"],
}


def query_words(query):
    words = [word for word in split_words(query) if word not in STOP_WORDS]
    for word in list(words):
        words += MOOD_SYNONYMS.get(word, [])
    return words


def bm25_scores(records, query, k1=1.4, b=0.75):
    documents = [record["tags"] for record in records]
    average_length = max(1.0, sum(len(document) for document in documents) / max(1, len(documents)))
    scores = numpy.zeros(len(records))
    for word in set(query_words(query)):
        containing = sum(1 for document in documents if word in document)
        if not containing:
            continue
        inverse_frequency = math.log(1 + (len(documents) - containing + 0.5) / (containing + 0.5))
        for row, document in enumerate(documents):
            frequency = document.count(word)
            if frequency:
                scores[row] += inverse_frequency * frequency * (k1 + 1) / (
                    frequency + k1 * (1 - b + b * len(document) / average_length))
    return scores


def impact_prior(records, query, strength):
    """Bonus for short sharp one-shots when the query names an impact (hit, slam, burst...)."""
    prior = numpy.zeros(len(records))
    names_an_impact = any(word.startswith(stem) for word in split_words(query) for stem in IMPACT_WORDS)
    if not strength or not names_an_impact:
        return prior
    for row, record in enumerate(records):
        if record["kind"] == "bed":
            prior[row] -= strength
        if record["duration"] <= 2.5:
            prior[row] += strength * 0.5
        if record["attack_ms"] <= 40:
            prior[row] += strength * 0.5
    return prior


def hybrid_scores(similarity, keyword, prior, keyword_weight):
    z_score = (similarity - similarity.mean()) / (similarity.std() + 1e-9)
    keyword_part = keyword / keyword.max() if keyword.max() > 0 else keyword
    return z_score + keyword_weight * keyword_part + prior


DUPLICATE_SIMILARITY = 0.999  # embeddings this close and the same length are the same audio under two names
DUPLICATE_LENGTH_TOLERANCE = 0.02  # seconds


def music_similarity(records, vectors, windows, query_vector):
    """Music score: half the whole-track similarity, half the best 10 s window. Others keep the plain similarity."""
    similarity = vectors @ query_vector
    for row, record in enumerate(records):
        if record["path"] in windows:
            best_window = float((windows[record["path"]][1] @ query_vector).max())
            similarity[row] = 0.5 * similarity[row] + 0.5 * best_window
    return similarity


def rank_sounds(records, vectors, query_vector, query, kind=None, licence="public", max_seconds=None, count=8,
                keyword_weight=2.0, impact_strength=0.5, min_seconds=None, bpm_range=None, windows=None):
    """Best `count` distinct files for a query. Identical audio under two names collapses into one result.

    Returns (rows, aliases, scores, similarity, keyword): `aliases` maps a kept row to the rows hidden behind it.
    """
    similarity = music_similarity(records, vectors, windows, query_vector) if windows else vectors @ query_vector
    keyword = bm25_scores(records, query)
    prior = impact_prior(records, query, impact_strength)
    scores = hybrid_scores(similarity, keyword, prior, keyword_weight)
    allowed = sorted((row for row, record in enumerate(records) if passes_filters(record, kind, licence, max_seconds, min_seconds, bpm_range)),
                     key=lambda row: -scores[row])
    kept, aliases = [], {}
    for row in allowed:
        twin = next((other for other in kept
                     if abs(records[row]["duration"] - records[other]["duration"]) <= DUPLICATE_LENGTH_TOLERANCE
                     and float(vectors[row] @ vectors[other]) > DUPLICATE_SIMILARITY), None)
        if twin is not None:
            aliases.setdefault(twin, []).append(row)
        elif len(kept) < count:
            kept.append(row)
    return kept, aliases, scores, similarity, keyword


def passes_filters(record, kind, licence, max_seconds, min_seconds=None, bpm_range=None):
    if kind and record["kind"] != kind:
        return False
    if licence == "cc0" and record["licence"] != "cc0":
        return False
    if licence == "public" and record["licence"] not in PUBLIC_SAFE_LICENCES:
        return False
    if max_seconds and record["duration"] > max_seconds:
        return False
    if min_seconds and record["duration"] < min_seconds:
        return False
    if bpm_range and not (record.get("bpm") and bpm_range[0] <= record["bpm"] <= bpm_range[1]):
        return False
    return True
