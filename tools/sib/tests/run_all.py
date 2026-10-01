#!/usr/bin/env python3
"""SIB validator test suite runner.

Runs all test modules and prints the exact counts required by the
verification gate. Stdlib unittest only; no external deps.

Run:  python3 -m tools.sib.tests.run_all
"""
from __future__ import annotations

import os
import sys
import unittest

if __package__ in (None, ""):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

MODULES = [
    "tools.sib.tests.test_taxonomy",
    "tools.sib.tests.test_yamlmini",
    "tools.sib.tests.test_frontmatter",
    "tools.sib.tests.test_lifecycle",
    "tools.sib.tests.test_artifact_validator",
    "tools.sib.tests.test_anchors",
    "tools.sib.tests.test_manifest_validator",
    "tools.sib.tests.test_chunking",
    "tools.sib.tests.test_ingest",
    "tools.sib.tests.test_determinism",
    "tools.sib.tests.test_runtime_boundary",
]


def main() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for mod in MODULES:
        suite.addTests(loader.loadTestsFromName(mod))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    total = result.testsRun
    failed = len(result.failures)
    errored = len(result.errors)
    skipped = len(result.skipped)
    passed = total - failed - errored - skipped
    print()
    print("SIB_TEST_SUMMARY")
    print(f"UNIT_TESTS: {passed} passed / {failed + errored} failed / {skipped} skipped")
    print(f"TOTAL: {total}")
    return 0 if (failed == 0 and errored == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
