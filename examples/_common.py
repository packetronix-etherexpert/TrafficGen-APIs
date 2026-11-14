"""Shared setup for the examples: reads TRAFFICGEN_BASE_URL / TRAFFICGEN_TOKEN from the environment."""
import os
import sys

from trafficgen_sdk import TrafficGenClient


def connect() -> TrafficGenClient:
    url = os.environ.get("TRAFFICGEN_BASE_URL")
    if not url:
        sys.exit("Set TRAFFICGEN_BASE_URL, e.g. export TRAFFICGEN_BASE_URL=http://10.0.0.5:9102")
    tg = TrafficGenClient(url, token=os.environ.get("TRAFFICGEN_TOKEN"),
                          verify=os.environ.get("TRAFFICGEN_VERIFY_TLS", "1") != "0")
    if os.environ.get("TRAFFICGEN_USER"):
        tg.login(os.environ["TRAFFICGEN_USER"], os.environ.get("TRAFFICGEN_PASS", ""))
    return tg
