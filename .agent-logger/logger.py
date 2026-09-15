#!/usr/bin/env python3
"""Fail-open, standard-library lifecycle logger for project-local agent hooks."""
import datetime as dt
import getpass
import json
import os
import pathlib
import subprocess
import sys
import uuid

EVENTS = {"turn.started", "turn.completed", "turn.interrupted", "turn.failed", "session.started", "session.ended"}

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

def root_for(cwd):
    try:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=1)
        if r.returncode == 0 and r.stdout.strip(): return pathlib.Path(r.stdout.strip()).resolve()
    except Exception: pass
    return pathlib.Path(cwd).resolve()

def safe(value, default="unknown"):
    return str(value).strip() if value is not None and str(value).strip() else default

def lock(path):
    # mkdir is atomic across processes; stale locks are removed only when clearly old.
    for _ in range(200):
        try: path.mkdir(); return
        except FileExistsError:
            try:
                if dt.datetime.now().timestamp() - path.stat().st_mtime > 30: path.rmdir()
            except OSError: pass
            import time; time.sleep(.01)
    raise RuntimeError("logger lock timeout")

def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw else {}
        if not isinstance(data, dict): return
        cwd = safe(data.get("cwd"), os.getcwd())
        root = root_for(cwd)
        state = root / ".agent-logger" / "state"
        state.mkdir(parents=True, exist_ok=True)
        agent = safe(data.get("agent")); session = safe(data.get("session_id")); event = safe(data.get("event"))
        turn = safe(data.get("turn_id"), "")
        if event not in EVENTS or agent == "unknown" or session == "unknown": return
        if event.startswith("turn.") and not turn:
            turn = uuid.uuid4().hex
        key = uuid.uuid5(uuid.NAMESPACE_URL, agent + "\0" + session + "\0" + turn).hex
        statefile, lockfile = state / (key + ".json"), state / ".lock"
        if event == "turn.started":
            record = {"prompt": str(data.get("prompt") or "")}
            tmp = statefile.with_suffix(".tmp-" + uuid.uuid4().hex)
            tmp.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8"); os.replace(tmp, statefile)
            return
        if not event.startswith("turn.") or event == "turn.started": return
        if not statefile.exists(): return
        record = json.loads(statefile.read_text(encoding="utf-8"))
        ended = safe(data.get("timestamp"), now())
        lines = ["## AI agent turn", "", f"- **Username:** `{getpass.getuser()}`", f"- **Time:** `{ended}`", "", "### Prompt", ""]
        prompt = record.get("prompt", "")
        lines.extend("> " + line if line else ">" for line in prompt.splitlines() or [""])
        lines.extend(["", "---", ""])
        lock(lockfile)
        try:
            with (root / "log.md").open("a", encoding="utf-8") as f: f.write("\n".join(lines))
        finally:
            try: lockfile.rmdir()
            except OSError: pass
        try: statefile.unlink()
        except OSError: pass
    except Exception:
        return

if __name__ == "__main__": main()
