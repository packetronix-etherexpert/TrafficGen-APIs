"""Read port, MAC and stream counters, then reset the port counters."""
from _common import connect

tg = connect()
for port in tg.list_ports():
    n = port["PortNo"]
    print(f"Port {n}: link={tg.get_link_status(n)} rate={tg.get_line_rate(n)}")
    mac = tg.port_mac_stats(n)
    print(f"  MAC tx counters: {len(mac['tx'])}, rx counters: {len(mac['rx'])}")
print("All stream stats:", tg.stream_stats())
tg.reset_port_stats(1)
print("Port 1 counters reset")
