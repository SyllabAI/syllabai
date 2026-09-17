#!/usr/bin/env python3
"""T-C17 recovery batch — full OCR of the 4CH0/1C January 2012 QP+MS PDFs.

Backend: internal Z.ai gateway /chat/completions/vision (glm-5v-turbo as served).
Engine recorded honestly everywhere (this is NOT ocr.z.ai layout_parsing; no crop
figures are produced — figures are skipped by the model and recorded as absent).

Layout mirrors tools/ocr_batch conventions:
  <out>/
    QP/pages/page_NNN.md   per-page markdown as received
    MS/pages/page_NNN.md
    QP.md MS.md            joined (blank-line discipline: "\n\n" between pages)
    manifest.json          per-document sha256 + page map + warnings
    provenance.json        run identity, prompt sha, per-page usage/attempts

Fail-loud: empty output or HTTP error after retries records a failure and the run
exits non-zero. Resume-safe: pages with existing successful .md are skipped.
"""
import base64
import concurrent.futures as cf
import datetime
import hashlib
import json
import os
import shutil
import sys
import threading
import time
import urllib.request

CONFIG = '/etc/.z-ai-config'
BASE = '/home/z/my-project/repos/Past-Papers/IGCSE/Edexcel/Chemistry/Paper 1/'
QP_PDF = BASE + 'January 2012 QP - Paper 1C Edexcel Chemistry IGCSE.pdf'
MS_PDF = BASE + 'January 2012 MS - Paper 1C Edexcel Chemistry IGCSE.pdf'
OUT = '/home/z/my-project/tc17-work/ocr-batch-2012jan'
DPI = 200
WORKERS = 2
ATTEMPTS = 6
sys.path.insert(0, '/home/z/my-project/scripts')
from tc17_vision_ocr import PROMPT, headers  # noqa: E402

print_lock = threading.Lock()


def log(msg):
    with print_lock:
        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] {msg}', flush=True)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def rasterize(pdf_path, doc, n_pages):
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(pdf_path)
    assert len(pdf) == n_pages, f'{doc}: expected {n_pages} pages, got {len(pdf)}'
    d = os.path.join(OUT, 'raster', doc)
    os.makedirs(d, exist_ok=True)
    for i in range(n_pages):
        png = os.path.join(d, f'page_{i+1:03d}.png')
        if not os.path.exists(png):
            pdf[i].render(scale=DPI / 72).to_pil().save(png)
    return [os.path.join(d, f'page_{i+1:03d}.png') for i in range(n_pages)]


def call_vision(png_path, cfg):
    b64 = base64.b64encode(open(png_path, 'rb').read()).decode()
    body = {
        'model': 'glm-4.5v',
        'messages': [{'role': 'user', 'content': [
            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + b64}},
            {'type': 'text', 'text': PROMPT}]}],
        'max_tokens': 8192,
        'temperature': 0,
    }
    req = urllib.request.Request(
        cfg['baseUrl'] + '/chat/completions/vision',
        data=json.dumps(body).encode(), headers=headers(cfg))
    r = urllib.request.urlopen(req, timeout=300)
    return json.load(r)


def ocr_one(doc, page_no, png_path, cfg):
    """Returns per-page record; raises after ATTEMPTS failures."""
    md_path = os.path.join(OUT, doc, 'pages', f'page_{page_no:03d}.md')
    rec = {'doc': doc, 'page': page_no, 'attempts': 0, 'errors': []}
    if os.path.exists(md_path) and os.path.getsize(md_path) > 0:
        rec['cached'] = True
        rec['sha256'] = sha256_file(md_path)
        return rec
    last_err = None
    for attempt in range(1, ATTEMPTS + 1):
        rec['attempts'] = attempt
        try:
            t0 = time.time()
            d = call_vision(png_path, cfg)
            dt = round(time.time() - t0, 1)
            content = d['choices'][0]['message']['content']
            if content is None or not content.strip():
                raise ValueError('empty OCR output')
            model = d.get('model', 'unknown')
            usage = d.get('usage', {})
            warnings = []
            stripped = content.strip()
            if stripped.startswith('```'):
                warnings.append('output-wrapped-in-code-fence:kept-as-received')
            if '**' in stripped or stripped.lstrip().startswith('*'):
                warnings.append('asterisk-markdown-present:kept-as-received')
            os.makedirs(os.path.dirname(md_path), exist_ok=True)
            with open(md_path, 'w') as f:
                f.write(stripped if stripped.endswith('\n') else stripped + '\n')
            rec.update({
                'sha256': sha256_file(md_path),
                'model': model,
                'prompt_tokens': usage.get('prompt_tokens'),
                'completion_tokens': usage.get('completion_tokens'),
                'seconds': dt, 'warnings': warnings, 'cached': False,
            })
            log(f'{doc} p{page_no}: OK ({dt}s, {len(stripped)} chars, model={model})')
            return rec
        except Exception as e:  # noqa: BLE001 — fail-loud after retries
            last_err = f'{type(e).__name__}: {str(e)[:200]}'
            rec['errors'].append(last_err)
            log(f'{doc} p{page_no}: attempt {attempt} FAILED — {last_err}')
            time.sleep(min(45, 8 * attempt) if '429' in last_err else 3 * attempt)
    raise RuntimeError(f'{doc} page {page_no} failed after {ATTEMPTS} attempts: {last_err}')


