#!/usr/bin/env python3
"""embed-bridge-v2 CI runner (records repo bench/inputs/bridge-v2/).

Embeds the 300 bridge preview chunks (engine pdflane-atoms/1.2.0, header-stamped
eval text = the exact bytes core's ChunkingService will embed at ingest) plus 10
topical probe queries, through the production embedding semantics:
gemini-embedding-001, RETRIEVAL_DOCUMENT (chunks) / RETRIEVAL_QUERY (probes),
outputDimensionality=768, one embedContent call per text.

Inputs (same directory): records.jsonl (300 records with ref/contentSha256/content),
probes.json (10 hand-written topical probes with target keywords).
Outputs (BRIDGE_OUT): embeddings_chunks.jsonl {ref,model,v[768] sorted by ref},
embeddings_probes.jsonl {pid,model,v[768]}, manifest.json (echoes input SHA256s +
counts + semantics), SHA256SUMS.

Stdlib only. Paced (default 500 ms) with exponential backoff on 429/5xx.
"""
import hashlib
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

MODEL = os.environ.get("EMBED_MODEL", "gemini-embedding-001")
DIM = 768
PACE = float(os.environ.get("EMBED_MIN_INTERVAL_MS", "500")) / 1000.0
KEY = os.environ.get("SYLLABAI_EMBEDDING_GEMINI_API_KEY") or \
    os.environ.get("SYLLABAI_EMBEDDING_GEMINI_API_KEYS", "").split(",")[0]
assert KEY, "no Gemini key in env"
HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path(os.environ.get("BRIDGE_OUT", "embed-out-bridge-v2"))
OUT.mkdir(parents=True, exist_ok=True)


def embed_one(text, task_type):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:embedContent"
    body = json.dumps({
        "model": f"models/{MODEL}",
        "content": {"parts": [{"text": text}]},
        "taskType": task_type,
        "outputDimensionality": DIM,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json", "x-goog-api-key": KEY}, method="POST")
    last = None
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.loads(r.read().decode())
            vals = resp.get("embedding", {}).get("values")
            if not vals or len(vals) != DIM:
                raise RuntimeError(f"bad dims {len(vals) if vals else 0}")
            return vals
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode()[:150]}"
            if e.code == 429 or "quota" in last.lower():
                time.sleep(min(2 ** attempt * 5, 180)); continue
            if e.code in (500, 503):
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise RuntimeError(last)
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            time.sleep(min(2 ** attempt * 3, 60))
    raise RuntimeError(f"embed failed after retries: {last}")


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    records = [json.loads(l) for l in (HERE / "records.jsonl").read_text().splitlines() if l]
    probes = json.loads((HERE / "probes.json").read_text())
    assert len(records) == 300, f"expected 300 records, got {len(records)}"
    assert all(r["contentSha256"] == hashlib.sha256(r["content"].encode("utf-8")).hexdigest()
               for r in records), "contentSha256 mismatch — input tampered"

    chunks, n = [], 0
    for r in records:
        v = embed_one(r["content"], "RETRIEVAL_DOCUMENT")
        chunks.append({"ref": r["ref"], "model": MODEL, "v": v})
        n += 1
        if n % 25 == 0 or n == len(records):
            print(f"chunks {n}/{len(records)}", flush=True)
        time.sleep(PACE)
    chunks.sort(key=lambda c: c["ref"])
    (OUT / "embeddings_chunks.jsonl").write_text(
        "".join(json.dumps(c) + "\n" for c in chunks))

    probes_out = []
    for p in probes["probes"]:
        v = embed_one(p["query"], "RETRIEVAL_QUERY")
        probes_out.append({"pid": p["id"], "model": MODEL, "v": v})
        time.sleep(PACE)
    (OUT / "embeddings_probes.jsonl").write_text(
        "".join(json.dumps(p) + "\n" for p in probes_out))

    manifest = {
        "artifact": "embed-bridge-v2",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL,
        "dimension": DIM,
        "semantics": {
            "chunks": "RETRIEVAL_DOCUMENT, one embedContent per text, outputDimensionality=768",
            "probes": "RETRIEVAL_QUERY, one embedContent per text, outputDimensionality=768",
            "note": "production GeminiEmbeddingProvider semantics (Spring AI GoogleGenAi "
                    "RETRIEVAL_DOCUMENT/RETRIEVAL_QUERY, dims 768); transport differs "
                    "(single-call vs batched) — values verified transport-independent by "
                    "the rev1 G2 float4-identity gate; rev2 re-verified post-ingest by "
                    "DB-vs-artifact vector diff",
        },
        "inputs": {
            "records.jsonl": {"records": len(records), "sha256": sha256(HERE / "records.jsonl")},
            "probes.json": {"probes": len(probes["probes"]), "sha256": sha256(HERE / "probes.json")},
        },
        "counts": {"chunks": len(chunks), "probes": len(probes_out)},
        "upstream": "engine pdflane-atoms/1.2.0 bridge release (parser PR #6, f0b6f81); "
                    "header projection port verified against ChunkingServiceTest grammar",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")

    sums = []
    for f in ("embeddings_chunks.jsonl", "embeddings_probes.jsonl", "manifest.json"):
        h = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
        sums.append(f"{h}  {f}")
    (OUT / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print("EMBED-BRIDGE-V2 COMPLETE:", len(chunks), "chunks +", len(probes_out), "probes")


if __name__ == "__main__":
    sys.exit(main())
