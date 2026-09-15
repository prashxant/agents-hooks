#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile
from pathlib import Path

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
        text = Path(job["log_file"]).read_text(encoding="utf-8")
        text = text.replace("_Summary pending._", f"1. {a}\n2. {b}", 1)
        Path(job["log_file"]).write_text(text, encoding="utf-8")
        job["status"] = "completed"
    except Exception as exc:
        job["status"], job["error"] = "failed", str(exc)
    jobfile.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__": main(sys.argv[1])
