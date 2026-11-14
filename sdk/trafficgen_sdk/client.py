"""Python client for the Packetronix Traffic Generator REST API."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

import requests

__all__ = ["TrafficGenClient", "TrafficGenError"]

API_PREFIX = "/TGAPI"


class TrafficGenError(Exception):
    """Raised for any HTTP error status or connection failure.

    Attributes:
        status_code: HTTP status, or None for connection-level failures.
        detail: the server's ``detail`` field (or response text) explaining the rejection.
    """

    def __init__(self, message: str, status_code: Optional[int] = None, detail: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class TrafficGenClient:
    """Client for one Traffic Generator appliance.

    Args:
        base_url: Appliance address, e.g. ``"http://10.0.0.5:9102"``. A trailing
            ``/TGAPI`` is accepted and not duplicated.
        token: API token (``pxtg_...``), sent as ``Authorization: Bearer``. Needed only
            when the appliance requires authentication for the REST API.
        verify: TLS certificate verification (``False`` for self-signed appliances, or a
            path to a CA bundle).
        timeout: Per-request timeout in seconds.
        session: Optional preconfigured ``requests.Session``.

    Example:
        >>> tg = TrafficGenClient("http://10.0.0.5:9102", token="pxtg_...")
        >>> tg.system_info()
    """

    def __init__(self, base_url: str, token: Optional[str] = None, *, verify: Any = True,
                 timeout: float = 30.0, session: Optional[requests.Session] = None):
        parts = urlsplit(base_url.rstrip("/"))
        path = parts.path[: -len(API_PREFIX)] if parts.path.endswith(API_PREFIX) else parts.path
        self._root = urlunsplit((parts.scheme, parts.netloc, path.rstrip("/"), "", ""))
        self.api_url = self._root + API_PREFIX
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.verify = verify
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    # ------------------------------------------------------------------ plumbing
    def login(self, username: str, password: str) -> None:
        """Start a cookie session with a web-UI account (alternative to an API token)."""
        try:
            r = self.session.post(self._root + "/login", data={"username": username, "password": password},
                                  timeout=self.timeout, allow_redirects=False)
        except requests.RequestException as e:
            raise TrafficGenError(f"Cannot reach {self._root}: {e}") from e
        if r.status_code != 303:
            raise TrafficGenError("Login failed: invalid username or password"
                                  if r.status_code in (401, 429) else f"Login failed: HTTP {r.status_code}",
                                  r.status_code)

    def _request(self, method: str, path: str, *, json: Any = None, params: Optional[dict] = None,
                 raw: bool = False) -> Any:
        url = self.api_url + "/" + path.lstrip("/")
        try:
            r = self.session.request(method, url, json=json, params=params, timeout=self.timeout, stream=raw)
        except requests.RequestException as e:
            raise TrafficGenError(f"{method} {url} failed: {e}") from e
        if not r.ok:
            try:
                body = r.json()
                detail = body.get("detail", body) if isinstance(body, dict) else body
            except ValueError:
                detail = r.text
            raise TrafficGenError(f"{method} {path} -> HTTP {r.status_code}: {detail}", r.status_code, detail)
        if raw:
            return r
        if not r.content:
            return None
        try:
            return r.json()
        except ValueError:
            return r.text

    # -------------------------------------------------------------------- system
    def help(self) -> Any:
        """Liveness check; returns ``{"message": "API is working OK!"}``."""
        return self._request("GET", "/help")

    def system_info(self) -> dict:
        """Application name, version and status."""
        return self._request("GET", "/system/info")

    def hardware_close(self) -> Any:
        """Release the card (used before external tools take over the device)."""
        return self._request("POST", "/system/hardware/close")

    def hardware_reinit(self) -> Any:
        """Re-open the card after :meth:`hardware_close`."""
        return self._request("POST", "/system/hardware/reinit")

    # --------------------------------------------------------------------- ports
    def list_ports(self) -> List[dict]:
        return self._request("GET", "/ports")

    def get_port(self, port_no: int) -> dict:
        return self._request("GET", f"/ports/{port_no}")

    def set_port(self, port_no: int, settings: dict) -> Any:
        """Replace a port's settings with ``settings`` (see ``PortSettingsModel``)."""
        return self._request("PUT", f"/ports/{port_no}", json=settings)

    def update_port(self, port_no: int, **fields: Any) -> Any:
        """Read the port's current settings, change only ``fields``, and write them back."""
        current = self.get_port(port_no)
        current.update(fields)
        return self.set_port(port_no, current)

    def get_link_status(self, port_no: int) -> Any:
        return self._request("GET", f"/ports/{port_no}/link_status")

    def get_line_rate(self, port_no: int) -> dict:
        """Live negotiated line rate, e.g. ``{"LineRate": "25G"}``."""
        return self._request("GET", f"/ports/{port_no}/line_rate")

    def set_line_rate(self, port_no: int, rate_sel: int) -> Any:
        """``rate_sel``: 1=1G, 2=10G, 3=25G, 4=100G, 5=100G+FEC."""
        return self._request("PUT", f"/ports/{port_no}/line_rate", params={"rate_sel": rate_sel})

    def arp(self, port_no: int, gateway_ip: str) -> Any:
        return self._request("POST", f"/ports/{port_no}/arp", json={"gateway_ip": gateway_ip})

    def ping(self, port_no: int, gateway_ip: str) -> Any:
        return self._request("POST", f"/ports/{port_no}/ping", json={"gateway_ip": gateway_ip})

    # ------------------------------------------------------------------- streams
    def list_streams(self, port_no: Optional[int] = None) -> List[dict]:
        """All streams, or only those of ``port_no``."""
        return self._request("GET", "/streams" if port_no is None else f"/streams/{port_no}")

    def get_stream(self, port_no: int, stream_no: int) -> dict:
        for s in self.list_streams(port_no):
            if s.get("StreamNo") == stream_no:
                return s
        raise TrafficGenError(f"No stream {stream_no} on port {port_no}", 404)

    def set_stream(self, port_no: int, stream_no: int, settings: dict) -> Any:
        """Replace a stream's settings (see ``StreamSettingsModel``). Set
        ``StreamEnable`` to ``True`` to start traffic."""
        return self._request("PUT", f"/streams/{port_no}/{stream_no}", json=settings)

    def update_stream(self, port_no: int, stream_no: int, **fields: Any) -> Any:
        """Read the stream's current settings, change only ``fields``, and write them back."""
        current = self.get_stream(port_no, stream_no)
        current.update(fields)
        return self.set_stream(port_no, stream_no, current)

    def stop_stream(self, port_no: int, stream_no: int) -> Any:
        return self._request("POST", f"/streams/{port_no}/{stream_no}/stop")

    def inject_error(self, port_no: int, stream_no: int, error_type: str) -> Any:
        """Inject a single error (e.g. ``"FCS"``, ``"Payload"``, ``"Sequence"``)."""
        return self._request("POST", f"/streams/{port_no}/{stream_no}/error", json={"error_type": error_type})

    # ----------------------------------------------------------------- statistics
    def port_stats(self, port_no: Optional[int] = None) -> Any:
        return self._request("GET", "/stats/ports" if port_no is None else f"/stats/ports/{port_no}")

    def port_mac_stats(self, port_no: int) -> dict:
        """MAC-level Tx/Rx counters: ``{"tx": [...], "rx": [...]}``."""
        return self._request("GET", f"/stats/ports/{port_no}/mac")

    def stream_stats(self, port_no: Optional[int] = None) -> Any:
        return self._request("GET", "/stats/streams" if port_no is None else f"/stats/streams/{port_no}")

    def stream_stats_batch(self, streams: Iterable[Tuple[int, int]]) -> Any:
        """Statistics for several ``(port_no, stream_no)`` pairs in one call."""
        queries = [{"port_no": p, "stream_no": s} for p, s in streams]
        return self._request("POST", "/stats/streams/batch", json={"queries": queries})

    def reset_port_stats(self, port_no: int) -> Any:
        return self._request("POST", f"/stats/ports/{port_no}/reset")

    def reset_stream_stats(self, port_no: int, stream_no: int, tx: bool = True, rx: bool = True) -> Any:
        return self._request("POST", f"/stats/ports/{port_no}/streams/{stream_no}/reset",
                             json={"tx": tx, "rx": rx})

    # ----------------------------------------------------------------------- BERT
    def set_bert_pattern(self, port_no: int, pattern: int, user_pattern: Optional[int] = None) -> Any:
        """``pattern``: 0=Fixed, 1=Increment, 2=PRBS31. ``user_pattern`` is the 32-bit value for Fixed."""
        body: Dict[str, Any] = {"pattern": pattern}
        if user_pattern is not None:
            body["UserPattern"] = user_pattern
        return self._request("POST", f"/ports/{port_no}/bert/pattern", json=body)

    def enable_bert(self, port_no: int, enable: bool) -> Any:
        return self._request("POST", f"/ports/{port_no}/bert/enable", json={"enable": 1 if enable else 0})

    def bert_stats(self, port_no: int) -> Any:
        return self._request("GET", f"/stats/ports/{port_no}/bert")

    # --------------------------------------------------------------------- Y.1564
    def y1564_list_configs(self) -> Any:
        return self._request("GET", "/y1564/configs")

    def y1564_get_config(self, filename: str) -> Any:
        return self._request("GET", f"/y1564/configs/{filename}")

    def y1564_save_config(self, name: str, config: dict, services: List[dict],
                          selected_services: Optional[List[dict]] = None) -> Any:
        return self._request("POST", "/y1564/configs", json={
            "name": name, "config": config, "services": services, "selected_services": selected_services})

    def y1564_start(self, config_name: Optional[str] = None, setup: Optional[dict] = None) -> Any:
        """Start a test from a saved config (``config_name``) or an inline ``setup``
        (``{"config": ..., "services": [...]}``)."""
        if (config_name is None) == (setup is None):
            raise ValueError("Give exactly one of config_name or setup")
        body = {"config_name": config_name} if config_name else {"setup": setup}
        return self._request("POST", "/y1564/start", json=body)

    def y1564_stop(self) -> Any:
        return self._request("POST", "/y1564/stop")

    def y1564_status(self) -> Any:
        return self._request("GET", "/y1564/status")

    def y1564_results(self) -> Any:
        return self._request("GET", "/y1564/results")

    def y1564_report(self, **fields: Any) -> Any:
        """Build a report; fields: customer, operator, site, dut, comment, prefix."""
        return self._request("POST", "/y1564/report", json=fields)

    def y1564_history(self) -> Any:
        return self._request("GET", "/y1564/history")

    def y1564_get_history(self, filename: str) -> Any:
        return self._request("GET", f"/y1564/history/{filename}")

    # -------------------------------------------------------------------- capture
    def get_capture_filters(self) -> Any:
        return self._request("GET", "/capture/filters")

    def get_capture_filter(self, port_no: int) -> dict:
        return self._request("GET", f"/capture/filters/{port_no}")

    def set_capture_filter(self, port_no: int, **fields: Any) -> dict:
        """Fields: mac, mac_filter, dst_ip, src_ip, port_range, vlan_range, ether_type,
        protocol, errored (see ``CaptureFilterModel``)."""
        return self._request("PUT", f"/capture/filters/{port_no}", json=fields)

    def delete_capture_filter(self, port_no: int) -> Any:
        return self._request("DELETE", f"/capture/filters/{port_no}")

    def start_capture(self, duration_s: int = 10, max_packets: int = 100000,
                      filters: Optional[dict] = None, restore_filters: bool = True) -> Any:
        return self._request("POST", "/captures", json={
            "duration_s": duration_s, "max_packets": max_packets,
            "filters": filters, "restore_filters": restore_filters})

    def list_captures(self) -> Any:
        return self._request("GET", "/captures")

    def get_capture(self, capture_id: str) -> Any:
        return self._request("GET", f"/captures/{capture_id}")

    def cancel_capture(self, capture_id: str) -> Any:
        return self._request("POST", f"/captures/{capture_id}/cancel")

    def delete_capture(self, capture_id: str) -> Any:
        return self._request("DELETE", f"/captures/{capture_id}")

    def download_pcap(self, capture_id: str, dest_path: str) -> str:
        """Save a finished capture as a pcap file and return ``dest_path``."""
        r = self._request("GET", f"/captures/{capture_id}/pcap", raw=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(65536):
                f.write(chunk)
        return dest_path

    def capture_analysis(self, capture_id: str, loss: bool = False, length: bool = False,
                         latency: bool = False) -> Any:
        """Analyses of a capture; with no flag set, all three are returned."""
        params = {k: True for k, v in (("loss", loss), ("length", length), ("latency", latency)) if v}
        return self._request("GET", f"/captures/{capture_id}/analysis", params=params)
