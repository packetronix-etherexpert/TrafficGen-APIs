"""Drive the appliance through the Open Traffic Generator (snappi) interface.

The OTG endpoints are optional: they exist only when the appliance runs with ENABLE_OTG=1.
If the appliance requires login, sign in first with the same account as the web UI (shown below).
"""
import os

import snappi

root = os.environ["TRAFFICGEN_BASE_URL"].rstrip("/")
api = snappi.api(location=root + "/TGAPI", verify=os.environ.get("TRAFFICGEN_VERIFY_TLS", "1") != "0")
if os.environ.get("TRAFFICGEN_USER"):
    # snappi keeps a requests.Session internally (checked against snappi 1.62; a private attribute):
    # log in through it so its cookie is sent with every OTG call.
    r = api._transport._session.post(root + "/login", allow_redirects=False,
                                     data={"username": os.environ["TRAFFICGEN_USER"],
                                           "password": os.environ.get("TRAFFICGEN_PASS", "")})
    assert r.status_code == 303, f"login failed: HTTP {r.status_code}"

config = api.config()
p1, p2 = (config.ports.port(name=n)[-1] for n in ("Port-1", "Port-2"))
flow = config.flows.flow(name="flow-1")[-1]
flow.tx_rx.port.tx_name, flow.tx_rx.port.rx_names = p1.name, [p2.name]
flow.rate.percentage = 10.0
api.set_config(config)
print("OTG config applied")
