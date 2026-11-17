"""Test mock for offline environments without the runtime SDK installed.

Production always installs the actual openai SDK from requirements.txt.
"""
import importlib.util
import sys
import types

if importlib.util.find_spec('openai') is None:
    sdk = types.ModuleType('openai')
    class APIError(Exception): pass
    sdk.APIError = APIError
    def unavailable(*a, **kw):
        raise RuntimeError('OpenAI SDK not installed (mock tests only)')
    sdk.AsyncOpenAI = unavailable
    sys.modules['openai'] = sdk
