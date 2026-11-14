# Packetronix Traffic Generator API - reference

Version 26.10.22.1. Base path: `/TGAPI` (for example `http://<appliance>:9102/TGAPI/ports`). Ports are numbered from 1. See [authentication](authentication.md) for tokens.

Generated from [`openapi/openapi.json`](openapi/openapi.json); an interactive view is in [`openapi/redoc.html`](openapi/redoc.html).

## System

| Method | Path | Body | Query | Description |
|---|---|---|---|---|
| GET | `/help` |  |  | Help |
| POST | `/system/hardware/close` |  |  | Close the hardware interface to allow firmware reloads. |
| POST | `/system/hardware/reinit` |  |  | Re-initialize the hardware interface after firmware reload. |
| GET | `/system/info` |  |  | Retrieve system information and status. |

## Ports

| Method | Path | Body | Query | Description |
|---|---|---|---|---|
| GET | `/ports` |  |  | Get configuration for all ports. |
| GET | `/ports/{port_no}` |  |  | Get configuration for a specific port. |
| PUT | `/ports/{port_no}` | `PortSettingsModel` |  | Update configuration for a specific port and apply to hardware. |
| POST | `/ports/{port_no}/arp` | `GatewayIPModel` |  | Send an ARP request to the Gateway IP on a specific port. |
| POST | `/ports/{port_no}/bert/enable` | `BertEnableModel` |  | Enable or disable RX BERT on a specific port. |
| POST | `/ports/{port_no}/bert/pattern` | `BertPatternModel` |  | Set the RX BERT pattern for a specific port. |
| GET | `/ports/{port_no}/line_rate` |  |  | Get line rate for a specific port. |
| PUT | `/ports/{port_no}/line_rate` |  | `rate_sel` | Set line rate for a specific port. rate_sel: 1=1G, 2=10G, 3=25G, 4=100G, 5=100G+FEC |
| GET | `/ports/{port_no}/link_status` |  |  | Get link status for a specific port. |
| POST | `/ports/{port_no}/ping` | `GatewayIPModel` |  | Send an ICMP Ping request to the Gateway IP on a specific port. |

## Streams

| Method | Path | Body | Query | Description |
|---|---|---|---|---|
| GET | `/streams` |  |  | Get all stream configurations. |
| GET | `/streams/{port_no}` |  |  | Get all streams associated with a specific port. |
| PUT | `/streams/{port_no}/{stream_no}` | `StreamSettingsModel` |  | Update a specific stream configuration and apply to hardware. |
| POST | `/streams/{port_no}/{stream_no}/error` | `ErrorActionModel` |  | Inject a single error of a specific type into a running stream. |
| POST | `/streams/{port_no}/{stream_no}/stop` |  |  | Stop traffic generation for a specific stream. |

## Statistics

| Method | Path | Body | Query | Description |
|---|---|---|---|---|
| GET | `/stats/ports` |  |  | Get port statistics for all ports simultaneously. |
| GET | `/stats/ports/{port_no}` |  |  | Get port statistics for a specific port. |
| GET | `/stats/ports/{port_no}/bert` |  |  | Get BERT statistics for a specific port. |
| GET | `/stats/ports/{port_no}/mac` |  |  | Get MAC-level Tx/Rx counters for a specific port, as {"tx": [...], "rx": [...]}. Preferred over /stats/ports/{port_no} for reading counters. |
| POST | `/stats/ports/{port_no}/reset` |  |  | Reset statistics for a specific port. |
| POST | `/stats/ports/{port_no}/streams/{stream_no}/reset` | `ResetStreamStatsModel` |  | Reset statistics for a specific stream on a port. |
| GET | `/stats/streams` |  |  | Get stream statistics for all ports simultaneously. |
| POST | `/stats/streams/batch` | `BatchStreamQueryModel` |  | Retrieve specific stream statistics in a single batch request. |
| GET | `/stats/streams/{port_no}` |  |  | Get stream statistics for a specific port. |

## Y.1564 service tests

