#!/usr/bin/env python3
"""Generate docs/api-reference.md from docs/openapi/openapi.json (run export_openapi.py first)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GROUPS = [("System", ("/system", "/help")), ("Ports", ("/ports",)), ("Streams", ("/streams",)),
          ("Statistics", ("/stats",)), ("Y.1564 service tests", ("/y1564",)),
          ("Capture", ("/capture", "/captures"))]


def group_of(path):
    for name, prefixes in GROUPS:
        if any(path == p or path.startswith(p + "/") for p in prefixes):
            return name
    return "Other"


def schema_name(node):
    if not node:
        return ""
    if "$ref" in node:
        return node["$ref"].rsplit("/", 1)[-1]
    if node.get("type") == "array":
        return f"list[{schema_name(node.get('items'))}]"
    return node.get("type", "")


def main():
    spec = json.load(open(os.path.join(HERE, "openapi.json")))
    models = spec.get("components", {}).get("schemas", {})
    rows = {}
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            body = ""
            if "requestBody" in op:
                content = next(iter(op["requestBody"]["content"].values()))
                body = schema_name(content.get("schema"))
            q = [p["name"] + ("" if p.get("required") else "?") for p in op.get("parameters", []) if p["in"] == "query"]
            rows.setdefault(group_of(path), []).append((path, method.upper(), op.get("summary", ""), body, q,
                                                        (op.get("description") or "").strip().split("\n\n")[0]))
    out = [f"# {spec['info']['title']} - reference", "",
           f"Version {spec['info'].get('version', '')}. Base path: `/TGAPI` (for example `http://<appliance>:9102/TGAPI/ports`). "
           "Ports are numbered from 1. When the appliance requires authentication, sign in first - see [authentication](authentication.md).",
           "", "Generated from [`openapi/openapi.json`](openapi/openapi.json); "
           "an interactive view is in [`openapi/redoc.html`](openapi/redoc.html).", ""]
    for name, _ in GROUPS + [("Other", ())]:
        if name not in rows:
            continue
        out += [f"## {name}", "", "| Method | Path | Body | Query | Description |", "|---|---|---|---|---|"]
        for path, method, summary, body, q, desc in sorted(rows[name]):
            text = (desc or summary).replace("|", "\\|").replace("\n", " ")
            out.append(f"| {method} | `{path}` | {('`' + body + '`') if body else ''} | {', '.join('`' + x + '`' for x in q)} | {text} |")
        out.append("")
    out += ["## Models", ""]
    for n, m in sorted(models.items()):
        if n in ("HTTPValidationError", "ValidationError"):
            continue
        out += [f"### {n}", "", "| Field | Type | Required |", "|---|---|---|"]
        req = set(m.get("required", []))
        for k, v in m.get("properties", {}).items():
            t = schema_name(v) or " or ".join(schema_name(x) or "null" for x in v.get("anyOf", [])) or "any"
            if "default" in v:
                t += f" (default `{v['default']}`)"
            out.append(f"| `{k}` | {t} | {'yes' if k in req else ''} |")
        out.append("")
    open(os.path.join(HERE, "..", "api-reference.md"), "w").write("\n".join(out))
    print("Wrote docs/api-reference.md")


if __name__ == "__main__":
    main()
