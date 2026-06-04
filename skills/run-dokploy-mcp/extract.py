#!/usr/bin/env python3
"""
Extract structured resource listings from Dokploy project-all output.

Usage:
    python3 extract.py <result-file> [filter-term]

If filter-term is given, only projects matching (case-insensitive) are shown.
If omitted, all projects are listed.

Output format:
    Project: <name> (ID: <id>)
      Environment: <name> (ID: <id>)
        Application: <name> | ID: <id> | Status: <status>
        Compose: <name> | ID: <id> | Status: <status>
        Postgres: <name> | ID: <id>
        ...
"""
import json
import sys


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <result-file> [filter-term]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    filter_term = sys.argv[2].lower() if len(sys.argv) > 2 else None

    with open(filepath) as f:
        raw = f.read()

    # Strip leading non-JSON if present (tool output prefix, line numbers, etc.)
    # Find the first { or [ that starts valid JSON
    for i, ch in enumerate(raw):
        if ch in ("{", "["):
            raw = raw[i:]
            break

    # Use raw_decode to handle trailing content gracefully
    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(raw)

    # Normalize to list of projects
    if isinstance(data, dict):
        projects = data.get("data", data.get("projects", []))
        if not isinstance(projects, list):
            for v in data.values():
                if isinstance(v, list):
                    projects = v
                    break
    elif isinstance(data, list):
        projects = data
    else:
        print("Unexpected data format", file=sys.stderr)
        sys.exit(1)

    # Service type extractors: (plural_key, singular_label, id_field, optional_status_field)
    service_types = [
        ("applications", "Application", "applicationId", "applicationStatus"),
        ("compose", "Compose", "composeId", "composeStatus"),
        ("postgres", "Postgres", "postgresId", "applicationStatus"),
        ("mysql", "MySQL", "mysqlId", "applicationStatus"),
        ("mariadb", "MariaDB", "mariadbId", "applicationStatus"),
        ("mongo", "Mongo", "mongoId", "applicationStatus"),
        ("redis", "Redis", "redisId", "applicationStatus"),
        ("libsql", "LibSQL", "libsqlId", "applicationStatus"),
    ]

    found = False
    for p in projects:
        if not isinstance(p, dict):
            continue

        name = p.get("name", "")
        pid = p.get("projectId", p.get("id", ""))
        if filter_term and filter_term not in name.lower():
            continue

        found = True
        print(f"Project: {name} (ID: {pid})")

        for env in p.get("environments", []):
            ename = env.get("name", "")
            eid = env.get("environmentId", env.get("id", ""))
            print(f"  Environment: {ename} (ID: {eid})")

            for key, label, id_field, status_field in service_types:
                for svc in env.get(key, []):
                    if not isinstance(svc, dict):
                        continue
                    sname = svc.get("name", "")
                    sid = svc.get(id_field, svc.get("id", ""))
                    status = svc.get(status_field, "")
                    line = f"    {label}: {sname} | ID: {sid}"
                    if status:
                        line += f" | Status: {status}"
                    print(line)

    if not found:
        if filter_term:
            print(f"No projects matching '{filter_term}' found.", file=sys.stderr)
        else:
            print("No projects found.", file=sys.stderr)


if __name__ == "__main__":
    main()
