#!/usr/bin/env python3

import json
import os
import sys
import getpass
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc)


def isoformat(timestamp):
    return timestamp.isoformat().replace("+00:00", "Z")


def find_project_root(start):
    current = Path(start).resolve()
    for directory in [current, *current.parents]:
        if (directory / ".git").exists():
            return directory
    return current


def safe_filename(value):
    return "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in value
    )


def append_atomically(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(descriptor, content.encode("utf-8"))
    finally:
        os.close(descriptor)


def format_prompt(prompt):
    return "\n".join(f"> {line}" if line else ">" for line in prompt.splitlines())


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    event_name = event.get("hook_event_name")
    session_id = event.get("session_id", "unknown-session")
    turn_id = event.get("turn_id", "unknown-turn")
    project_root = find_project_root(event.get("cwd", os.getcwd()))
    state_directory = project_root / ".codex" / "logger-state"
    state_file = state_directory / f"{safe_filename(turn_id)}.json"
    log_file = project_root / "log.md"

    if event_name == "UserPromptSubmit":
        state_directory.mkdir(parents=True, exist_ok=True)
        state = {
            "session_id": session_id,
            "turn_id": turn_id,
            "prompt": event.get("prompt", ""),
            "model": event.get("model", "unknown"),
            "started_at": isoformat(utc_now()),
        }
        temporary_file = state_file.with_suffix(".tmp")
        temporary_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temporary_file.replace(state_file)
        return 0

    if event_name not in {"Stop", "Interrupt"} or not state_file.exists():
        return 0

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0

    ended_at = utc_now()
    started_at = datetime.fromisoformat(state["started_at"].replace("Z", "+00:00"))
    duration_seconds = round((ended_at - started_at).total_seconds(), 3)
    status = "completed" if event_name == "Stop" else "interrupted"
    entry = f"""
## Codex turn

- **Username:** `{getpass.getuser()}`
- **Time:** `{isoformat(ended_at)}`

### Prompt

{format_prompt(state["prompt"])}

---

"""
    append_atomically(log_file, entry)
    try:
        state_file.unlink()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
