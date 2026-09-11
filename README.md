# Reusable agent hooks

This folder contains the project-local agent hooks and logger.

This package is hosted at `github.com/prashxant/agents-hooks`.

After publishing, another project can install the hooks from its project root with:

```bash
curl -fsSL https://raw.githubusercontent.com/prashxant/agents-hooks/main/install.sh -o /tmp/install-agent-hooks.sh
bash /tmp/install-agent-hooks.sh
```

The installer backs up existing `.codex/hooks.json`, `.codex/hooks`, and `.agent-logger` paths before installing.
