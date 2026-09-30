#!/usr/bin/env python3
"""T-C17 Stage B — deterministic clean-and-verify for the fresh 2012-Jan session.

Implements CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md v1.1 (§4 B.0, §5/§6 removals,
§7.1 repairs, §8 artifacts) as a deterministic, anchor-asserted script.

Determinism: all block boundaries are located by unique anchors (asserted); with
TC17_EPOCH_PIN=1 the report's generated_at_utc is pinned so re-runs are
byte-identical. Fail-loud: any missing anchor or checksum mismatch aborts with
nothing written.
"""
import datetime
import hashlib
import json
import os
import sys

SESSION = os.environ.get('TC17_SESSION',
                         '/home/z/my-project/tc17-work/corpus-sandbox/paper 1/2012-Jan')
EPOCH = '1970-01-01T00:00:00Z'
PIN = os.environ.get('TC17_EPOCH_PIN') == '1'
TOOLING = 'syllabai-parser 7b8bcba tools/corpus_ops + tools/glmocr (python twin; Java unavailable in sandbox)'
PROTOCOL = 'CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md v1.1'

EXPECTED_Q_TOTALS = {'1': 10, '2': 8, '3': 13, '4': 8, '5': 11,
                     '6': 14, '7': 9, '8': 10, '9': 18, '10': 8, '11': 11}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def find_exactly(lines, needle, what):
    hits = [i for i, ln in enumerate(lines) if needle in ln]
    if len(hits) != 1:
        raise SystemExit(f'ANCHOR FAIL: {what} expected exactly once, found {len(hits)}')
    return hits[0]


def apply_removals(lines, removals, path_name):
    """removals: list of (op_class, set_of_0based_line_indices). Returns new lines + ledger."""
    ledger = []
    doomed = set()
    for op_class, idxs in removals:
        doomed |= idxs
    out = [ln for i, ln in enumerate(lines) if i not in doomed]
    # blank-line corollary: no glued text — strip leading/trailing blank runs only
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    text = '\n'.join(out) + '\n'
    return text, ledger


