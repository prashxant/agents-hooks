# Reusable agent hooks

This folder contains the project-local agent hooks and logger.

This package is hosted at `github.com/prashxant/agents-hooks`.

Install from the root of the project where you want logging enabled:

```bash
curl -fsSL https://raw.githubusercontent.com/prashxant/agents-hooks/main/install.sh \
  -o /tmp/install-agent-hooks.sh
bash /tmp/install-agent-hooks.sh
```

Existing installations are updated in place by default, without creating backup folders:

```bash
bash /tmp/install-agent-hooks.sh
```

To preserve backups before updating, use:

```bash
bash /tmp/install-agent-hooks.sh --backup
```

The installer creates these exact paths in the current project:

```text
.codex/config.toml
.codex/hooks.json
.agent-logger/
log.md
```

It enables Codex hooks and writes completed turn logs to `log.md`. Run `pwd` before installing to confirm you are in the intended project root. The default update replaces managed files in place, preserves `log.md` and runtime state, and does not create backup folders. The optional `--backup` mode moves existing hook/logger paths to timestamped backup paths first.

Verify the installation with:

```bash
ls -la .codex .agent-logger log.md
cat .codex/config.toml
```
