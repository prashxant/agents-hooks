# Project-local AI agent lifecycle logger

Adapters read the agent hook JSON from standard input and forward only normalized lifecycle metadata to `logger.py`. The logger is fail-open: malformed input or filesystem contention never blocks an agent. It records the username, time, and prompt in the project-root `log.md`; state is transient under `.agent-logger/state/`.

The adapter mappings reflect the stable event names supplied by each agent. OpenCode uses its plugin event payload to invoke `adapters/opencode.py`; its plugin should pass the event object through unchanged.
