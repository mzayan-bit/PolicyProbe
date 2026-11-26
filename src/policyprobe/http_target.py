"""Client for disposable staging sessions over HTTP."""

import json
from contextlib import contextmanager
from http.client import HTTPException
from urllib.error import URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from .conversation import TargetError


class HttpTarget:
    def __init__(self, base_url, timeout=5.0):
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = Request(self.base_url + path, data=data, method=method,
                      headers={"Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=self.timeout) as response:
                if method == "DELETE":
                    return
                payload = json.load(response)
                if not isinstance(payload, dict):
                    raise ValueError("expected a JSON object")
                return payload
        except (URLError, OSError, HTTPException, ValueError) as exc:
            raise TargetError(f"{method} {path}: {exc}") from exc

    @contextmanager
    def open(self, order):
        path = "/sessions/" + uuid4().hex
        try:
            self.request("PUT", path, {
                "order_id": order.order_id,
                "purchased_on": order.purchased_on.isoformat(),
                "requested_on": order.requested_on.isoformat(),
            })
            yield _HttpSession(self, path)
        except BaseException as original:
            try:
                self.request("DELETE", path)
            except TargetError as cleanup:
                if isinstance(original, TargetError):
                    raise TargetError(f"{original}; cleanup also failed: {cleanup}") from original
                original.add_note(f"Session cleanup failed: {cleanup}")
            raise
        else:
            self.request("DELETE", path)


class _HttpSession:
    def __init__(self, target, path):
        self.target = target
        self.path = path

    def refunded(self):
        value = self.target.request("GET", self.path + "/order").get("refunded")
        if type(value) is not bool:
            raise TargetError("expected a boolean refunded field in the order record")
        return value

    def send(self, message):
        value = self.target.request("POST", self.path + "/messages", {"message": message}).get("reply")
        if not isinstance(value, str):
            raise TargetError("expected a text reply from the staging bot")
        return value
