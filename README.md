# Reusable agent hooks

This folder contains the project-local agent hooks and logger.

This package is hosted at `github.com/prashxant/agents-hooks`.

Install from the root of the project where you want logging enabled:

```bash
curl -fsSL https://raw.githubusercontent.com/prashxant/agents-hooks/main/install.sh \
  -o /tmp/install-agent-hooks.sh
bash /tmp/install-agent-hooks.sh
```

The installer creates these exact paths in the current project:

```text
.codex/config.toml
.codex/hooks.json
.agent-logger/
log.md
```

It enables Codex hooks and writes completed turn logs to `log.md`. Run `pwd` before installing to confirm you are in the intended project root. Existing hook/logger paths are moved to timestamped backup paths before replacement; no numbered duplicate folders are created by the installer.

Verify the installation with:

```bash
ls -la .codex .agent-logger log.md
cat .codex/config.toml
```
