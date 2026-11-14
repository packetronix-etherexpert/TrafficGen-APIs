"""Robot Framework keyword library over trafficgen_sdk.TrafficGenClient.

Each public method becomes a keyword (underscores become spaces). See example.robot.
"""
from trafficgen_sdk import TrafficGenClient


class TrafficGenLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self._tg = None

    def connect_to_traffic_generator(self, base_url, token=None, username=None, password=None, verify_tls=True):
        """Open a connection. Use ``token`` (API token) or ``username``/``password`` (web-UI login)."""
        self._tg = TrafficGenClient(base_url, token=token or None, verify=str(verify_tls).lower() != "false")
        if username:
            self._tg.login(username, password or "")

    def get_system_info(self):
        return self._tg.system_info()

    def get_ports(self):
        return self._tg.list_ports()

    def get_line_rate(self, port):
        return self._tg.get_line_rate(int(port))["LineRate"]

    def get_streams(self, port):
        return self._tg.list_streams(int(port))

    def update_stream(self, port, stream, **fields):
        return self._tg.update_stream(int(port), int(stream), **fields)

    def start_stream(self, port, stream):
        return self._tg.update_stream(int(port), int(stream), StreamEnable=True)

    def stop_stream(self, port, stream):
        return self._tg.stop_stream(int(port), int(stream))

    def get_mac_counters(self, port):
        """Return ``{'tx': [...], 'rx': [...]}`` MAC-level counters for a port."""
        return self._tg.port_mac_stats(int(port))

    def reset_port_statistics(self, port):
        return self._tg.reset_port_stats(int(port))
