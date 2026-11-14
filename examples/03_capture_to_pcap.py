"""Capture traffic for 10 s with a UDP filter on port 1, analyse it, and save the pcap."""
import time

from _common import connect

tg = connect()
tg.set_capture_filter(1, protocol="udp", mac_filter="promiscuous")
cap = tg.start_capture(duration_s=10, max_packets=50000)
cid = cap["id"]
print("Started capture", cid)

# States: starting -> running -> done (or failed / cancelled)
while True:
    status = tg.get_capture(cid)
    if status["state"] not in ("starting", "running"):
        break
    time.sleep(1)
if status["state"] != "done":
    raise SystemExit(f"Capture {status['state']}: {status.get('error')}")

print("Loss/latency/length analysis:", tg.capture_analysis(cid))
print("Saved", tg.download_pcap(cid, f"capture_{cid}.pcap"))
