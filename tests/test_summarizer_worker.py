import tempfile
import unittest
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location

SPEC = spec_from_file_location("summarizer_worker", ".agent-logger/summarizer_worker.py")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SummaryUpdateTests(unittest.TestCase):
    def test_updates_matching_block_and_preserves_other_entries(self):
        content = (
            "<!-- agent-turn:first -->\n## AI agent turn\n\n### Prompt\n> first\n\n"
            "### Summary\n\n_Summary pending._\n\n### Decision\n\n_Decision pending._\n\n---\n"
            "<!-- agent-turn:second -->\n## AI agent turn\n\n### Prompt\n> second\n\n"
            "### Summary\n\n_Summary pending._\n\n### Decision\n\n_Decision pending._\n\n---\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "log.md"
            log.write_text(content, encoding="utf-8")
            MODULE.update_section(log, "agent-turn:second", "_Summary pending._", "1. second asked\n2. second produced")
            MODULE.update_section(log, "agent-turn:second", "_Decision pending._", "Not a Decision")
            MODULE.update_section(log, "agent-turn:first", "_Summary pending._", "1. first asked\n2. first produced")
            MODULE.update_section(log, "agent-turn:first", "_Decision pending._", "Decision: choose first")
            result = log.read_text(encoding="utf-8")
        self.assertIn("<!-- agent-turn:first -->\n## AI agent turn", result)
        self.assertIn("1. first asked\n2. first produced", result)
        self.assertIn("1. second asked\n2. second produced", result)
        self.assertIn("Not a Decision", result)
        self.assertIn("Decision: choose first", result)
        self.assertNotIn("_Summary pending._", result)
        self.assertNotIn("_Decision pending._", result)


if __name__ == "__main__":
    unittest.main()
