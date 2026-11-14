"""Configure one stream on port 1, run it for a few seconds, then stop it.

WARNING: this transmits real traffic out of port 1. Ports are numbered from 1.
"""
import time

from _common import connect

PORT, STREAM = 1, 1

tg = connect()
print("Appliance:", tg.system_info())
print("Port", PORT, "line rate:", tg.get_line_rate(PORT))

# Read-modify-write: change only the fields you name, keep everything else as it is.
tg.update_stream(PORT, STREAM, FrameLenType="Fixed", FrameLenMin=512, FrameLenMax=512, Rate=10)

tg.reset_stream_stats(PORT, STREAM)
tg.update_stream(PORT, STREAM, StreamEnable=True)       # start traffic
time.sleep(5)
print("Stream stats after 5 s:", tg.stream_stats(PORT))
tg.stop_stream(PORT, STREAM)
