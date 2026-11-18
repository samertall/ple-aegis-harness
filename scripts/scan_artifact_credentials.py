"""Offline pre-publication scan for credential-shaped content in PLE artifacts.

This never prints matching contents or paths, does not modify artifact files,
does not make network requests, and is only a coarse guard (not proof of safety).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SECRET_RE = re.compile(
    rb"(?:AIza[A-Za-z0-9_-]{20,}|hf_[A-Za-z0-9]{24,}|sk-[A-Za-z0-9_-]{24,})"
)


def has_credential_pattern(root: Path) -> bool:
    if not root.is_dir():
        raise ValueError("Artifact directory missing")
    for file in root.rglob("*"):
        if file.is_symlink():
            raise ValueError("Symlink found inside artifacts: refusing publication")
        if not file.is_file():
            continue
        with file.open("rb") as source:
            overlap = b""
            while block := source.read(256 * 1024):
                if SECRET_RE.search(overlap + block):
                    return True
                overlap = block[-256:]
    return False


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: scan_artifact_credentials.py artifacts/")
        return 2
    try:
        unsafe = has_credential_pattern(Path(argv[0]))
    except (ValueError, OSError):
        print("ARTIFACT_SAFETY_UNVERIFIED: refusing export")
        return 2
    if unsafe:
        print("CREDENTIAL_PATTERN_DETECTED: refusing export; value and location withheld")
        return 1
    print("No common credential patterns detected. This is NOT a complete security review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
