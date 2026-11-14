"""Drive the appliance through the Open Traffic Generator (snappi) interface.

The OTG endpoints are optional: they exist only when the appliance runs with ENABLE_OTG=1.
If the appliance requires authentication, pass your API token as shown.
"""
import os

import snappi

api = snappi.api(location=os.environ["TRAFFICGEN_BASE_URL"].rstrip("/") + "/TGAPI")
if os.environ.get("TRAFFICGEN_TOKEN"):
    # snappi keeps a requests.Session internally (tested with snappi 1.62); this is a private attribute.
    api._transport._session.headers["Authorization"] = "Bearer " + os.environ["TRAFFICGEN_TOKEN"]

config = api.config()
p1, p2 = (config.ports.port(name=n)[-1] for n in ("Port-1", "Port-2"))
flow = config.flows.flow(name="flow-1")[-1]
flow.tx_rx.port.tx_name, flow.tx_rx.port.rx_names = p1.name, [p2.name]
flow.rate.percentage = 10.0
api.set_config(config)
print("OTG config applied")
