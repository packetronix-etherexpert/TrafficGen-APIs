# Authentication

Depending on how the appliance is configured, the REST API (everything under `/TGAPI`) is either
**open** or **requires authentication**. Ask your appliance administrator which applies, or just try
`GET /TGAPI/help`: a `401` response means authentication is required.

## API tokens (recommended for scripts and CI)

Create a token in the appliance web UI (**Config > API tokens...**) or on the appliance shell:

```bash
python auth_cli.py token-create <username> ci-pipeline --days 90
```

The token (`pxtg_<id>_<secret>`) is shown **once**. Send it on every request:

```bash
curl -H "Authorization: Bearer $TRAFFICGEN_TOKEN" http://<appliance>:9102/TGAPI/ports
```

`X-API-Key: <token>` is also accepted for tools that cannot set an `Authorization` header.

- A token acts as its owner, with the owner's **current** role. Deleting the user, or changing their
  role, takes effect immediately.
- Tokens work **only** on `/TGAPI`. They do not open the web UI or the user-management pages.
- Tokens expire (default 90 days; `--days 0` = never). Revoke one at any time from the same page.
- Use one token per pipeline or tool so you can revoke them independently.

With the SDK: `TrafficGenClient("http://<appliance>:9102", token=os.environ["TRAFFICGEN_TOKEN"])`.

## Browser-style login (alternative)

`TrafficGenClient.login(username, password)` signs in with a web-UI account and keeps the session
cookie for later calls. Prefer tokens for unattended jobs: they can be limited to one purpose and
revoked without changing anyone's password.

## Security notes

- **Use HTTPS.** Over plain HTTP, tokens and passwords cross the network in clear text. Put the appliance
  behind a TLS-terminating reverse proxy, and pass `verify=False` (or a CA bundle path) only for
  self-signed certificates in a lab.
- Keep tokens in your CI system's secret store (`TRAFFICGEN_TOKEN`), never in the repository.
- **Roles.** A token's role is its owner's role. All tokens can call every `/TGAPI` endpoint, including
  those that change hardware settings or start traffic; the role distinction applies to the web UI
  (user management, firmware reload and reboot are admin-only there).
