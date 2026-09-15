#!/usr/bin/env python3
import json, os, sys, subprocess
AGENT = os.path.splitext(os.path.basename(sys.argv[0]))[0]
def main():
    try: d = json.load(sys.stdin)
    except Exception: d = {}
    name = d.get("hook_event_name", d.get("event", ""))
    mapping = {"UserPromptSubmit":"turn.started", "BeforeAgent":"turn.started", "beforeSubmitPrompt":"turn.started", "user.message":"turn.started", "Stop":"turn.completed", "AfterAgent":"turn.completed", "stop":"turn.completed", "session.idle":"turn.completed", "Interrupt":"turn.interrupted", "error":"turn.failed", "SessionStart":"session.started", "SessionEnd":"session.ended", "sessionStart":"session.started", "sessionEnd":"session.ended"}
    event = mapping.get(name, name if name in mapping.values() else "")
    out = {"agent":AGENT, "event":event, "session_id":d.get("session_id") or d.get("sessionId") or "unknown", "turn_id":d.get("turn_id") or d.get("turnId") or "", "prompt":d.get("prompt") or d.get("user_prompt") or "", "model":d.get("model") or "unknown", "timestamp":d.get("timestamp"), "cwd":d.get("cwd") or os.getcwd()}
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.dirname(__file__)), "logger.py")], input=json.dumps(out), text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if __name__ == "__main__": main()
