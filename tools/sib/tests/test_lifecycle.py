"""Lifecycle tests: exact transition table, no shortcuts."""
from __future__ import annotations

import unittest

from tools.sib import lifecycle


class TestLifecycle(unittest.TestCase):
    def test_legal_happy_path(self):
        self.assertTrue(lifecycle.can_transition("GENERATED", "QA_PASSED"))
        self.assertTrue(lifecycle.can_transition("QA_PASSED", "STAGED"))
        self.assertTrue(lifecycle.can_transition("STAGED", "PUBLISHED"))

    def test_qa_failure_branch(self):
        self.assertTrue(lifecycle.can_transition("GENERATED", "QA_FAILED"))

    def test_no_generated_to_published_shortcut(self):
        self.assertFalse(lifecycle.can_transition("GENERATED", "PUBLISHED"))
        self.assertFalse(lifecycle.can_transition("GENERATED", "STAGED"))
        self.assertFalse(lifecycle.can_transition("QA_PASSED", "PUBLISHED"))

    def test_qa_failed_terminal(self):
        self.assertFalse(lifecycle.can_transition("QA_FAILED", "GENERATED"))
        self.assertFalse(lifecycle.can_transition("QA_FAILED", "QA_PASSED"))
        self.assertFalse(lifecycle.can_transition("QA_FAILED", "STAGED"))
        self.assertFalse(lifecycle.can_transition("QA_FAILED", "PUBLISHED"))

    def test_published_terminal(self):
        for dst in ("GENERATED", "QA_PASSED", "QA_FAILED", "STAGED",
                    "PUBLISHED"):
            self.assertFalse(lifecycle.can_transition("PUBLISHED", dst))

    def test_invalid_statuses(self):
        self.assertFalse(lifecycle.is_valid_status("PUBLISHED_SIGNED"))
        self.assertFalse(lifecycle.can_transition("BANANA", "STAGED"))
        self.assertFalse(lifecycle.can_transition("STAGED", "BANANA"))


if __name__ == "__main__":
    unittest.main()
