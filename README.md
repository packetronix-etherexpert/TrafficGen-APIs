# Traffic Generator APIs

[![CI](https://github.com/packetronix-etherexpert/TrafficGen-APIs/actions/workflows/ci.yml/badge.svg)](https://github.com/packetronix-etherexpert/TrafficGen-APIs/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

REST API reference, Python SDK and automation examples for the **Packetronix Traffic Generator** - an
FPGA-based Ethernet traffic generator and analyzer. Drive it from your own test automation, CI/CD
pipelines or scripts: the same controls as the appliance's web UI, exposed over REST.

See also [WAN-Emulator-APIs](https://github.com/packetronix-etherexpert/WAN-Emulator-APIs) for the
Packetronix WAN-Emulator.

## What's here

| Directory | Description |
|---|---|
| [`docs/`](docs/api-reference.md) | REST API reference, OpenAPI schema and [authentication guide](docs/authentication.md) |
| [`sdk/`](sdk/) | `trafficgen-sdk` - Python client library |
| [`examples/`](examples/) | Runnable scripts: stream setup, statistics, capture, Y.1564, snappi (OTG) |
| [`tests/`](tests/) | pytest suite (offline unit tests + live smoke tests) |
| [`robot/`](robot/) | Robot Framework keyword library and example suite |

Pipeline examples: GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)),
GitLab CI ([`.gitlab-ci.yml`](.gitlab-ci.yml)) and Jenkins ([`Jenkinsfile`](Jenkinsfile)).

## Requirements

- Python 3.10+
- Network access to a Traffic Generator appliance (REST API on port 9102 by default)
- An API token, if the appliance requires authentication - see [authentication](docs/authentication.md)

## Install

```bash
git clone https://github.com/packetronix-etherexpert/TrafficGen-APIs.git
cd TrafficGen-APIs
pip install -e sdk/
```

## Quick start

```python
from trafficgen_sdk import TrafficGenClient

tg = TrafficGenClient("http://10.0.0.5:9102", token="pxtg_...")   # omit token if the API is open

print(tg.system_info())
print(tg.get_line_rate(1))                        # ports are numbered from 1

tg.update_stream(1, 1, FrameLenMin=512, FrameLenMax=512, Rate=10)
tg.update_stream(1, 1, StreamEnable=True)         # start traffic on port 1, stream 1
print(tg.port_mac_stats(1))
tg.stop_stream(1, 1)
```

Or with plain HTTP:

```bash
curl -H "Authorization: Bearer $TRAFFICGEN_TOKEN" http://10.0.0.5:9102/TGAPI/ports
```

## Documentation

- [API reference](docs/api-reference.md) - endpoints grouped by System, Ports, Streams, Statistics,
  Y.1564 and Capture, plus every request model
- [Interactive reference](docs/openapi/redoc.html) and the [OpenAPI schema](docs/openapi/openapi.json)
  (also published on GitHub Pages)
- [SDK reference](sdk/README.md)
- [Authentication](docs/authentication.md)

## Testing against your appliance

The unit tests mock all HTTP calls and need no hardware. To also run the live smoke tests and the
Robot Framework suite (both read-only) against a real appliance:

```bash
export TRAFFICGEN_BASE_URL=http://10.0.0.5:9102
export TRAFFICGEN_TOKEN=pxtg_...        # only if authentication is enabled

pip install -r tests/requirements.txt -r robot/requirements.txt
pytest tests/
robot robot/example.robot
```

Without `TRAFFICGEN_BASE_URL` the live tests are skipped - which is also how the CI pipelines behave by
default. To enable them in CI, set `TRAFFICGEN_BASE_URL` (variable) and `TRAFFICGEN_TOKEN` (secret).

## Refreshing the API reference

The reference is generated from the appliance's own OpenAPI schema, so it cannot drift from the code:

```bash
python docs/openapi/export_openapi.py --base-url http://10.0.0.5:9102
python docs/openapi/build_reference.py
```

## Scope

Covers the `/TGAPI` REST endpoints of the Traffic Generator. The Open Traffic Generator (OTG/snappi)
endpoints are optional and appear only on appliances started with `ENABLE_OTG=1`
([example](examples/05_snappi_otg.py)).

## Support

Questions, bug reports and feature requests: please [open an issue](https://github.com/packetronix-etherexpert/TrafficGen-APIs/issues).

## License

MIT - see [LICENSE](LICENSE).
