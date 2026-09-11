#!/usr/bin/env python3
"""SyllabAI Google Sheet dashboard updater.

Gathers repo metadata, default-branch commits, Google Drive Sync run health
(GitHub API) and Drive folder statistics (Drive API), then writes them to a
Google Sheet with tabs: Overview, Commits, Sync Runs, Info.

Runs inside GitHub Actions (SyllabAI/syllabai). Stdlib only.

Env:
  GH_TOKEN      GitHub PAT (repo read + Actions read across SyllabAI repos)
  OAUTH_BLOCK   the GDRIVE_RCLONE_OAUTH secret ([gdrive] rclone config block)
  SHEET_ID      target spreadsheet id (repo variable GDRIVE_SHEET_ID)
  FOLDER_ID     SyllabAI-GitHub Drive folder id (repo variable GDRIVE_FOLDER_ID)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

GH_ORG = os.environ.get("GH_ORG", "SyllabAI")
SHEET_ID = os.environ.get("SHEET_ID", "")
GH_TOKEN = os.environ.get("GH_TOKEN", "")
OAUTH_BLOCK = os.environ.get("OAUTH_BLOCK", "")
FOLDER_ID = os.environ.get("FOLDER_ID", "")
MAX_COMMIT_ROWS = 5000
MAX_DRIVE_FILES = 5000
INC_PAGES = 2     # commit pages (100/page) per repo per normal run
FULL_PAGES = 20   # when the Commits tab starts empty (first run)

ROLES = {
    "syllabai": "Master project pack — spec, ADRs, decisions, trackers",
    "syllabai-core": "Backend modular monolith — Java 25 · Spring Boot 4.1 · Render",
    "syllabai-web": "Frontend — Next.js 16 · React 19 · Vercel",
    "syllabai-parser": "Content pipeline — offline document parsing (Java/Python)",
    "syllabai-pastpapers": "Canonical QP/MS corpus (official assessment materials)",
    "Past-Papers": "Edexcel IGCSE Chemistry QP/MS + GLM-OCR markdown",
    "syllabai-resources": "Revision notes, textbooks, specification corpus",
}


def die(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def http(method, url, data=None, headers=None, timeout=60, retries=2):
    hdrs = dict(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        hdrs.setdefault("Content-Type", "application/json")
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode()
                if raw.strip() and not raw.lstrip().startswith(("{", "[")):
                    die(f"{method} {url} -> non-JSON response (blocked?): {raw[:150]}")
                return r.status, (json.loads(raw) if raw.strip() else {})
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            die(f"{method} {url} -> {e}")


def gh(path, params=None):
    url = f"https://api.github.com{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    st, data = http("GET", url, headers={
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "syllabai-dashboard"})
    if st != 200:
        die(f"GitHub GET {path} -> {st}: {json.dumps(data)[:200]}")
    return data


def parse_oauth_block(text):
    cid = sec = tok = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("client_id"):
            cid = s.split("=", 1)[1].strip()
        elif s.startswith("client_secret"):
            sec = s.split("=", 1)[1].strip()
        elif s.startswith("token = "):
            tok = json.loads(s.split("= ", 1)[1].strip())
    if not (cid and sec and tok and tok.get("refresh_token")):
        die("OAUTH_BLOCK parse failed — is GDRIVE_RCLONE_OAUTH set?")
    return cid, sec, tok["refresh_token"]


def google_token(cid, sec, rtok):
    d = urllib.parse.urlencode({"client_id": cid, "client_secret": sec,
                                "refresh_token": rtok, "grant_type": "refresh_token"}).encode()
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    "https://oauth2.googleapis.com/token", data=d, method="POST"), timeout=30) as r:
                return json.loads(r.read().decode())["access_token"]
        except Exception as e:
            if attempt == 2:
                die(f"Google token refresh failed: {e}")
            time.sleep(2 ** (attempt + 1))


def gdrive_get(path, token):
    return http("GET", f"https://www.googleapis.com/drive/v3{path}",
                headers={"Authorization": f"Bearer {token}"})


def sheet_clear(tab, token):
    rng = urllib.parse.quote(f"{tab}!A1:Z10000", safe="")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{rng}:clear"
    st, data = http("POST", url, headers={"Authorization": f"Bearer {token}"})
    if st != 200:
        die(f"sheet_clear {tab} -> {st}: {json.dumps(data)[:200]}")


def sheet_put(tab, rows, token):
    # single-range write form (values/{range}?valueInputOption=...) gets served an HTML
    # block page from datacenter IPs - use values:batchUpdate instead (verified working)
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values:batchUpdate"
    payload = {"valueInputOption": "USER_ENTERED",
               "data": [{"range": f"{tab}!A1", "values": rows}]}
    st, data = http("POST", url, data=payload, headers={"Authorization": f"Bearer {token}"})
    if st not in (200, 201):
        die(f"sheet_put {tab} -> {st}: {json.dumps(data)[:200]}")


def sheet_get(tab, token, cols="A2:E"):
    rng = urllib.parse.quote(f"{tab}!{cols}", safe="")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{rng}"
    st, data = http("GET", url, headers={"Authorization": f"Bearer {token}"})
    return data.get("values", []) if st == 200 else []


def safe(v, maxlen=500):
    s = str(v).replace("\r", " ").replace("\n", " | ")
    if s.startswith(("=", "+", "@")):
        s = "'" + s
    return s[:maxlen]


def iso_utc(s):
    return (s or "").replace("T", " ").replace("Z", "")[:19]


def sha_of_cell(cell):
    """Extract full sha from =HYPERLINK(\"...commit/<sha>\",...) or plain text."""
    c = str(cell)
    if c.startswith("=HYPERLINK("):
        parts = c.split('"')
        if len(parts) > 1:
            return parts[1].rstrip("/").split("/")[-1]
    return c.strip()


def drive_children(folder_id, token):
    out, page_token = [], None
    while True:
        params = {"q": f"'{folder_id}' in parents and trashed=false",
                  "fields": "nextPageToken, files(id,name,size,mimeType)", "pageSize": 1000}
        if page_token:
            params["pageToken"] = page_token
        st, data = gdrive_get("/files?" + urllib.parse.urlencode(params), token)
        if st != 200:
            break
        out += data.get("files", [])
        page_token = data.get("nextPageToken")
        if not page_token or len(out) >= MAX_DRIVE_FILES:
            break
    return out


def drive_stats(folder_id, token):
    files, size, stack = 0, 0, [folder_id]
    while stack and files < MAX_DRIVE_FILES:
        fid = stack.pop()
        for it in drive_children(fid, token):
            if it.get("mimeType") == "application/vnd.google-apps.folder":
                stack.append(it["id"])
            else:
                files += 1
                size += int(it.get("size", 0))
    return files, round(size / 1e6, 1)


def duration_min(run):
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        start = datetime.strptime(run.get("run_started_at") or run["created_at"], fmt)
        end = datetime.strptime(run.get("updated_at"), fmt)
        return round((end - start).total_seconds() / 60, 1)
    except Exception:
        return ""


def main():
    for name in ("SHEET_ID", "GH_TOKEN", "OAUTH_BLOCK"):
        if not os.environ.get(name):
            die(f"missing env {name}")

    cid, sec, rtok = parse_oauth_block(OAUTH_BLOCK)
    gtoken = google_token(cid, sec, rtok)
    print("[OK] Google token refreshed")

    # /user/repos returns public + private for the token's own account;
    # /users/{user}/repos returns public only
    repos = gh("/user/repos", {"per_page": 100, "sort": "pushed",
                               "visibility": "all", "affiliation": "owner"})
    print(f"[OK] {len(repos)} repos fetched")

    # ---- commits: merge new into existing log ----
    existing = sheet_get("Commits", gtoken)
    seen = {sha_of_cell(r[3]) for r in existing if len(r) > 3}
    full_mode = len(existing) < 50
    pages = FULL_PAGES if full_mode else INC_PAGES
    new_rows = []
    for repo in repos:
        full = repo["full_name"]
        for page in range(1, pages + 1):
            batch = gh(f"/repos/{full}/commits", {"per_page": 100, "page": page})
            if not batch:
                break
            for c in batch:
                sha = c["sha"]
                if sha in seen:
                    continue
                seen.add(sha)
                author = (c.get("commit", {}).get("author", {}) or {}).get("name", "unknown")
                msg = c["commit"]["message"].splitlines()[0]
                new_rows.append([iso_utc(c["commit"]["author"]["date"]), repo["name"],
                                 safe(author, 80), f'=HYPERLINK("{c["html_url"]}","{sha[:7]}")',
                                 safe(msg, 300)])
            if len(batch) < 100:
                break
    all_rows = new_rows + [list(r) for r in existing]
    all_rows.sort(key=lambda r: str(r[0]), reverse=True)
    all_rows = all_rows[:MAX_COMMIT_ROWS]
    print(f"[OK] commits: {len(existing)} existing, +{len(new_rows)} new -> {len(all_rows)} rows")

    # ---- sync runs (last 25 per repo) + last-sync map ----
    run_rows, last_sync = [], {}
    for repo in repos:
        full = repo["full_name"]
        data = gh(f"/repos/{full}/actions/runs", {"per_page": 30})
        runs = [r for r in data.get("workflow_runs", []) if r.get("name") == "Google Drive Sync"]
        for r in runs[:25]:
            run_rows.append([repo["name"], r["status"], r.get("conclusion") or "-",
                             r.get("head_branch", ""), r.get("event", ""),
                             iso_utc(r.get("run_started_at") or r["created_at"]),
                             duration_min(r), f'=HYPERLINK("{r["html_url"]}","open")'])
        if runs:
            r0 = runs[0]
            last_sync[full] = {
                "status": r0["status"] if r0["status"] != "completed" else (r0.get("conclusion") or "-"),
                "time": iso_utc(r0.get("run_started_at") or r0["created_at"]),
                "url": r0["html_url"],
            }
    print(f"[OK] sync runs: {len(run_rows)} rows")

    # ---- drive stats per repo folder ----
    drive_map = {}
    if FOLDER_ID:
        for it in drive_children(FOLDER_ID, gtoken):
            if it.get("mimeType") == "application/vnd.google-apps.folder":
                drive_map[it["name"]] = it["id"]
    else:
        print("[WARN] FOLDER_ID not set — skipping Drive stats")

    # ---- overview ----
    ov_rows = []
    for repo in sorted(repos, key=lambda r: r["name"]):
        full, name = repo["full_name"], repo["name"]
        lc = gh(f"/repos/{full}/commits", {"per_page": 1})
        lc = lc[0] if isinstance(lc, list) and lc else None
        ds = drive_stats(drive_map[name], gtoken) if name in drive_map else ("", "")
        role = ROLES.get(name) or repo.get("description") or ""
        lc_time = lc_msg = ""
        if lc:
            lc_time = iso_utc(lc["commit"]["author"]["date"])
            lc_msg = safe(lc["commit"]["message"].splitlines()[0], 200)
        s = last_sync.get(full, {})
        ov_rows.append([
            name, f'=HYPERLINK("{repo["html_url"]}","open")', safe(role, 150),
            "private" if repo["private"] else "public",
            repo.get("language") or "-", repo.get("default_branch") or "main",
            lc_time, lc_msg,
            s.get("status", "no runs yet"),
            f'=HYPERLINK("{s["url"]}","open")' if s.get("url") else "-",
            s.get("time", "-"), ds[0], ds[1],
        ])
    print("[OK] overview rows built")

    # ---- write everything ----
    sheet_clear("Overview", gtoken)
    sheet_put("Overview", [["Repo", "Link", "Role", "Visibility", "Language", "Branch",
                            "Last commit (UTC)", "Last commit message", "Last sync status",
                            "Last sync run", "Last sync time (UTC)", "Drive files",
                            "Drive size (MB)"]] + ov_rows, gtoken)
    sheet_clear("Sync Runs", gtoken)
    sheet_put("Sync Runs", [["Repo", "Status", "Conclusion", "Branch", "Event",
                             "Started (UTC)", "Duration (min)", "Run link"]] + run_rows, gtoken)
    sheet_clear("Commits", gtoken)
    sheet_put("Commits", [["Time (UTC)", "Repo", "Author", "SHA", "Message"]] + all_rows, gtoken)
    print(f"[DONE] dashboard refreshed — {len(ov_rows)} repos, {len(run_rows)} runs, {len(all_rows)} commits")


if __name__ == "__main__":
    main()
