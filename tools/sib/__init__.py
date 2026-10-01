"""SIB v1 validator and ingestion scaffolding (tools/sib).

Implements the deterministic validation boundary for Subject Intelligence
Build (SIB-1.0) artifacts as defined by:

* docs/research/SUBJECT_INTELLIGENCE_BUILD_V1.md   (protocol, PROPOSED)
* docs/research/SIB_ARTIFACT_SCHEMA_V1.md          (artifact schema, PROPOSED)

Architectural status: the SIB design remains PROPOSED. This package provides
the validation/ingestion scaffolding only; it does not promote SIB to
ACCEPTED and does not generate any subject artifact corpus.

Design invariants:
* validation is pure evidence -- it never mutates artifacts, manifests,
  canonical curriculum, KG, learner state or assessment truth;
* deterministic: identical input -> byte-identical reports;
* stdlib-only core (PyYAML used when available, guarded).
"""

__version__ = "0.1.0"

SIB_PROTOCOL = "SIB-1.0"