| Method | Path | Body | Query | Description |
|---|---|---|---|---|
| GET | `/y1564/configs` |  |  | List saved test setups (newest first), same files the UI's Load Config menu shows. |
| POST | `/y1564/configs` | `Y1564SaveConfigModel` |  | Save a reusable named test setup, in the same format the UI's Save Config menu item writes, so it also shows up in the UI's Load Config list. |
| GET | `/y1564/configs/{filename}` |  |  | Retrieve a saved test setup's raw contents (config + services + selected_services). |
| GET | `/y1564/history` |  |  | List previously completed test result files, newest first, same list the UI's Test Report History dropdown shows. |
| GET | `/y1564/history/{filename}` |  |  | Retrieve a previously completed test's full result (same shape as GET /y1564/results). |
| POST | `/y1564/report` | `Y1564ReportRequestModel` |  | Generate and download the PDF report for the most recently completed test - identical output to the UI's Export PDF Report button. |
| GET | `/y1564/results` |  |  | The full structured result of the most recently completed test (config, per-step config_test/perf_test results, active_services, timing, port_statistics) - the same object the UI's Export PDF Report button reads from. |
| POST | `/y1564/start` | `Y1564StartModel` |  | Start a Y.1564 test run in the background. Provide either `config_name` (a setup already saved via POST /y1564/configs) or an inline `setup`. Poll GET /y1564/status for progress and GET /y1564/results once it completes. |
| GET | `/y1564/status` |  |  | Poll this periodically while a test is running for live status/progress/partial results. |
| POST | `/y1564/stop` |  |  | Gracefully stop the currently running Y.1564 test (same as the UI's Stop Test button). |

## Capture

| Method | Path | Body | Query | Description |
|---|---|---|---|---|
| GET | `/capture/filters` |  |  | Capture filter of every port, read back from the hardware (null: no rule on that port). |
| DELETE | `/capture/filters/{port_no}` |  |  | Remove the port's filter rule. With no rule the port's traffic is not delivered to the capture path. |
| GET | `/capture/filters/{port_no}` |  |  | Get Capture Filter |
| PUT | `/capture/filters/{port_no}` | `CaptureFilterModel` |  | Apply a filter to a port and return it as read back from the hardware. |
| GET | `/captures` |  |  | List Captures |
| POST | `/captures` | `CaptureStartModel` |  | Start a capture. Returns immediately with its capture_id; poll GET /captures/{id}. |
| DELETE | `/captures/{capture_id}` |  |  | Delete Capture |
| GET | `/captures/{capture_id}` |  |  | Get Capture |
| GET | `/captures/{capture_id}/analysis` |  | `loss?`, `length?`, `latency?` | The Capture tab's analyses as JSON; with none of the flags set, all three are returned. |
| POST | `/captures/{capture_id}/cancel` |  |  | Ask a running capture to finish early; what was captured so far is kept (state 'cancelled'). |
| GET | `/captures/{capture_id}/pcap` |  |  | Download Capture |

## Models

### BatchStreamQueryModel

| Field | Type | Required |
|---|---|---|
| `queries` | list[StreamQueryModel] | yes |

### BertEnableModel

| Field | Type | Required |
|---|---|---|
| `enable` | integer | yes |

### BertPatternModel

| Field | Type | Required |
|---|---|---|
| `pattern` | integer | yes |
| `UserPattern` | integer or null |  |

### CaptureFilterModel

| Field | Type | Required |
|---|---|---|
| `mac` | string (default ``) |  |
| `mac_filter` | string (default `promiscuous`) |  |
| `dst_ip` | string (default `0.0.0.0/0`) |  |
| `src_ip` | string (default `0.0.0.0/0`) |  |
| `port_range` | string (default `0-65535`) |  |
| `vlan_range` | string (default `disable`) |  |
| `ether_type` | string (default `disable`) |  |
| `protocol` | string (default `any`) |  |
| `errored` | string (default `Enable`) |  |

### CaptureStartModel

| Field | Type | Required |
|---|---|---|
| `duration_s` | integer (default `10`) |  |
| `max_packets` | integer (default `100000`) |  |
| `filters` | object or null |  |
| `restore_filters` | boolean (default `True`) |  |

### ErrorActionModel

| Field | Type | Required |
|---|---|---|
| `error_type` | string | yes |

### GatewayIPModel

| Field | Type | Required |
|---|---|---|
| `gateway_ip` | string | yes |

### PacketModifierModel

| Field | Type | Required |
|---|---|---|
| `Enable` | boolean or null |  |
| `Offset` | integer or null |  |
| `ModifierType` | string or null |  |
| `ModifierValueMin` | integer or null |  |
| `ModifierValueMax` | integer or null |  |
| `StepSize` | integer or null |  |
| `RepeatCount` | integer or null |  |
| `Mask` | string or null |  |

### PortSettingsModel

| Field | Type | Required |
|---|---|---|
| `PortNo` | integer or null |  |
| `PortMode` | string or null |  |
| `FlowControl` | boolean or null |  |
| `MulticastDrop` | boolean or null |  |
| `BroadcastDrop` | boolean or null |  |
| `LoopbackLayer` | string or null |  |
| `PIDType` | string or null |  |
| `TrafficMode` | string or null |  |
| `SeqRate` | number or null |  |
| `BurstPeriod` | integer or null |  |
| `LatencyMeas` | string or null |  |
| `MacAddress` | string or null |  |
| `IPAddress` | string or null |  |
| `SubnetMask` | string or null |  |
| `IMIX` | list[list[integer]] or string or null |  |

### ResetStreamStatsModel

| Field | Type | Required |
|---|---|---|
| `tx` | boolean (default `True`) |  |
| `rx` | boolean (default `True`) |  |

### StreamQueryModel

| Field | Type | Required |
|---|---|---|
| `port_no` | integer | yes |
| `stream_no` | integer | yes |

### StreamSettingsModel

| Field | Type | Required |
|---|---|---|
| `index` | integer or null |  |
| `PortNo` | integer or null |  |
| `StreamEnable` | boolean or null |  |
| `StreamNo` | integer or null |  |
| `PIDNo` | integer or null |  |
| `Rate` | number or null |  |
| `BurstSize` | integer or null |  |
| `BurstDensity` | number or null |  |
| `SequencePacket` | integer or null |  |
| `PacketCounts` | integer or null |  |
| `FrameLenType` | string or null |  |
| `FrameLenMin` | integer or null |  |
| `FrameLenMax` | integer or null |  |
| `EMixLen` | list[integer] or string or null |  |
| `PayloadType` | string or null |  |
| `PayloadData` | string or null |  |
| `Layers` | string or null |  |
| `MAC_DA` | string or null |  |
| `MAC_SA` | string or null |  |
| `IP_DA` | string or null |  |
| `IP_SA` | string or null |  |
| `Port_DA` | integer or null |  |
| `Port_SA` | integer or null |  |
| `HeaderLen` | integer or null (default `0`) |  |
| `RAW` | string or null |  |
| `NoOfModifiers` | integer or null |  |
| `ErrorType` | string or null |  |
| `ErrorAction` | boolean or null |  |
| `PacketModifier` | list[PacketModifierModel] or null |  |

### Y1564ReportRequestModel

| Field | Type | Required |
|---|---|---|
| `customer` | string or null |  |
| `operator` | string or null |  |
| `site` | string or null |  |
| `dut` | string or null |  |
| `comment` | string or null |  |
| `prefix` | string or null (default `Y1564_Report`) |  |

### Y1564SaveConfigModel

| Field | Type | Required |
|---|---|---|
| `config` | Y1564TestConfigModel | yes |
| `services` | list[object] | yes |
| `selected_services` | list[object] or null |  |
| `name` | string | yes |

### Y1564SetupModel

| Field | Type | Required |
|---|---|---|
| `config` | Y1564TestConfigModel | yes |
| `services` | list[object] | yes |
| `selected_services` | list[object] or null |  |

### Y1564StartModel

| Field | Type | Required |
|---|---|---|
| `config_name` | string or null |  |
| `setup` | Y1564SetupModel or null |  |

### Y1564TestConfigModel

| Field | Type | Required |
|---|---|---|
| `direction` | string | yes |
| `line_rate` | string | yes |
| `west_loc` | string (default `Local`) |  |
| `remote_ip` | string or null |  |
| `remote_port` | integer or null |  |
| `remote_hw_port` | integer or null |  |
| `max_flr` | number or null |  |
| `max_ftd` | number or null |  |
| `max_fdv` | number or null |  |
| `min_avail` | number or null |  |
| `ses_threshold` | number or null |  |
| `enable_config_test` | boolean (default `True`) |  |
| `step_duration` | number or null (default `10.0`) |  |
| `cir_steps` | list[number] or null |  |
| `test_eir` | boolean (default `False`) |  |
| `test_cbs` | boolean (default `False`) |  |
| `test_ebs` | boolean (default `False`) |  |
| `test_policing` | boolean (default `False`) |  |
| `policing_m_factor` | number or null (default `25.0`) |  |
| `enable_perf_test` | boolean (default `True`) |  |
| `perf_duration_preset` | string or null (default `15 Seconds`) |  |
| `perf_duration_custom` | string or null |  |
