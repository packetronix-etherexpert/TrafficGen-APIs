"""Run an ITU-T Y.1564 service test from a configuration saved on the appliance."""
import sys
import time

from _common import connect

tg = connect()
configs = tg.y1564_list_configs()
print("Saved configurations:", configs)
name = sys.argv[1] if len(sys.argv) > 1 else None
if not name:
    sys.exit("usage: 04_y1564_from_saved_config.py <saved-config-filename>")

tg.y1564_start(config_name=name)
while tg.y1564_status()["is_running"]:
    time.sleep(5)
print("Results:", tg.y1564_results())
