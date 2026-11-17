"""Non-inference Gemini API key/model check.

Only GETs public model metadata using an authorized key; never submits PLE
datasets, prompts, or generation requests. It CANNOT prove billing tier.
"""
from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "gemini-3.8-flash"
MODEL_URL = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL


def check_model_metadata(key: str) -> str:
    if not key or "\n" in key or "\r" in key:
        raise ValueError("A single-line Gemini API key is required")
    # Never place credentials in a URL, printed arguments or logger output.
    request = Request(
        MODEL_URL,
        headers={"x-goog-api-key": key, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise RuntimeError(f"Model metadata endpoint returned HTTP {response.status}")
            payload = json.loads(response.read(512_000))
    except HTTPError as error:
        # Do not print or parse response bodies, which may contain sensitive values.
        raise RuntimeError(f"Model metadata HTTP {error.code}") from None
    except URLError:
        raise RuntimeError("Unable to reach Gemini API metadata endpoint") from None
    except (ValueError, TypeError):
        raise RuntimeError("Invalid Gemini model metadata response") from None
    name = payload.get("name") if isinstance(payload, dict) else None
    if name != "models/" + MODEL:
        raise RuntimeError("Key authenticated, but expected Gemini model was not returned")
    return name


def main() -> int:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        print("SKIPPED: GEMINI_API_KEY is not configured. No request made.")
        return 2
    try:
        name = check_model_metadata(key)
    except (ValueError, RuntimeError) as error:
        # Error messages contain no key, URLs with key, prompts or response body.
        print(f"MODEL_METADATA_CHECK_FAILED: {error}")
        return 1
    print(f"KEY_METADATA_OK: {name}; no prompts or inference submitted.")
    print("Billing/Free Tier status is NOT verified by this endpoint.")
    print("This is NOT a PLE benchmark evaluation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