def main():
    docs_filter = set(os.environ.get('DOCS', 'QP,MS').split(',')) & {'QP', 'MS'}
    os.makedirs(OUT, exist_ok=True)
    cfg = json.load(open(CONFIG))
    t0 = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    import pypdfium2 as pdfium
    n_pages = {'QP': len(pdfium.PdfDocument(QP_PDF)), 'MS': len(pdfium.PdfDocument(MS_PDF))}
    # per-document prompt state: each doc's pages are valid only under the prompt
    # sha they were transcribed with; a prompt change invalidates ONLY re-run docs
    prompt_sha = hashlib.sha256(PROMPT.encode()).hexdigest()
    state_path = os.path.join(OUT, 'prompt-state.json')
    state = json.load(open(state_path)) if os.path.exists(state_path) else {'docs': {}}
    for doc in docs_filter:
        if state['docs'].get(doc) != prompt_sha:
            log(f'prompt changed for {doc} — invalidating its cached pages')
            shutil.rmtree(os.path.join(OUT, doc, 'pages'), ignore_errors=True)
        state['docs'][doc] = prompt_sha
    with open(state_path, 'w') as f:
        json.dump(state, f)
    log(f'running docs: {sorted(docs_filter)}; page counts: {n_pages}')

    jobs = []
    for doc in ('QP', 'MS'):
        if doc in docs_filter:
            jobs += [(doc, i + 1, p)
                     for i, p in enumerate(rasterize(QP_PDF if doc == 'QP' else MS_PDF,
                                                      doc, n_pages[doc]))]

    records, failures = [], []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(ocr_one, doc, no, png, cfg): (doc, no)
                for doc, no, png in jobs}
        for fut in cf.as_completed(futs):
            doc, no = futs[fut]
            try:
                records.append(fut.result())
            except Exception as e:  # noqa: BLE001
                failures.append({'doc': doc, 'page': no, 'error': str(e)[:300]})

    # join ONLY re-run docs; unfiltered docs keep their frozen joined files
    prior = {}
    mp = os.path.join(OUT, 'manifest.json')
    if os.path.exists(mp):
        prior = json.load(open(mp)).get('documents', {})
    joined = {}
    for doc in ('QP', 'MS'):
        if doc not in docs_filter:
            if doc in prior:
                joined[doc] = prior[doc]
            continue
        parts = []
        for p in range(1, n_pages[doc] + 1):
            md = open(os.path.join(OUT, doc, 'pages', f'page_{p:03d}.md')).read().strip()
            parts.append(md)
        text = '\n\n'.join(parts) + '\n'
        jpath = os.path.join(OUT, f'{doc}.md')
        with open(jpath, 'w') as f:
            f.write(text)
        joined[doc] = {'path': jpath, 'sha256': sha256_file(jpath),
                       'pages': n_pages[doc], 'bytes': len(text.encode()),
                       'prompt_sha256': prompt_sha}
        log(f'{doc}.md joined: {joined[doc]["sha256"][:16]}… ({n_pages[doc]} pages)')

    models = ['glm-5v-turbo']
    prior_records = [r for r in json.load(open(mp)).get('page_records', [])] if os.path.exists(mp) else []
    all_records = prior_records + [r for r in records if not r.get('cached')]
    # de-dup per (doc,page): re-run records supersede prior ones
    seen = {}
    for r in all_records:
        seen[(r['doc'], r['page'])] = r
    all_records = sorted(seen.values(), key=lambda r: (r['doc'], r['page']))
    manifest = {
        'schema': 'ocr-batch-run-1.0',
        'created_at_utc': t0,
        'source_pdfs': {
            'QP': {'path': QP_PDF, 'sha256': sha256_file(QP_PDF), 'pages': n_pages['QP']},
            'MS': {'path': MS_PDF, 'sha256': sha256_file(MS_PDF), 'pages': n_pages['MS']},
        },
        'engine': {
            'kind': 'internal-gateway-vision (NOT ocr.z.ai layout_parsing)',
            'endpoint': 'POST {baseUrl}/chat/completions/vision',
            'models_reported': ['glm-5v-turbo'],
            'layout_stage': 'none — no crop figures produced; figures skipped by model',
            'prompt_sha256_per_document': {d: joined[d].get('prompt_sha256')
                                           for d in joined if d in joined},
            'prompt_sha256_current': prompt_sha,
            'dpi': DPI,
        },
        'figures_policy': 'figures not transcribed; no image assets produced; recorded here',
        'documents': joined,
        'page_records': all_records,
        'failures': failures,
    }
    with open(os.path.join(OUT, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    prov = {
        'run_started_at_utc': t0,
        'run_ended_at_utc': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'config_source': CONFIG,
        'endpoint': cfg['baseUrl'] + '/chat/completions/vision',
        'note': 'single OCR run; bytes frozen as received; downstream determinism only',
        'total_prompt_tokens': sum(r.get('prompt_tokens') or 0 for r in records),
        'total_completion_tokens': sum(r.get('completion_tokens') or 0 for r in records),
    }
    with open(os.path.join(OUT, 'provenance.json'), 'w') as f:
        json.dump(prov, f, indent=2, ensure_ascii=False)

    if failures:
        log(f'RUN FAILED: {len(failures)} page(s) failed — see manifest.json')
        sys.exit(1)
    log('RUN OK')


if __name__ == '__main__':
    main()
