"""OFFLINE PLE protocol simulator — not a real engineering model.

Supports ONLY the official kit's connection probe, hello.txt smoke and
secret_word MCP checks. Never generates real dev-set artifacts or calls APIs.
"""
from __future__ import annotations
import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL = "gemini-3.8-flash"
TOKEN = "local-offline-protocol-test-only"

def make_call(name, args):
    return {"id": "call_offline_" + name, "type": "function",
            "function": {"name": name, "arguments": json.dumps(args)}}

def has_called(messages, name, path=None):
    for m in messages:
        if m.get("role") != "assistant": continue
        for c in m.get("tool_calls") or []:
            fn = c.get("function") or {}
            if fn.get("name") != name: continue
            if path is None: return True
            try: a = json.loads(fn.get("arguments") or "{}")
            except (ValueError, TypeError): continue
            if a.get("path") == path: return True
    return False

def simulated_response(req):
    messages = req.get("messages") or []
    user = "\n".join(str(m.get("content") or "") for m in messages if m.get("role") == "user")
    outputs = "\n".join(str(m.get("content") or "") for m in messages if m.get("role") == "tool")
    content, calls = "", None
    if "Reply with the word OK" in user:
        content = "OK"
    elif "hello.txt" in user and "HELLO" in user:
        if has_called(messages, "write_file", "/app/hello.txt"):
            content = "done"
        else:
            calls = [make_call("write_file", {"path": "/app/hello.txt", "content": "HELLO\n"})]
    elif "secret_word" in user and "mcp.txt" in user:
        if has_called(messages, "write_file", "/app/mcp.txt"):
            content = "done"
        else:
            found = re.search(r"MCP-[A-F0-9]{8}", outputs)
            if found:
                calls = [make_call("write_file", {"path": "/app/mcp.txt", "content": found.group(0)})]
            elif has_called(messages, "mcp_search"):
                calls = [make_call("mcp_call", {"server": "apps", "tool": "secret_word", "arguments": {}})]
            else:
                calls = [make_call("mcp_search", {"server": "apps", "query": "secret_word"})]
    else:
        raise ValueError("Only official PLE probe, hello.txt smoke and secret_word MCP tests are supported")
    msg = {"role": "assistant", "content": content}
    if calls: msg["tool_calls"] = calls
    return {"id": "chatcmpl_offline_test", "object": "chat.completion",
            "created": int(time.time()), "model": MODEL,
            "choices": [{"index": 0, "message": msg, "finish_reason": "tool_calls" if calls else "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/chat/completions" or self.headers.get("Authorization") != "Bearer " + TOKEN:
            return self.reply(403, {"error": "offline protocol fixture only"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= 2_000_000:
                return self.reply(413, {"error": "request size rejected"})
            req = json.loads(self.rfile.read(size))
            if req.get("model") != MODEL:
                return self.reply(422, {"error": "wrong fixture model"})
            self.reply(200, simulated_response(req))
        except (ValueError, KeyError, TypeError):
            self.reply(422, {"error": "unsupported non-protocol fixture request"})

    def reply(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args): pass

if __name__ == "__main__":
    port = int(os.environ.get("PLE_OFFLINE_MOCK_PORT", "48711"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
