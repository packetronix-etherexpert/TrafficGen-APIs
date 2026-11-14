"""Offline unit tests: verify the exact HTTP requests the SDK sends."""
import pytest
import requests

from trafficgen_sdk import TrafficGenClient, TrafficGenError


def test_base_url_forms():
    for u in ("http://h:9102", "http://h:9102/", "http://h:9102/TGAPI", "http://h:9102/TGAPI/"):
        assert TrafficGenClient(u).api_url == "http://h:9102/TGAPI"


def test_bearer_token_sent(fake):
    s = requests.Session(); s.mount("http://", fake)
    fake.add("GET", "/TGAPI/help", {"message": "ok"})
    TrafficGenClient("http://h", token="pxtg_abc_def", session=s).help()
    assert fake.calls[0]["headers"]["Authorization"] == "Bearer pxtg_abc_def"


def test_no_auth_header_without_token(client, fake):
    fake.add("GET", "/TGAPI/help", {"message": "ok"})
    client.help()
    assert "Authorization" not in fake.calls[0]["headers"]


def test_http_error_carries_status_and_detail(client, fake):
    fake.add("GET", "/TGAPI/ports/9", {"detail": "Port 9 not found"}, status=404)
    with pytest.raises(TrafficGenError) as e:
        client.get_port(9)
    assert e.value.status_code == 404 and e.value.detail == "Port 9 not found"


def test_unauthenticated_error(client, fake):
    fake.add("GET", "/TGAPI/ports", {"detail": "Authentication required"}, status=401)
    with pytest.raises(TrafficGenError) as e:
        client.list_ports()
    assert e.value.status_code == 401


def test_update_port_merges_current_settings(client, fake):
    fake.add("GET", "/TGAPI/ports/1", {"PortNo": 1, "FlowControl": True, "IPAddress": "10.0.0.1"})
    fake.add("PUT", "/TGAPI/ports/1", {"ok": True})
    client.update_port(1, IPAddress="10.0.0.9")
    put = fake.calls[-1]
    assert put["method"] == "PUT" and put["json"] == {"PortNo": 1, "FlowControl": True, "IPAddress": "10.0.0.9"}


def test_update_stream_merges_and_enables(client, fake):
    fake.add("GET", "/TGAPI/streams/1", [{"StreamNo": 1, "StreamEnable": False, "Rate": 10}, {"StreamNo": 2}])
    fake.add("PUT", "/TGAPI/streams/1/1", {"ok": True})
    client.update_stream(1, 1, StreamEnable=True)
    assert fake.calls[-1]["json"] == {"StreamNo": 1, "StreamEnable": True, "Rate": 10}


def test_get_stream_missing_raises(client, fake):
    fake.add("GET", "/TGAPI/streams/1", [{"StreamNo": 2}])
    with pytest.raises(TrafficGenError):
        client.get_stream(1, 1)


def test_line_rate_uses_query_param(client, fake):
    fake.add("PUT", "/TGAPI/ports/0/line_rate?rate_sel=3", {"ok": True})
    client.set_line_rate(0, 3)
    assert fake.calls[0]["path"] == "/TGAPI/ports/0/line_rate?rate_sel=3"


def test_stream_stats_batch_body(client, fake):
    fake.add("POST", "/TGAPI/stats/streams/batch", {})
    client.stream_stats_batch([(1, 1), (2, 3)])
    assert fake.calls[0]["json"] == {"queries": [{"port_no": 1, "stream_no": 1}, {"port_no": 2, "stream_no": 3}]}


def test_reset_stream_stats_flags(client, fake):
    fake.add("POST", "/TGAPI/stats/ports/1/streams/2/reset", {})
    client.reset_stream_stats(1, 2, tx=False)
    assert fake.calls[0]["json"] == {"tx": False, "rx": True}


def test_bert_requests(client, fake):
    fake.add("POST", "/TGAPI/ports/1/bert/pattern", {})
    fake.add("POST", "/TGAPI/ports/1/bert/enable", {})
    client.set_bert_pattern(1, 0, user_pattern=0xDEADBEEF)
    client.enable_bert(1, True)
    assert fake.calls[0]["json"] == {"pattern": 0, "UserPattern": 0xDEADBEEF}
    assert fake.calls[1]["json"] == {"enable": 1}


def test_y1564_start_requires_exactly_one_source(client):
    with pytest.raises(ValueError):
        client.y1564_start()
    with pytest.raises(ValueError):
        client.y1564_start(config_name="a", setup={})


def test_y1564_start_by_saved_config(client, fake):
    fake.add("POST", "/TGAPI/y1564/start", {"started": True})
    client.y1564_start(config_name="lab.json")
    assert fake.calls[0]["json"] == {"config_name": "lab.json"}


def test_capture_analysis_flags(client, fake):
    fake.add("GET", "/TGAPI/captures/c1/analysis?loss=True&latency=True", {})
    client.capture_analysis("c1", loss=True, latency=True)
    assert "loss=True" in fake.calls[0]["path"] and "length" not in fake.calls[0]["path"]


def test_download_pcap_writes_file(client, fake, tmp_path):
    fake.add("GET", "/TGAPI/captures/c1/pcap", b"\xd4\xc3\xb2\xa1PCAPDATA", headers={"Content-Type": "application/vnd.tcpdump.pcap"})
    out = client.download_pcap("c1", str(tmp_path / "c.pcap"))
    assert open(out, "rb").read() == b"\xd4\xc3\xb2\xa1PCAPDATA"


def test_login_success_and_failure(fake):
    s = requests.Session(); s.mount("http://", fake)
    fake.add("POST", "/login", None, status=303, headers={"Location": "/"})
    TrafficGenClient("http://h:9102", session=s).login("admin", "pw")
    assert fake.calls[0]["url"] == "http://h:9102/login"
    fake.add("POST", "/login", None, status=401)
    with pytest.raises(TrafficGenError):
        TrafficGenClient("http://h:9102", session=s).login("admin", "bad")
