"""No inference or secrets in logs during Gemini metadata preflight."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_gemini_metadata as m


class Reply:
    status = 200
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self, limit):
        return json.dumps({"name": "models/gemini-3.8-flash"}).encode()


def test_metadata_check_is_get_and_never_exposes_key():
    token = "SECRET_SHOULD_NEVER_BE_PRINTED_123456"
    def verify(req, timeout):
        assert req.get_method() == "GET"
        assert req.full_url == m.MODEL_URL
        assert req.get_header("X-goog-api-key") == token
        assert "SECRET" not in req.full_url
        assert timeout == 20
        return Reply()
    with patch.object(m, "urlopen", verify):
        assert m.check_model_metadata(token) == "models/gemini-3.8-flash"


def test_no_key_skips_without_network(monkeypatch, capsys):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch.object(m, "urlopen") as api:
        assert m.main() == 2
    api.assert_not_called()
    assert "SKIPPED" in capsys.readouterr().out


def test_key_not_disclosed_in_http_error(monkeypatch, capsys):
    from urllib.error import HTTPError
    monkeypatch.setenv("GEMINI_API_KEY", "A_SECRET_WITH_UNIQUE_IDENTIFIER")
    def fail(*args, **kwargs):
        raise HTTPError("https://example.invalid", 403, "denied", {}, None)
    with patch.object(m, "urlopen", fail):
        assert m.main() == 1
    out = capsys.readouterr().out
    assert "403" in out
    assert "A_SECRET_WITH_UNIQUE_IDENTIFIER" not in out


def test_wrong_model_is_rejected():
    class Wrong(Reply):
        def read(self, limit):
            return json.dumps({"name": "models/gemini-2.5-flash"}).encode()
    with patch.object(m, "urlopen", lambda req, timeout: Wrong()):
        with pytest.raises(RuntimeError, match="expected Gemini model"):
            m.check_model_metadata("ANONYMOUS_TEST_SECRET")


def test_newline_in_key_rejected():
    with pytest.raises(ValueError, match="single-line"):
        m.check_model_metadata("abc\nx")
