"""SIB artifact status lifecycle.

Source of truth: docs/research/SUBJECT_INTELLIGENCE_BUILD_V1.md section 5:

    GENERATED -> QA_PASSED -> STAGED -> PUBLISHED
    GENERATED -> QA_FAILED

Notes:
* The validator itself NEVER performs a transition and never rewrites
  artifact status. ``can_transition`` is used by the explicit, operator-level
  ingestion commands (stage/publish) and by tests.
* QA_FAILED is terminal for a given artifact_version. Regeneration produces a
  new artifact_version whose status starts at GENERATED; it does not "unfail"
  the failed version.
* PUBLISHED is terminal (further edits require a new artifact_version).
"""
from __future__ import annotations

from typing import Dict, FrozenSet

STATUS_GENERATED = "GENERATED"
STATUS_QA_PASSED = "QA_PASSED"
STATUS_QA_FAILED = "QA_FAILED"
STATUS_STAGED = "STAGED"
STATUS_PUBLISHED = "PUBLISHED"

ALL_STATUSES = (STATUS_GENERATED, STATUS_QA_PASSED, STATUS_QA_FAILED,
                STATUS_STAGED, STATUS_PUBLISHED)

TRANSITIONS: Dict[str, FrozenSet[str]] = {
    STATUS_GENERATED: frozenset({STATUS_QA_PASSED, STATUS_QA_FAILED}),
    STATUS_QA_PASSED: frozenset({STATUS_STAGED}),
    STATUS_QA_FAILED: frozenset(),          # terminal for the version
    STATUS_STAGED: frozenset({STATUS_PUBLISHED}),
    STATUS_PUBLISHED: frozenset(),          # terminal
}

# Publication requires the artifact to be STAGED and QA evidence to exist.
# There is no GENERATED -> PUBLISHED or QA_PASSED -> PUBLISHED shortcut.
PUBLICATION_SOURCES = frozenset({STATUS_STAGED})


def is_valid_status(status: str) -> bool:
    return status in ALL_STATUSES


def can_transition(src: str, dst: str) -> bool:
    """True iff dst is a lifecycle-legal successor of src."""
    if not is_valid_status(src) or not is_valid_status(dst):
        return False
    return dst in TRANSITIONS.get(src, frozenset())
