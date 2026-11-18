"""Run yt-dlp so it survives TLS-inspecting antivirus, and report its exit code instead of hiding it.

Behind antivirus that re-signs HTTPS traffic (Norton and others), the yt-dlp binary on PATH trusts only its bundled
certificates and fails with `curl: (60)` or `CERTIFICATE_VERIFY_FAILED`. The same yt-dlp run as a library under
`uv run --with "yt-dlp[default]" --with truststore`, after `truststore.inject_into_ssl()`, trusts the Windows or
macOS certificate store and works.

As a command (same arguments and exit code as yt-dlp):
  uv run --no-project python ytdlp_runner.py <yt-dlp arguments>
As a module: `run_yt_dlp(arguments)` returns a CompletedProcess.

WATCH_VIDEO_YTDLP picks the way: `auto` (default) tries the binary and switches to the library on a certificate
error or when the binary is missing; `library` always uses the library; `binary` never falls back.
"""

import os
import re
import subprocess
import sys

CERTIFICATE_ERROR = re.compile(r"CERTIFICATE_VERIFY_FAILED|curl: \(60\)|certificate verify failed|unable to get local issuer", re.I)
BASE_ARGUMENTS = ["--js-runtimes", "node", "--encoding", "utf-8"]
MODE_VARIABLE = "WATCH_VIDEO_YTDLP"


def library_command(arguments):
    """Command that runs yt-dlp as a library with the system certificate store."""
    return [
        "uv", "run", "--no-project", "--with", "yt-dlp[default]", "--with", "truststore",
        "python", "-I", os.path.abspath(__file__), "--as-library", *arguments,
    ]


def run_library(arguments, **run_options):
    return subprocess.run(library_command([*BASE_ARGUMENTS, *arguments]), **run_options)


def run_binary(arguments, **run_options):
    return subprocess.run(["yt-dlp", *BASE_ARGUMENTS, *arguments], **run_options)


def run_yt_dlp(arguments, **run_options):
    """Runs yt-dlp with captured text output. Never raises for a failed download: check returncode."""
    run_options = {"capture_output": True, "text": True, "encoding": "utf-8", "errors": "replace", **run_options}
    mode = os.environ.get(MODE_VARIABLE, "auto")
    if mode == "library":
        return run_library(arguments, **run_options)
    try:
        result = run_binary(arguments, **run_options)
    except FileNotFoundError:
        if mode == "binary":
            raise
        print("yt-dlp is not on PATH; running it as a library through uv.", file=sys.stderr)
        return run_library(arguments, **run_options)
    certificate_failed = result.returncode != 0 and CERTIFICATE_ERROR.search(result.stderr or "")
    if certificate_failed and mode == "auto":
        print("yt-dlp could not verify a certificate (TLS-inspecting antivirus?); retrying as a library with truststore.", file=sys.stderr)
        return run_library(arguments, **run_options)
    return result


def explain_failure(result):
    """Last lines of yt-dlp's error output, for a message that says why a run failed."""
    lines = (result.stderr or result.stdout or "").strip().splitlines()
    return " | ".join(lines[-3:])[:400] or f"exit code {result.returncode}"


def main_as_library(arguments):
    import truststore

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    truststore.inject_into_ssl()
    import yt_dlp

    try:
        yt_dlp.main(arguments)
    except SystemExit as finished:
        return finished.code if isinstance(finished.code, int) else (0 if finished.code is None else 1)
    return 0


def main():
    arguments = sys.argv[1:]
    if arguments[:1] == ["--as-library"]:
        sys.exit(main_as_library(arguments[1:]))
    # Output is captured so a certificate error can be seen, then replayed unchanged.
    result = run_yt_dlp(arguments)
    sys.stdout.write(result.stdout or "")
    sys.stderr.write(result.stderr or "")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
