#!/usr/bin/env python3
"""Fetch the live OpenAPI schema from a running appliance and save it as openapi.json.

FastAPI generates the schema from the appliance's own routes and models, so it always matches
the real API. Run this after the API changes, then `python build_reference.py`.

Usage:
    python export_openapi.py --base-url http://10.0.0.5:9102 [--token pxtg_...]
"""
import argparse
import json
import os
import sys

import requests


# Descriptions in the appliance source that expose internal implementation notes; replaced in the
# published schema. (Fix the docstring at its source too, then this override can be deleted.)
DESCRIPTION_OVERRIDES = {
    ("get", "/stats/ports/{port_no}/mac"):
        "Get MAC-level Tx/Rx counters for a specific port, as {\"tx\": [...], \"rx\": [...]}. "
        "Preferred over /stats/ports/{port_no} for reading counters.",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default=os.environ.get("TRAFFICGEN_BASE_URL"), required=not os.environ.get("TRAFFICGEN_BASE_URL"))
    ap.add_argument("--token", default=os.environ.get("TRAFFICGEN_TOKEN"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "openapi.json"))
    a = ap.parse_args()
    headers = {"Authorization": f"Bearer {a.token}"} if a.token else {}
    r = requests.get(a.base_url.rstrip("/") + "/TGAPI/openapi.json", headers=headers, timeout=30)
    if not r.ok:
        sys.exit(f"HTTP {r.status_code} fetching schema: {r.text[:200]}")
    schema = r.json()
    # FastAPI's defaults ("FastAPI" / 0.1.0) say nothing useful - label the schema with the product and appliance version.
    try:
        version = requests.get(a.base_url.rstrip("/") + "/TGAPI/system/info", headers=headers, timeout=30).json().get("version", "")
    except (requests.RequestException, ValueError):
        version = ""
    schema["info"] = {"title": "Packetronix Traffic Generator API", "version": version or schema["info"].get("version", ""),
                      "description": "REST API of the Packetronix Traffic Generator appliance. Served under /TGAPI."}
    for (method, path), text in DESCRIPTION_OVERRIDES.items():
        if path in schema["paths"] and method in schema["paths"][path]:
            schema["paths"][path][method]["description"] = text
    with open(a.out, "w") as f:
        json.dump(schema, f, indent=2, sort_keys=False)
        f.write("\n")
    print(f"Wrote {a.out}: {len(schema['paths'])} paths")


if __name__ == "__main__":
    main()
