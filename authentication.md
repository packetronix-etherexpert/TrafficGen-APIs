# Authentication

Depending on how the appliance is configured, the REST API (everything under `/TGAPI`) is either
**open** or **requires you to sign in**. The API uses the same session login as the appliance's web UI:
there are no separate API keys or tokens. Try `GET /TGAPI/help` - a `401` response means login is required.

## Signing in

`POST /login` with the form fields `username` and `password` (the same account you use in the web UI).
A successful login answers `303` and sets a session cookie, `px_tgen_session`; send that cookie on every
later request. The session lasts 12 hours.

```bash
# keep the cookie in a file
curl -sk -c jar.txt -d username=ci -d password="$TRAFFICGEN_PASS" https://<appliance>/login
curl -sk -b jar.txt https://<appliance>/TGAPI/ports
curl -sk -b jar.txt https://<appliance>/logout
```

With the SDK, `login()` does this for you and signs in again automatically if the session expires:

```python
from trafficgen_sdk import TrafficGenClient

with TrafficGenClient("https://10.0.0.5", verify_tls=False) as tg:   # verify_tls=False: self-signed certificate
    tg.login("ci", "your-password")
    print(tg.list_ports())
```

## Accounts for scripts and CI

- Create a **dedicated account** for each pipeline or tool (web UI: **Config > Users...**, admin only; or
  `python auth_cli.py add ci` on the appliance). Give it the **`user`** role - it can use the whole REST API
  and cannot manage users.
- Use a long random password and keep it in your CI system's secret store (`TRAFFICGEN_USER`,
  `TRAFFICGEN_PASS`), never in the repository.
- To cut off a pipeline, delete its account or change its password; deleting an account ends its live
  sessions immediately.

## Security notes

- **Use HTTPS.** Over plain HTTP, passwords and session cookies cross the network in clear text. Put the
  appliance behind a TLS-terminating reverse proxy (the appliance's bundled nginx setup serves
  `https://<appliance>/` on port 443). For a self-signed certificate pass `verify_tls=False` (or a CA bundle
  path); for the examples, tests and CI set `TRAFFICGEN_VERIFY_TLS=0`.
- **Lockout.** After 5 failed logins for the same user from the same address within 5 minutes, further
  attempts get `429` for a few minutes - make sure a CI job with a wrong password does not keep retrying.
- **Roles.** Every signed-in account can call every `/TGAPI` endpoint, including those that change hardware
  settings or start traffic. The `admin` role matters only in the web UI (user management, firmware reload
  and reboot).
