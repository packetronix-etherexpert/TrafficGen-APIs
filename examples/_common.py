"""Shared setup for the examples.

Environment: TRAFFICGEN_BASE_URL (required), TRAFFICGEN_USER / TRAFFICGEN_PASS (needed when the
appliance requires login), TRAFFICGEN_VERIFY_TLS=0 (self-signed certificate).
"""
import os
import sys

from trafficgen_sdk import TrafficGenClient


def connect() -> TrafficGenClient:
    url = os.environ.get("TRAFFICGEN_BASE_URL")
    if not url:
        sys.exit("Set TRAFFICGEN_BASE_URL, e.g. export TRAFFICGEN_BASE_URL=https://10.0.0.5")
    tg = TrafficGenClient(url, verify_tls=os.environ.get("TRAFFICGEN_VERIFY_TLS", "1") != "0")
    if os.environ.get("TRAFFICGEN_USER"):
        tg.login(os.environ["TRAFFICGEN_USER"], os.environ.get("TRAFFICGEN_PASS", ""))
    return tg
