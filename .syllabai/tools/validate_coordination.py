#!/usr/bin/env python3
"""Coordination-state validator for the SyllabAI multi-agent system.

Phase 1 is WARN-ONLY by design (ADR-style conservative rollout):
findings are printed and written to the optional step summary, but the
script exits 0 unless run with --mode strict. Flip the workflow to
--mode strict only after two clean weeks (zero findings), per the
operator's decision.

Checked surfaces
----------------
locks.yaml (active leases):
  L1  required lease fields present (resource, owner, task, base_commit,
      acquired_at, expires_at) per lease_schema.required
  L2  expires_at parses and is in the future (expired => release/reclaim)
  L3  lease resource is a known shared resource (agent-registry
      shared_resources ∪ locks.yaml resource_classes)
  L4  lease task references an existing .syllabai/tasks/<task>.yaml
  L5  no duplicate active lease on a serialized resource

locks.yaml (structured fulfilled-lease history, T-COORD-2 P2):
  H1  required history row fields present (resource, task, outcome,
      released_at, receipt)
  H2  outcome within the legal vocabulary
  H3  history task references an existing task packet (warn)
  H4  released_at parses (warn)
  H5  no duplicate (resource, task) history rows (warn)

agent-registry.yaml:
  R1  agents' requires_coordination_for entries reference known shared
      resources
  R2  registry shared_resources and locks.yaml resource_classes do not
      contradict on policy (serialized/coordinated/operator-gated)

tasks/*.yaml (task packets):
  T1  task.id matches the filename stem (or filename stem starts with
      the id + '-' for sub-task files)
  T2  status is a legal enum value (READY|EXECUTING|BLOCKED|VERIFYING|DONE)
  T3  claims keys (if present) use only the 4 legal labels
  T4  VERIFYING/DONE packets have non-empty acceptance
  T5  EXECUTING/VERIFYING/DONE packets have a non-empty owner
  T0  file parses as YAML at all

Exit codes: 0 = warn mode (always), 1 = strict mode with findings,
2 = internal error (bad invocation, unreadable files).
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

LEGAL_STATUSES = {"READY", "EXECUTING", "BLOCKED", "VERIFYING", "DONE"}
LEGAL_CLAIM_LABELS = {"VERIFIED", "INFERRED", "REPORTED", "UNVERIFIED"}
KNOWN_POLICIES = {"serialized", "coordinated", "operator-gated"}
LEGAL_HISTORY_OUTCOMES = {"fulfilled_released", "expired_reclaimed", "superseded"}
HISTORY_REQUIRED = ["resource", "task", "outcome", "released_at", "receipt"]


class Report:
    def __init__(self, strict: bool, summary_path: str | None):
        self.strict = strict
        self.findings: list[dict] = []
        self.summary_path = summary_path

    def add(self, code: str, severity: str, subject: str, detail: str):
        self.findings.append(
            {"code": code, "severity": severity, "subject": subject, "detail": detail}
        )

    def error(self, code: str, subject: str, detail: str):
        self.add(code, "ERROR", subject, detail)

    def warn(self, code: str, subject: str, detail: str):
        self.add(code, "WARNING", subject, detail)

    @property
    def errors(self) -> int:
        return sum(1 for f in self.findings if f["severity"] == "ERROR")

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f["severity"] == "WARNING")

    def exit_code(self) -> int:
        if not self.strict:
            return 0
        return 1 if self.findings else 0

    def render(self) -> str:
        lines = []
        if not self.findings:
            lines.append("coordination-guard: 0 findings — coordination state is clean.")
        else:
            lines.append(
                f"coordination-guard: {self.errors} error(s), {self.warnings} warning(s)"
                + ("  [STRICT MODE]" if self.strict else "  [WARN-ONLY phase 1]")
            )
            for f in sorted(self.findings, key=lambda x: (x["severity"], x["code"])):
                lines.append(f"  [{f['severity']}] {f['code']} {f['subject']}: {f['detail']}")
        return "\n".join(lines)

    def write_summary(self, extra: str = ""):
        if not self.summary_path:
            return
        try:
            with open(self.summary_path, "a", encoding="utf-8") as fh:
                fh.write("## Coordination guard\n\n```\n")
                fh.write(self.render())
                if extra:
                    fh.write("\n\n" + extra)
                fh.write("\n```\n")
        except OSError:
            pass  # summary is best-effort; never fail the run on it


def load_yaml(path: Path, report: Report, subject: str):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        report.error("YAML-PARSE", subject, f"unparseable YAML: {str(exc).splitlines()[0]}")
    except OSError as exc:
        report.error("IO", subject, f"unreadable: {exc}")
    return None


def parse_ts(value) -> dt.datetime | None:
    """Parse an ISO-ish timestamp; tolerate 'Z', missing seconds and the
    datetime.date/datetime objects YAML produces for bare ISO dates."""
    if isinstance(value, dt.datetime):
        return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.min, tzinfo=dt.timezone.utc)
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError:
        try:  # date-only
            parsed = dt.datetime.fromisoformat(raw + "T00:00:00+00:00")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def known_shared_resources(registry: dict, locks: dict) -> set[str]:
    known: set[str] = set()
    for name in (registry.get("shared_resources") or {}):
        known.add(str(name))
    for name in (locks.get("resource_classes") or {}):
        known.add(str(name))
    return known


def check_locks(locks_doc: dict, report: Report, known_resources: set[str],
                serialized: set[str], task_ids: set[str]):
    lease_list = locks_doc.get("locks") or []
    if not isinstance(lease_list, list):
        report.error("L-FORMAT", ".syllabai/locks.yaml", "locks is not a list")
        return
    seen_on_serialized: dict[str, str] = {}
    now = dt.datetime.now(dt.timezone.utc)
    for i, lease in enumerate(lease_list):
        subject = f".syllabai/locks.yaml lease[{i}]"
        if not isinstance(lease, dict):
            report.error("L-FORMAT", subject, "lease is not a mapping")
            continue
        resource = str(lease.get("resource", ""))
        task = str(lease.get("task", ""))
        required = (locks_doc.get("lease_schema") or {}).get("required") or [
            "resource", "owner", "task", "base_commit", "acquired_at", "expires_at",
        ]
        missing = [k for k in required if not lease.get(k)]
        if missing:
            report.error("L1-SCHEMA", subject, f"missing required fields: {', '.join(missing)}")
        if resource and resource not in known_resources:
            report.warn("L3-RESOURCE", subject,
                        f"resource '{resource}' not in shared_resources/resource_classes")
        if task and task not in task_ids:
            report.warn("L4-TASKREF", subject,
                        f"task '{task}' has no packet in .syllabai/tasks/")
        expiry = parse_ts(lease.get("expires_at"))
        if lease.get("expires_at") and expiry is None:
            report.warn("L2-EXPIRY", subject,
                        f"expires_at '{lease.get('expires_at')}' unparsable")
        elif expiry is not None and expiry < now:
            report.warn("L2-EXPIRED", subject,
                        f"expired at {lease.get('expires_at')} — release or reclaim per the rule")
        if resource in serialized and resource:
            if resource in seen_on_serialized:
                report.error("L5-DUP", subject,
                             f"serialized resource '{resource}' also leased by {seen_on_serialized[resource]}")
            else:
                seen_on_serialized[resource] = task or f"lease[{i}]"


def check_registry(registry: dict, report: Report, known_resources: set[str],
                   lock_policies: dict):
    for agent_name, agent in (registry.get("agents") or {}).items():
        if not isinstance(agent, dict):
            continue
        for res in agent.get("requires_coordination_for") or []:
            if str(res) not in known_resources:
                report.warn("R1-RESOURCE", f"agent-registry.yaml agent '{agent_name}'",
                            f"requires_coordination_for '{res}' is not a known shared resource")
    reg_policies = {}
    for name, spec in (registry.get("shared_resources") or {}).items():
        if isinstance(spec, dict):
            reg_policies[str(name)] = str(spec.get("allocation", ""))
    for name, policy in reg_policies.items():
        if policy and policy not in KNOWN_POLICIES:
            report.warn("R2-POLICY", f"agent-registry.yaml shared_resource '{name}'",
                        f"unknown allocation policy '{policy}'")
        if name in lock_policies and policy and lock_policies[name] and lock_policies[name] != policy:
            report.warn("R2-CONTRADICTION", f"shared resource '{name}'",
                        f"agent-registry says '{policy}' but locks.yaml resource_classes says '{lock_policies[name]}'")


def check_history(locks_doc: dict, report: Report, task_ids: set[str]):
    """Structured fulfilled-lease history (T-COORD-2 P2). Append-only block;
    prose release annotations remain legal legacy records."""
    history = locks_doc.get("history")
    if history is None:
        return  # legacy file without the block — nothing to check
    if not isinstance(history, list):
        report.error("H-FORMAT", ".syllabai/locks.yaml history", "history is not a list")
        return
    seen_pairs = {}
    for i, row in enumerate(history):
        subject = f".syllabai/locks.yaml history[{i}]"
        if not isinstance(row, dict):
            report.error("H-FORMAT", subject, "history row is not a mapping")
            continue
        missing = [k for k in HISTORY_REQUIRED if not row.get(k)]
        if missing:
            report.error("H1-SCHEMA", subject, f"missing required fields: {', '.join(missing)}")
        outcome = str(row.get("outcome", ""))
        if outcome and outcome not in LEGAL_HISTORY_OUTCOMES:
            report.warn("H2-OUTCOME", subject,
                        f"outcome '{outcome}' outside the vocabulary: "
                        f"{', '.join(sorted(LEGAL_HISTORY_OUTCOMES))}")
        task = str(row.get("task", ""))
        if task and task not in task_ids:
            report.warn("H3-TASKREF", subject,
                        f"task '{task}' has no packet in .syllabai/tasks/")
        if row.get("released_at") and parse_ts(row.get("released_at")) is None:
            report.warn("H4-DATE", subject,
                        f"released_at '{row.get('released_at')}' unparsable")
        pair = (str(row.get("resource", "")), task)
        if pair[0] and pair[1]:
            if pair in seen_pairs:
                report.warn("H5-DUP", subject,
                            f"duplicate (resource, task) history pair with row {seen_pairs[pair]}")
            else:
                seen_pairs[pair] = f"history[{i}]"


def check_tasks(tasks_dir: Path, report: Report) -> set[str]:
    task_ids: set[str] = set()
    if not tasks_dir.is_dir():
        report.warn("T-DIR", ".syllabai/tasks", "directory missing")
        return task_ids
    for path in sorted(tasks_dir.glob("*.yaml")):
        if path.name.upper().startswith("README"):
            continue
        subject = f".syllabai/tasks/{path.name}"
        doc = load_yaml(path, report, subject)
        if doc is None:
            continue
        task = doc.get("task") if isinstance(doc, dict) else None
        if not isinstance(task, dict):
            report.warn("T0-STRUCTURE", subject, "no 'task' mapping at top level")
            continue
        stem = path.stem
        tid = str(task.get("id", "") or "")
        if tid:
            task_ids.add(tid)
            if tid != stem and not stem.startswith(tid + "-"):
                report.warn("T1-ID", subject, f"id '{tid}' does not match filename stem '{stem}'")
        else:
            report.warn("T1-ID", subject, "missing task.id")
        status = str(task.get("status", "") or "")
        if status and status not in LEGAL_STATUSES:
            report.warn("T2-STATUS", subject, f"illegal status '{status}'")
        claims = task.get("claims")
        if claims is not None:
            if not isinstance(claims, dict):
                report.warn("T3-CLAIMS", subject, "claims present but not a mapping")
            else:
                bad = [k for k in claims if str(k) not in LEGAL_CLAIM_LABELS]
                if bad:
                    report.warn("T3-CLAIMS", subject,
                                f"claim labels outside the 4-tier vocabulary: {', '.join(map(str, bad))}")
        acceptance = task.get("acceptance")
        if status in {"VERIFYING", "DONE"}:
            if not acceptance:
                report.warn("T4-ACCEPTANCE", subject,
                            f"status {status} but acceptance is empty")
            owner = task.get("owner")
            if not owner:
                report.warn("T5-OWNER", subject, f"status {status} but owner is empty")
        if status == "EXECUTING" and not task.get("owner"):
            report.warn("T5-OWNER", subject, "status EXECUTING but owner is empty")
    return task_ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".", help="repository root (default: cwd)")
    parser.add_argument("--mode", choices=["warn", "strict"], default="warn",
                        help="warn: always exit 0 (phase 1); strict: exit 1 on any finding")
    parser.add_argument("--summary", default=None,
                        help="path to append a GitHub step summary (e.g. $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args()

    root = Path(args.repo_root)
    syllabai = root / ".syllabai"
    report = Report(strict=(args.mode == "strict"), summary_path=args.summary)

    if not syllabai.is_dir():
        report.error("IO", ".syllabai", "coordination directory not found")
        print(report.render())
        report.write_summary()
        return report.exit_code() if args.mode == "strict" else 0

    registry = load_yaml(syllabai / "agent-registry.yaml", report, "agent-registry.yaml") or {}
    locks = load_yaml(syllabai / "locks.yaml", report, "locks.yaml") or {}
    registry = registry if isinstance(registry, dict) else {}
    locks = locks if isinstance(locks, dict) else {}

    known_resources = known_shared_resources(registry, locks)
    lock_policies = {
        str(name): str((spec or {}).get("policy", "") if isinstance(spec, dict) else "")
        for name, spec in (locks.get("resource_classes") or {}).items()
    }
    serialized = {n for n, p in lock_policies.items() if p == "serialized"}

    # Tasks first so lease task-references can resolve.
    task_ids = check_tasks(syllabai / "tasks", report)
    check_locks(locks, report, known_resources, serialized, task_ids)
    check_history(locks, report, task_ids)
    check_registry(registry, report, known_resources, lock_policies)

    print(report.render())
    report.write_summary()
    return report.exit_code()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - last-resort guard, report crisply
        print(f"coordination-guard: internal error: {exc}", file=sys.stderr)
        sys.exit(2)