def main():
    raw_qp_path = os.path.join(SESSION, 'QP.md')
    raw_ms_path = os.path.join(SESSION, 'MS.md')
    raw_qp = open(raw_qp_path, 'rb').read()
    raw_ms = open(raw_ms_path, 'rb').read()
    qp_sha, ms_sha = sha256_bytes(raw_qp), sha256_bytes(raw_ms)

    # ── B.0 — pre-clean capture, checksum cross-check against MANIFEST first ──
    manifest = json.load(open(os.path.join(SESSION, '..', 'MANIFEST.json')))
    md = manifest['sessions']['2012-Jan']['documents']
    if md['QP']['sha256'] != qp_sha or md['MS']['sha256'] != ms_sha:
        raise SystemExit('B.0 HARD STOP: raw checksums do not match MANIFEST.json')
    batch_manifest = json.load(open('/home/z/my-project/tc17-work/ocr-batch-2012jan/manifest.json'))
    engine = batch_manifest['engine']
    prior_manifest = json.load(open('/home/z/my-project/repos/Past-Papers/paper 1/MANIFEST.json'))
    prior = prior_manifest['sessions']['2012-Jan']['documents']

    qp_lines = raw_qp.decode().splitlines()
    ms_lines = raw_ms.decode().splitlines()

    # witnesses (line numbers are 1-based in the ledger)
    w1 = find_exactly(qp_lines, 'The total mark for this paper is 120.', 'qp printed total witness')
    w2 = find_exactly(qp_lines, 'TOTAL FOR PAPER = 120 MARKS', 'qp printed paper-total line')
    import re
    q_totals = {}
    total_re = re.compile(r'^\(Total for Question (\d{1,2}) = (\d{1,3}) marks\)\s*$')
    for i, ln in enumerate(qp_lines):
        m = total_re.match(ln)
        if m:
            q_totals[m.group(1)] = int(m.group(2))
    if q_totals != EXPECTED_Q_TOTALS:
        raise SystemExit(f'B.0 FAIL: per-question totals {q_totals} != expected {EXPECTED_Q_TOTALS}')
    if sum(q_totals.values()) != 120:
        raise SystemExit('B.0 FAIL: question total sum != printed paper total 120')
    ms_total_lines = [ln for ln in ms_lines if 'otal for paper' in ln.lower()]
    ms_paper_total = None if not ms_total_lines else ms_total_lines

    # identity as printed (asserted from the raw covers)
    id_checks = [
        ('board', 'Edexcel', qp_lines), ('unit', 'Unit: 4CH0', qp_lines),
        ('session', 'Friday 13 January 2012', qp_lines),
        ('ms_session', 'January 2012', ms_lines),
    ]
    identity = {'board': 'Edexcel',
                'qualification': 'International GCSE Chemistry / Science (Double Award)',
                'paper_reference': '4CH0/1C (also 4SC0/1C)',
                'session': 'Friday 13 January 2012 - Morning (QP); January 2012 (MS)'}
    for _, needle, lines in id_checks:
        if not any(needle in ln for ln in lines):
            raise SystemExit(f'B.0 FAIL: identity anchor {needle!r} not found')

    # ── B.1/B.2 — removals by unique anchors ─────────────────────────────────
    # QP block 1..93 = cover + instructions/information/advice + furniture +
    # periodic table + BLANK PAGE + PMT + "Answer ALL questions."; Q1 stem at 95.
    q1 = find_exactly(qp_lines, '1 Salt is soluble in water', 'Q1 stem')
    if q1 != 94:  # 0-based: line 95 1-based
        raise SystemExit(f'ANCHOR FAIL: Q1 stem at {q1}, expected 94')
    answer_all = find_exactly(qp_lines, 'Answer ALL questions.', 'Answer ALL instruction')
    pmt_strays = [i for i, ln in enumerate(qp_lines) if ln.strip() == 'PMT' and i > answer_all]
    if pmt_strays != [280, 677, 812]:
        raise SystemExit(f'ANCHOR FAIL: PMT strays {pmt_strays} != [280, 677, 812]')
    blanks_tail = [i for i, ln in enumerate(qp_lines) if ln.strip() == 'BLANK PAGE' and i > w2]
    if blanks_tail != [843, 845]:
        raise SystemExit(f'ANCHOR FAIL: tail BLANK PAGEs {blanks_tail} != [843, 845]')

    qp_removals = [
        ('cover-instructions-periodic-boilerplate', set(range(0, answer_all + 1))),
        ('page-furniture-pmt', set(pmt_strays)),
        ('blank-page', set(blanks_tail)),
    ]

    # MS: 1..35 = cover + corporate preamble (© Pearson Education Ltd 2012 at 35);
    # identity line 37 KEPT (session-92 precedent); footer 1236..EOF removed.
    copyright_line = find_exactly(ms_lines, '© Pearson Education Ltd 2012', 'ms preamble end')
    if copyright_line != 34:
        raise SystemExit(f'ANCHOR FAIL: ms preamble end at {copyright_line}, expected 34')
    footer_start = find_exactly(ms_lines, 'Further copies of this publication', 'ms footer start')
    if footer_start != 1235:
        raise SystemExit(f'ANCHOR FAIL: ms footer at {footer_start}, expected 1235')
    ms_removals = [
        ('cover-corporate-preamble', set(range(0, copyright_line + 1))),
        ('publications-footer', set(range(footer_start, len(ms_lines)))),
    ]

    clean_qp, _ = apply_removals(qp_lines, qp_removals, 'QP')
    clean_ms, _ = apply_removals(ms_lines, ms_removals, 'MS')

    # ── B.3 — repair pass: assert nothing needs §7.1 fixes ────────────────────
    def grammar_counters(text):
        return {
            'dollarFences': text.count('$$'),
            'tableOpen': text.count('<table'),
            'tableClose': text.count('</table>'),
        }
    gq, gm = grammar_counters(clean_qp), grammar_counters(clean_ms)
    if gq['dollarFences'] % 2 or gm['dollarFences'] % 2:
        raise SystemExit('B.3: unbalanced $$ fences — §7.1.1 fix would be needed')
    if gq['tableOpen'] != gq['tableClose'] or gm['tableOpen'] != gm['tableClose']:
        raise SystemExit('B.3: unbalanced tables — §7.1.2 fix would be needed')

    clean_dir = os.path.join(SESSION, 'clean')
    os.makedirs(clean_dir, exist_ok=True)
    open(os.path.join(clean_dir, 'QP.md'), 'w').write(clean_qp)
    open(os.path.join(clean_dir, 'MS.md'), 'w').write(clean_ms)

    operations = [
        {'op': 'remove-block', 'class': 'cover-instructions-periodic-boilerplate',
         'target': 'QP', 'lines': f'1-{answer_all + 1}',
         'detail': 'cover fields, Instructions/Information/Advice, Turn over/P40126A/'
                   'copyright/barcode furniture, periodic table + key, BLANK PAGE, PMT, '
                   '"Answer ALL questions." (B.0 witnesses captured first)'},
        {'op': 'remove-line', 'class': 'page-furniture-pmt', 'target': 'QP',
         'lines': ', '.join(str(i + 1) for i in pmt_strays), 'detail': '3 stray PMT marks'},
        {'op': 'remove-block', 'class': 'blank-page', 'target': 'QP',
         'lines': ', '.join(str(i + 1) for i in blanks_tail), 'detail': '2 trailing BLANK PAGEs'},
        {'op': 'remove-block', 'class': 'cover-corporate-preamble', 'target': 'MS',
         'lines': f'1-{copyright_line + 1}',
         'detail': 'Mark Scheme cover + Edexcel/Pearson corporate preamble; '
                   'identity line "INTERNATIONAL GCSE CHEMISTRY 4CH0 4SC0 /1C – JANUARY 2012" KEPT'},
        {'op': 'remove-block', 'class': 'publications-footer', 'target': 'MS',
         'lines': f'{footer_start + 1}-{len(ms_lines)}',
         'detail': 'Edexcel Publications order info + corporate footer'},
    ]

    report = {
        'schema': 'clean-report-1.0',
        'session': '2012-Jan',
        'generated_at_utc': EPOCH if PIN else datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'protocol': PROTOCOL,
        'tooling': TOOLING,
        'raw_provenance': {
            'note': 'raw = FRESH full-document OCR parse of the official PDFs '
                    '(operator-directed "parse the pdf version add it"); NOT the 2026-09-11 '
                    'ocr.z.ai website batch recorded in the canonical manifest',
            'source_pdfs': {
                'QP': {'name': 'January 2012 QP - Paper 1C Edexcel Chemistry IGCSE.pdf'},
                'MS': {'name': 'January 2012 MS - Paper 1C Edexcel Chemistry IGCSE.pdf'},
            },
            'engine': engine,
            'batch_manifest': 'ocr-batch-2012jan/manifest.json (sandbox evidence)',
            'supersedes': {
                'prior_raw': {'qp_sha256': prior['QP']['sha256'], 'ms_sha256': prior['MS']['sha256']},
                'prior_execution': 'session-92 T-C17 first execution (protocol machinery VERIFIED, '
                                   'session NOT CLEANED: G2 FAIL 120 vs 98, escalations E-001..E-004)',
                'supersession_reason': 'operator-directed fresh parse recovers the printed total '
                                       'lines the prior OCR lost (Q5=11, Q11=11) and drops the '
                                       'prior in-table OCR artifacts (E-004)',
            },
        },
        'raw': {'qp_sha256': qp_sha, 'ms_sha256': ms_sha},
        'clean': {'qp_sha256': sha256_bytes(clean_qp.encode()),
                  'ms_sha256': sha256_bytes(clean_ms.encode())},
        'captured_totals': {
            'qp_paper_total': 120,
            'qp_paper_total_witnesses': [
                {'line': w1 + 1, 'text': 'The total mark for this paper is 120.'},
                {'line': w2 + 1, 'text': 'TOTAL FOR PAPER = 120 MARKS'},
            ],
            'ms_paper_total': None,
            'ms_paper_total_note': 'absent from the PRINTED mark scheme (same as prior raw); '
                                   'not an escalation — nothing reconstructed',
            'per_question_totals': q_totals,
            'per_question_totals_absent': [],
        },
        'identity_as_printed': identity,
        'operations': operations,
        'repairs': [],
        'escalations': [],
        'observations': [
            {'id': 'N-001', 'kind': 'printed-total-discrepancy',
             'detail': 'the PRINTED mark scheme says "Total 11 marks" for Question 3 while the '
                       'printed QP says "(Total for Question 3 = 13 marks)" and the MS mark '
                       'cells for Q3 sum to 13 — a property of the printed documents, faithfully '
                       'transcribed on both sides; recorded for operator awareness, nothing changed',
             'state': 'informational'},
        ],
        'figures_note': 'fresh parse carries NO image islands (vision engine has no layout/crop '
                        'stage — recorded honestly in the batch manifest); the prior raw\'s 11 '
                        'assets remain in the canonical session folder untouched',
    }
    open(os.path.join(clean_dir, 'clean-report.json'), 'w').write(
        json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print('B.0–B.3 COMPLETE')
    print('clean QP sha256:', report['clean']['qp_sha256'])
    print('clean MS sha256:', report['clean']['ms_sha256'])
    print('operations:', len(operations), '| repairs: 0 | escalations: 0')


if __name__ == '__main__':
    main()
