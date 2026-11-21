"""Optional Ollama client for locally served models."""

import json
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler
from urllib.parse import urlsplit


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class LocalModel:
    def __init__(self, model, endpoint="http://127.0.0.1:11434"):
        parsed = urlsplit(endpoint)
        if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "::1"):
            raise ValueError("use an HTTP endpoint on a literal loopback address")
        if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
            raise ValueError("endpoint must contain only host and port")
        if not model.strip():
            raise ValueError("model name is required")
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.calls = 0

    def complete(self, prompt):
        request = Request(self.endpoint + "/api/chat", data=json.dumps({
            "model": self.model, "stream": False, "format": "json",
            "messages": [{"role": "user", "content": prompt}],
            "options": {"temperature": 0, "num_predict": 512},
        }).encode(), headers={"Content-Type": "application/json"})
        self.calls += 1
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(request, timeout=60) as response:
            payload = json.load(response)
        if payload.get("done") is not True:
            raise ValueError("model response is incomplete")
        return json.loads(payload["message"]["content"])
