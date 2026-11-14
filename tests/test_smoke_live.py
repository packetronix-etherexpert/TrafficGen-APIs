"""Read-only smoke tests against a real appliance. Skipped unless TRAFFICGEN_BASE_URL is set."""


def test_api_is_up(live_client):
    assert "OK" in live_client.help()["message"]


def test_system_info(live_client):
    info = live_client.system_info()
    assert "version" in info


def test_ports_listed(live_client):
    ports = live_client.list_ports()
    assert isinstance(ports, list) and ports


def test_line_rate_readable(live_client, live_port):
    assert "LineRate" in live_client.get_line_rate(live_port)


def test_streams_listed(live_client, live_port):
    assert isinstance(live_client.list_streams(live_port), list)


def test_mac_stats_have_tx_and_rx(live_client, live_port):
    stats = live_client.port_mac_stats(live_port)
    assert "tx" in stats and "rx" in stats
