#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile
from pathlib import Path

def update_summary(log_file, marker, summary):
    """Replace the pending summary only inside the block identified by marker."""
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
    if "_Summary pending._" not in block:
        raise ValueError("summary_placeholder_not_found:" + marker)
    block = block.replace("_Summary pending._", summary, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")

def main(path):
    jobfile = Path(path); job = json.loads(jobfile.read_text())
    if os.environ.get("AGENT_LOGGER_SUMMARIZER_RUNNING") == "1": return
    prompt = ("Return JSON only with exactly two string fields: summary_line_1 and summary_line_2.\n"
              "Line 1: what the user asked. Line 2: what the agent changed or produced.\n\n"
              + json.dumps({"prompt": job["prompt"], "response": job["response"]}, ensure_ascii=False))
    try:
        with tempfile.NamedTemporaryFile() as out:
            subprocess.run(["codex", "exec", "--ephemeral", "--skip-git-repo-check", "--output-last-message", out.name, "-"],
                           input=prompt, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=90, check=True, env={**os.environ, "AGENT_LOGGER_SUMMARIZER_RUNNING": "1"})
            result = json.loads(Path(out.name).read_text())
        a, b = result.get("summary_line_1", "").strip(), result.get("summary_line_2", "").strip()
        if not a or not b: raise ValueError("empty_summary")
        update_summary(job["log_file"], job["marker"], f"1. {a}\n2. {b}")
        job["status"] = "completed"
    except Exception as exc:
        attempts = int(job.get("attempts", 0)) + 1
        job["attempts"], job["error"] = attempts, str(exc)
        job["status"] = "waiting_for_provider" if attempts < 3 else "failed"
        if attempts >= 3:
            log = Path(job["log_file"])
            update_summary(log, job["marker"], "_Summary unavailable after 3 attempts._")
    jobfile.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__": main(sys.argv[1])
