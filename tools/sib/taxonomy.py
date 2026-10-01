"""SIB v1 research-family taxonomy.

Source of truth: docs/research/SUBJECT_INTELLIGENCE_BUILD_V1.md (section 3,
"Research families"). The taxonomy is universal; applicability is
subject-specific and recorded per artifact in the subject manifest.

95 artifacts across 12 families:
  CUR(8) EXP(8) MIS(9) ASM(10) MS(8) EXM(6) PED(9) PRA(5) PRO(7)
  HIS(7) TUT(10) GAP(8) = 95
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Family:
    """A SIB research family (e.g. 03 Misconception & Error Intelligence)."""

    code: str                 # short code used in artifact/record IDs, e.g. "MIS"
    number: str               # zero-padded family number from the design doc, e.g. "03"
    slug: str                 # metadata research_family value, e.g. "misconception_intelligence"
    title: str                # human title from the design doc
    artifacts: Tuple[str, ...]  # artifact titles indexed by their 1-based ordinal


@dataclass(frozen=True)
class ArtifactSpec:
    """One of the 95 taxonomy artifacts."""

    artifact_id: str          # e.g. "MIS-01"
    family_code: str          # e.g. "MIS"
    family_slug: str          # e.g. "misconception_intelligence"
    title: str                # e.g. "Misconception Atlas"
    default_slug: str         # canonical filename slug, e.g. "MISCONCEPTION_ATLAS"


def _family(code: str, number: str, slug: str, title: str, names: List[str]) -> Family:
    return Family(code=code, number=number, slug=slug, title=title,
                  artifacts=tuple(names))


FAMILIES: Dict[str, Family] = {f.code: f for f in [
    _family("CUR", "01", "curriculum_intelligence", "Curriculum Intelligence", [
        "Curriculum Overview", "Specification Interpretation", "Concept Taxonomy",
        "Concept Relationships", "Prerequisite Knowledge Map", "Cross-Topic Connections",
        "Terminology & Definitions", "Curriculum Boundaries"]),
    _family("EXP", "02", "explanation_intelligence", "Explanation Intelligence", [
        "Core Concept Explanations", "Simple Explanations", "Deep Explanations",
        "Alternative Explanations", "Analogies & Mental Models", "Conceptual Distinctions",
        "Why It Works", "Common Why Questions"]),
    _family("MIS", "03", "misconception_intelligence", "Misconception & Error Intelligence", [
        "Misconception Atlas", "Concept Confusion Atlas", "Common Student Errors",
        "Reasoning Errors", "Calculation Errors", "Terminology Errors",
        "Exam Answer Errors", "Misconception Diagnostics", "Misconception Interventions"]),
    _family("ASM", "04", "assessment_intelligence", "Assessment Intelligence", [
        "Assessment Overview", "Question Taxonomy", "Question Archetypes",
        "Command Word Analysis", "Mark Allocation Patterns", "Question Difficulty Patterns",
        "Multi-Concept Question Patterns", "Context Patterns",
        "Question Progression Patterns", "Assessment Coverage Analysis"]),
    _family("MS", "05", "mark_scheme_intelligence", "Mark Scheme Intelligence", [
        "Mark Scheme Structure", "Mark Point Taxonomy", "Required Answer Elements",
        "Acceptable Alternatives", "Common Mark-Loss Patterns", "Partial Credit Patterns",
        "Examiner/Marking Language", "Answer Quality Patterns"]),
    _family("EXM", "06", "examiner_intelligence", "Examiner Intelligence", [
        "Examiner Report Synthesis", "Recurring Examiner Warnings", "What Examiners Reward",
        "What Examiners Penalize", "Question-Specific Examiner Insights",
        "Exam Technique Insights"]),
    _family("PED", "07", "learning_pedagogy_intelligence", "Learning & Pedagogy Intelligence", [
        "Learning Sequence Analysis", "Prerequisite Learning Paths", "Difficulty Progression",
        "Explanation Strategies", "Practice Strategies", "Retrieval Practice Opportunities",
        "Interleaving Opportunities", "Scaffolding Strategies",
        "Diagnostic Teaching Strategies"]),
    _family("PRA", "08", "practical_procedural_intelligence",
            "Practical / Procedural Intelligence", [
        "Core Procedures", "Method/Technique Patterns", "Practical/Experimental Intelligence",
        "Procedure Errors & Failure Modes", "Method Selection Guide"]),
    _family("PRO", "09", "problem_solving_intelligence", "Problem-Solving Intelligence", [
        "Problem-Solving Frameworks", "Problem Type → Method Mapping",
        "Multi-Step Reasoning Patterns", "Decision Points", "Dead Ends & Failed Approaches",
        "Worked-Reasoning Patterns", "Transfer Patterns"]),
    _family("HIS", "10", "historical_longitudinal_intelligence",
            "Historical / Longitudinal Intelligence", [
        "Specification Evolution", "Legacy → Current Mapping", "Assessment Evolution",
        "Terminology Evolution", "Question Evolution", "Persistent Patterns",
        "Historical Relevance Analysis"]),
    _family("TUT", "11", "tutor_intelligence", "Tutor Intelligence", [
        "Subject Tutor Knowledge Base", "Common Student Questions",
        "Follow-Up Question Patterns", "Socratic Question Patterns", "Hint Strategies",
        "Misconception Response Patterns", "Exam Feedback Patterns",
        "Concept Comparison Guides", "Deep-Dive Explanations",
        "Subject-Specific Tutor Guidance"]),
    _family("GAP", "12", "gap_intelligence", "Gap Intelligence", [
        "Curriculum Coverage Gaps", "KG Coverage Gaps", "Assessment Coverage Gaps",
        "Misconception Coverage Gaps", "Resource Quality Gaps", "Retrieval Risk Analysis",
        "Tutor Knowledge Gaps", "Subject Research Backlog"]),
]}

# ---- artifact lookup tables -------------------------------------------------

ARTIFACTS: Dict[str, ArtifactSpec] = {}
for _f in FAMILIES.values():
    for _i, _title in enumerate(_f.artifacts, start=1):
        _aid = f"{_f.code}-{_i:02d}"
        _slug = (_title.upper()
                 .replace("&", "AND")
                 .replace("→", "TO")
                 .replace("/", " ")
                 .replace("-", " ")
                 .replace("(", " ")
                 .replace(")", " "))
        # normalize whitespace/underscores deterministically
        _slug = "_".join("".join(ch if (ch.isalnum() or ch in "_") else "_"
                                 for ch in _slug).split("_"))
        while "__" in _slug:
            _slug = _slug.replace("__", "_")
        _slug = _slug.strip("_")
        ARTIFACTS[_aid] = ArtifactSpec(artifact_id=_aid, family_code=_f.code,
                                       family_slug=_f.slug, title=_title,
                                       default_slug=_slug)

TAXONOMY_SIZE = len(ARTIFACTS)  # expected 95

# ---- identifier conventions --------------------------------------------------

# artifact ID: family code (2-3 uppercase letters) + 2-digit ordinal
ARTIFACT_ID_PATTERN = r"^[A-Z]{2,3}-[0-9]{2}$"
# record ID: family code + 3-digit ordinal (distinguishes records from artifacts)
RECORD_ID_PATTERN = r"^([A-Z]{2,3})-[0-9]{3}$"


def is_valid_artifact_id(artifact_id: str) -> bool:
    """Structural (shape) validity of an artifact ID."""
    import re
    return bool(re.match(ARTIFACT_ID_PATTERN, artifact_id or ""))


def is_valid_record_id(record_id: str) -> bool:
    """Structural (shape) validity of a machine-readable record ID (MIS-001 style)."""
    import re
    return bool(re.match(RECORD_ID_PATTERN, record_id or ""))


def family_of(artifact_id: str) -> str:
    """Family code for an artifact ID, or '' when unknown."""
    if not is_valid_artifact_id(artifact_id):
        return ""
    return artifact_id.split("-")[0]


def expected_family_slug(artifact_id: str) -> str:
    """research_family value an artifact must carry for its artifact_id."""
    fam = FAMILIES.get(family_of(artifact_id))
    return fam.slug if fam else ""


def expected_record_family(record_id: str) -> str:
    """Family code implied by a record ID, or ''."""
    import re
    m = re.match(RECORD_ID_PATTERN, record_id or "")
    return m.group(1) if m else ""


def canonical_filename(subject: str, specification: str, artifact_id: str,
                       slug: str | None = None) -> str:
    """Canonical artifact filename.

    Contract (SIB_ARTIFACT_SCHEMA_V1.md §1, PROPOSED/DEFINED 2026-10-01):

        <SUBJECT>_<SPECIFICATION>_<ARTIFACT_ID>_<SLUG>.md

    Slot 2 is the SPECIFICATION code (e.g. ``4CH1``) -- the template and the
    worked example agree on this. The qualification (e.g. International
    GCSE) is required front-matter metadata but never participates in the
    filename.
    """
    norm_subj = (subject or "").upper().replace(" ", "_")
    norm_spec = (specification or "").upper().replace(" ", "_")
    slug_part = (slug or ARTIFACTS[artifact_id].default_slug) if artifact_id in ARTIFACTS else (slug or "")
    return f"{norm_subj}_{norm_spec}_{artifact_id}_{slug_part}.md".replace("__", "_")


def all_artifact_ids() -> List[str]:
    """All 95 artifact IDs in family/ordinal order (deterministic)."""
    return list(ARTIFACTS.keys())
