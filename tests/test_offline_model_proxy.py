"""Tests for the deterministic OFFLINE protocol fixture; NOT benchmark tests."""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from mock_model_proxy import simulated_response

def request(task):
    return {"model": "claude-opus-5-5", "messages": [{"role": "user", "content": task}]}

def called(reply):
    return reply["choices"][0]["message"].get("tool_calls", [])

def test_probe():
    assert simulated_response(request("Reply with the word OK."))["choices"][0]["message"]["content"] == "OK"

def test_smoke_write_then_finish():
    data = request("Create hello.txt in /app whose entire content is HELLO")
    fn = called(simulated_response(data))[0]["function"]
    assert fn["name"] == "write_file"
    assert json.loads(fn["arguments"]) == {"path": "/app/hello.txt", "content": "HELLO\n"}
    data["messages"].append({"role": "assistant", "tool_calls": [{"function": fn}]})
    assert simulated_response(data)["choices"][0]["message"]["content"] == "done"

def test_mcp_search_call_and_dynamic_word():
    data = request("Call MCP server apps secret_word and write /app/mcp.txt")
    first = called(simulated_response(data))[0]["function"]
    assert first["name"] == "mcp_search"
    data["messages"] += [{"role": "assistant", "tool_calls": [{"function": first}]},
                         {"role": "tool", "content": '{"matches":[{"name":"secret_word"}]}'}]
    second = called(simulated_response(data))[0]["function"]
    assert second["name"] == "mcp_call"
    data["messages"] += [{"role": "assistant", "tool_calls": [{"function": second}]},
                         {"role": "tool", "content": '{"content":[{"type":"text","text":"MCP-ABCDEF12"}]}'}]
    third = called(simulated_response(data))[0]["function"]
    assert third["name"] == "write_file"
    assert json.loads(third["arguments"]) == {"path": "/app/mcp.txt", "content": "MCP-ABCDEF12"}
    data["messages"].append({"role": "assistant", "tool_calls": [{"function": third}]})
    assert simulated_response(data)["choices"][0]["message"]["content"] == "done"

def test_engineering_task_rejected():
    with pytest.raises(ValueError, match="Only official PLE"):
        simulated_response(request("Design a footing and compute structural loads"))
