# trafficgen-sdk

Python client for the Packetronix Traffic Generator REST API. Requires Python 3.10+ and `requests`.

```bash
pip install -e sdk/          # from a clone of this repository
```

## Usage

```python
from trafficgen_sdk import TrafficGenClient, TrafficGenError

tg = TrafficGenClient("http://10.0.0.5:9102", token="pxtg_...")   # token only if the appliance requires one

print(tg.system_info())
print(tg.get_line_rate(1))                    # ports are numbered from 1

tg.update_stream(1, 1, FrameLenMin=512, FrameLenMax=512, Rate=10)   # read-modify-write
tg.update_stream(1, 1, StreamEnable=True)     # start traffic
print(tg.port_mac_stats(1))
tg.stop_stream(1, 1)

try:
    tg.get_port(99)
except TrafficGenError as e:
    print(e.status_code, e.detail)            # 404 Port not found
```

Every method raises `TrafficGenError` (with `status_code` and the server's `detail`) on an HTTP error
or connection failure - it never returns an error dictionary.

## Method overview

| Area | Methods |
|---|---|
| System | `help`, `system_info`, `hardware_close`, `hardware_reinit` |
| Ports | `list_ports`, `get_port`, `set_port`, `update_port`, `get_link_status`, `get_line_rate`, `set_line_rate`, `arp`, `ping` |
| Streams | `list_streams`, `get_stream`, `set_stream`, `update_stream`, `stop_stream`, `inject_error` |
| Statistics | `port_stats`, `port_mac_stats`, `stream_stats`, `stream_stats_batch`, `reset_port_stats`, `reset_stream_stats` |
| BERT | `set_bert_pattern`, `enable_bert`, `bert_stats` |
| Y.1564 | `y1564_list_configs`, `y1564_get_config`, `y1564_save_config`, `y1564_start`, `y1564_stop`, `y1564_status`, `y1564_results`, `y1564_report`, `y1564_history`, `y1564_get_history` |
| Capture | `get_capture_filters`, `get_capture_filter`, `set_capture_filter`, `delete_capture_filter`, `start_capture`, `list_captures`, `get_capture`, `cancel_capture`, `delete_capture`, `download_pcap`, `capture_analysis` |

`set_port` / `set_stream` replace the whole settings object; `update_port` / `update_stream` read the
current settings first and change only the fields you pass. Field names and types are in the
[API reference](../docs/api-reference.md) (`PortSettingsModel`, `StreamSettingsModel`, ...).

Authentication: see [docs/authentication.md](../docs/authentication.md).
