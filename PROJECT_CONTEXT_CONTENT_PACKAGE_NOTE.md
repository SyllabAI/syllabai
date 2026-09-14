# Content Package Architecture Note

**Status:** PROPOSED  
**Date:** 2026-09-15

The project now has a proposed Content Compiler / Content Package architecture. See `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md`, `CONTENT_PACKAGE_V0_1.md`, and ADR-021.

Key boundary:

```text
Markdown content artifacts → validation/normalization → PostgreSQL domain projection
                                                  ↘ SQLite portable package
```

Markdown is durable and human-readable; PostgreSQL remains canonical runtime/domain storage; SQLite is a derived portable corpus/QA/research/distribution package. Generic MarkdownDB is not a core dependency.

This note exists only to make the architecture discoverable from the central project context; the companion architecture/ADR documents remain authoritative for the decision.
