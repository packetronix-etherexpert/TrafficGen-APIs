"""Shared fixtures.

Offline tests use ``fake`` - a requests transport adapter that records requests and returns
canned responses, so they need neither hardware nor a network. Live tests use the
``live_client`` fixture, which skips unless TRAFFICGEN_BASE_URL is set (and signs in when
TRAFFICGEN_USER / TRAFFICGEN_PASS are set).
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
        self.routes = {}           # (METHOD, path-after-host) -> (status, body, headers) or a list of those
        self.jar = None            # cookie jar of the session this adapter is mounted on

    def mount_on(self, session):
        """Mount on ``session`` and let it keep the cookies this fake 'server' sets (a real
        connection does that through urllib3; the fake has to do it by hand)."""
        session.mount("http://", self)
        self.jar = session.cookies
        return session

    def add_sequence(self, method, path, responses):
        """Answer successive requests to the same route with successive (status, body) pairs."""
        self.routes[(method.upper(), path)] = [(st, body, {}) for st, body in responses]

    def add(self, method, path, body=None, status=200, headers=None):
        self.routes[(method.upper(), path)] = (status, body, headers or {})

    def send(self, request, **kwargs):
        path = request.path_url
        body = json.loads(request.body) if request.body and "json" in request.headers.get("Content-Type", "") else request.body
        self.calls.append({"method": request.method, "url": request.url, "path": path, "json": body,
                           "headers": dict(request.headers)})
        route = self.routes.get((request.method, path), (404, {"detail": "no such route"}, {}))
        status, payload, headers = route.pop(0) if isinstance(route, list) else route
        if self.jar is not None and "Set-Cookie" in headers:
            name, _, value = headers["Set-Cookie"].split(";")[0].partition("=")
            self.jar.set(name, value)
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
    return TrafficGenClient("http://tg.test:9102", session=fake.mount_on(requests.Session()))


@pytest.fixture(scope="session")
def live_client():
    url = os.environ.get("TRAFFICGEN_BASE_URL")
    if not url:
        pytest.skip("TRAFFICGEN_BASE_URL not set - skipping live tests")
    tg = TrafficGenClient(url, verify_tls=os.environ.get("TRAFFICGEN_VERIFY_TLS", "1") != "0")
    if os.environ.get("TRAFFICGEN_USER"):                   # needed only when the appliance requires login
        tg.login(os.environ["TRAFFICGEN_USER"], os.environ.get("TRAFFICGEN_PASS", ""))
    yield tg
    tg.logout()


@pytest.fixture(scope="session")
def live_port(live_client):
    """First port number the appliance reports (ports are numbered from 1 - never assume 0)."""
    ports = live_client.list_ports()
    if not ports:
        pytest.skip("appliance reports no ports")
    return ports[0]["PortNo"]
