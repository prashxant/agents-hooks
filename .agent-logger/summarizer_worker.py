#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile
from pathlib import Path

def update_section(log_file, marker, placeholder, replacement):
    """Replace one placeholder only inside the block identified by marker."""
    path = Path(log_file)
    text = path.read_text(encoding="utf-8")
    marker_line = f"<!-- {marker} -->"
    start = text.find(marker_line)
    if start < 0:
        raise ValueError("log_marker_not_found:" + marker)
    end = text.find("\n---\n", start)
    if end < 0:
        raise ValueError("log_block_not_found:" + marker)
    block = text[start:end]
    if placeholder not in block:
        raise ValueError("placeholder_not_found:" + marker)
    block = block.replace(placeholder, replacement, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")

def main(path):
    jobfile = Path(path); job = json.loads(jobfile.read_text())
    if os.environ.get("AGENT_LOGGER_SUMMARIZER_RUNNING") == "1": return
    prompt = ("Return JSON only with exactly four fields: summary_line_1, summary_line_2, is_decision, decision_text.\n"
              "summary_line_1: what the user asked. summary_line_2: what the agent changed or produced.\n"
              "is_decision must be a boolean. decision_text must be a concise decision if is_decision is true, otherwise an empty string.\n\n"
              + json.dumps({"prompt": job["prompt"], "response": job["response"]}, ensure_ascii=False))
    try:
        with tempfile.NamedTemporaryFile() as out:
            subprocess.run(["codex", "exec", "--ephemeral", "--skip-git-repo-check", "--output-last-message", out.name, "-"],
                           input=prompt, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=90, check=True, env={**os.environ, "AGENT_LOGGER_SUMMARIZER_RUNNING": "1"})
            result = json.loads(Path(out.name).read_text())
        a, b = result.get("summary_line_1", "").strip(), result.get("summary_line_2", "").strip()
        decision, decision_text = result.get("is_decision"), result.get("decision_text", "").strip()
        if not a or not b or not isinstance(decision, bool) or (decision and not decision_text) or (not decision and decision_text): raise ValueError("invalid_summary_or_decision")
        update_section(job["log_file"], job["marker"], "_Summary pending._", f"1. {a}\n2. {b}")
        label = f"Decision: {decision_text}" if decision else "Not a Decision"
        update_section(job["log_file"], job["marker"], "_Decision pending._", label)
        job["status"] = "completed"
    except Exception as exc:
        attempts = int(job.get("attempts", 0)) + 1
        job["attempts"], job["error"] = attempts, str(exc)
        job["status"] = "waiting_for_provider" if attempts < 3 else "failed"
        if attempts >= 3:
            log = Path(job["log_file"])
            update_section(log, job["marker"], "_Summary pending._", "_Summary unavailable after 3 attempts._")
            update_section(log, job["marker"], "_Decision pending._", "_Decision unavailable after 3 attempts._")
    jobfile.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__": main(sys.argv[1])
