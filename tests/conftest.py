"""Shared fixtures.

Offline tests use ``fake`` - a requests transport adapter that records requests and returns
canned responses, so they need neither hardware nor a network. Live tests use the
``live_client`` fixture, which skips unless TRAFFICGEN_BASE_URL is set.
"""
import io
import json
import os

import pytest
import requests
from requests.adapters import BaseAdapter

from trafficgen_sdk import TrafficGenClient


class FakeAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.calls = []            # (method, url, json_body)
        self.routes = {}           # (METHOD, path-after-host) -> (status, body, headers)

    def add(self, method, path, body=None, status=200, headers=None):
        self.routes[(method.upper(), path)] = (status, body, headers or {})

    def send(self, request, **kwargs):
        path = request.path_url
        body = json.loads(request.body) if request.body and "json" in request.headers.get("Content-Type", "") else request.body
        self.calls.append({"method": request.method, "url": request.url, "path": path, "json": body,
                           "headers": dict(request.headers)})
        status, payload, headers = self.routes.get((request.method, path), (404, {"detail": "no such route"}, {}))
        resp = requests.Response()
        resp.status_code = status
        resp.url = request.url
        resp.headers.update(headers)
        if isinstance(payload, (bytes, bytearray)):
            resp._content = bytes(payload)
        elif payload is not None:
            resp._content = json.dumps(payload).encode()
            resp.headers.setdefault("Content-Type", "application/json")
        else:
            resp._content = b""
        resp.request = request
        resp.raw = io.BytesIO(resp._content)     # lets stream=True / iter_content work
        return resp

    def close(self):
        pass


@pytest.fixture
def fake():
    return FakeAdapter()


@pytest.fixture
def client(fake):
    session = requests.Session()
    session.mount("http://", fake)
    return TrafficGenClient("http://tg.test:9102", session=session)


@pytest.fixture(scope="session")
def live_client():
    url = os.environ.get("TRAFFICGEN_BASE_URL")
    if not url:
        pytest.skip("TRAFFICGEN_BASE_URL not set - skipping live tests")
    tg = TrafficGenClient(url, token=os.environ.get("TRAFFICGEN_TOKEN"),
                          verify=os.environ.get("TRAFFICGEN_VERIFY_TLS", "1") != "0")
    if os.environ.get("TRAFFICGEN_USER"):
        tg.login(os.environ["TRAFFICGEN_USER"], os.environ.get("TRAFFICGEN_PASS", ""))
    return tg


@pytest.fixture(scope="session")
def live_port(live_client):
    """First port number the appliance reports (ports are numbered from 1 - never assume 0)."""
    ports = live_client.list_ports()
    if not ports:
        pytest.skip("appliance reports no ports")
    return ports[0]["PortNo"]
