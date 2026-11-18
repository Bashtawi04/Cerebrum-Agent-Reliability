#!/usr/bin/env python3
"""Let an agent written for an Azure-style OpenAI endpoint talk to a local Ollama model, for free.

The agents in this course call  <endpoint>/openai/v1/chat/completions  (the Azure layout). Ollama serves the same API
at /v1/chat/completions. This tiny proxy listens on one port, rewrites the path, and forwards the request to Ollama.

    python3 tools/local_model_proxy.py --model qwen2.5:7b            # then put in your .env:
        AZURE_OPENAI_ENDPOINT=http://127.0.0.1:8099
        AZURE_OPENAI_API_KEY=local
        AZURE_OPENAI_DEPLOYMENT=qwen2.5:7b

Standard library only. It never leaves your machine.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DROP = {"parallel_tool_calls"}   # parameters some local servers refuse; the agents here do not need them


def make_handler(ollama, model):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            path = self.path
            for prefix in ("/openai/v1/", "/v1/"):
                if path.startswith(prefix):
                    path = path[len(prefix) - 1:]
                    break
            try:
                body = json.loads(raw)
                for k in DROP:
                    body.pop(k, None)
                if model:
                    body["model"] = model
                req = urllib.request.Request(f"{ollama}/v1{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=900) as r:
                    self._send(r.status, r.read())
            except urllib.error.HTTPError as e:
                self._send(e.code, e.read())
            except Exception as e:  # noqa: BLE001
                self._send(502, json.dumps({"error": {"message": f"proxy error: {e}"}}).encode())

    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="always use this Ollama model, whatever name the agent asks for")
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--ollama", default="http://127.0.0.1:11434")
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.ollama, a.model))
    print(f"proxy on http://127.0.0.1:{a.port} -> {a.ollama} (model: {a.model or 'as asked'})", file=sys.stderr)
    srv.serve_forever()


if __name__ == "__main__":
    main()
