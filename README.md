# use-dockploy-mcp

A Claude Code skill for deploying, managing, and monitoring services on [Dokploy](https://dokploy.com) via MCP tools.

## What it does

This skill teaches Claude Code how to interact with your Dokploy instance efficiently — deploy apps, read logs, manage domains, update environment variables, and inspect container status — all through the Dokploy MCP server, never via direct HTTP calls.

## Install

```bash
npx skills add CraftaleAgency/use-dokploy-mcp
```

Or install only the specific skill:

```bash
npx skills add CraftaleAgency/use-dokploy-mcp --skill run-dokploy-mcp
```

### Alternative methods

Copy the skill into your project:

```bash
# From your project root
cp -r .claude/skills/ your-project/.claude/skills/
```

Or add as a git submodule:

```bash
git submodule add https://github.com/CraftaleAgency/use-dockploy-mcp.git .claude/skills/run-dokploy-mcp
```

## Prerequisites

1. **Dokploy MCP server** configured in your Claude Code settings (`.claude/settings.json` or global):

```json
{
  "mcpServers": {
    "dokploy": {
      "command": "npx",
      "args": ["-y", "@dokploy/mcp"],
      "env": {
        "DOKPLOY_URL": "https://your-dokploy-instance.com",
        "DOKPLOY_ACCESS_TOKEN": "your-api-token"
      }
    }
  }
}
```

2. **Python 3** (for the `extract.py` helper — handles the 140K+ `project-all` response)

## What's included

| File | Purpose |
|---|---|
| `SKILL.md` | Agent-facing instructions — auto-loads when deploying or managing services |
| `extract.py` | Python helper that parses `project-all` output into compact name+ID listings |

## Key patterns

### Finding resource IDs (the big one)

`project-all` returns **140K+ characters** on most instances. Reading it directly blows the context window. The skill provides `extract.py` to filter:

```bash
python3 extract.py <project-all-output-file> my-project
```

### Common operations

```
# Deploy
application-deploy(applicationId: "...")
compose-deploy(composeId: "...")

# Logs
application-readLogs(applicationId: "...", tail: 50, search: "error")

# Update env vars (newline-separated, not JSON)
application-saveEnvironment(applicationId: "...", env: "KEY=val\nKEY2=val2", ...)

# Domains
domain-byApplicationId(applicationId: "...")
```

### Anti-patterns documented

- Never read `project-all` output directly
- `*-search` tools are unreliable — fall back to `project-all` + filter
- `project-update` requires `name` even if only changing `description`
- Compose logs need Docker `containerId`, not Dokploy `composeId`

## License

MIT
