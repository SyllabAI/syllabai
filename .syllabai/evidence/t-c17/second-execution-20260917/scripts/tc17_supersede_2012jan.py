#!/usr/bin/env python3
"""Apply the operator-directed 2012-Jan raw supersession to a paper-1 corpus dir.

- Replaces 2012-Jan/QP.md + MS.md with the fresh vision-engine parse
- Archives the prior raw as QP.raw-superseded-20260911.md / MS.raw-superseded-20260911.md
- Updates MANIFEST.json additively (v1.1): schema_version, ops_log[], clean{}, documents
- Copies the clean/ subtree (QP.md, MS.md, clean-report.json)
Everything else in the corpus is untouched. Run corpus_ops verify afterwards.
"""
import json
import os
import shutil
import sys

TARGET = sys.argv[1]  # dir containing `paper 1`
SRC = '/home/z/my-project/tc17-work/corpus-sandbox/paper 1/2012-Jan'
OLD_CLONE = '/home/z/my-project/repos/Past-Papers'

paper = os.path.join(TARGET, 'paper 1')
sess = os.path.join(paper, '2012-Jan')
man_path = os.path.join(paper, 'MANIFEST.json')
man = json.load(open(man_path))

new_qp_sha = json.load(open(os.path.join(SRC, '..', 'MANIFEST.json')))['sessions']['2012-Jan']['documents']['QP']['sha256']
new_ms_sha = json.load(open(os.path.join(SRC, '..', 'MANIFEST.json')))['sessions']['2012-Jan']['documents']['MS']['sha256']
old_qp_sha = man['sessions']['2012-Jan']['documents']['QP']['sha256']
old_ms_sha = man['sessions']['2012-Jan']['documents']['MS']['sha256']
report = json.load(open(os.path.join(SRC, 'clean', 'clean-report.json')))

# 1. archive prior raw (idempotent: refuse if already superseded)
for op in man.get('ops_log', []):
    if op.get('batch_id') == 'raw-supersession-2012-Jan-20260917T-chain':
        sys.exit('already superseded — refusing double application')
shutil.copy(os.path.join(sess, 'QP.md'), os.path.join(sess, 'QP.raw-superseded-20260911.md'))
shutil.copy(os.path.join(sess, 'MS.md'), os.path.join(sess, 'MS.raw-superseded-20260911.md'))

# sanity: archived bytes must hash to the recorded prior checksums
import hashlib
for fname, expected in [('QP.raw-superseded-20260911.md', old_qp_sha),
                        ('MS.raw-superseded-20260911.md', old_ms_sha)]:
    got = hashlib.sha256(open(os.path.join(sess, fname), 'rb').read()).hexdigest()
    if got != expected:
        sys.exit(f'ARCHIVE ANCHOR FAIL: {fname} {got} != {expected}')

# 2. replace raw
shutil.copy(os.path.join(SRC, 'QP.md'), os.path.join(sess, 'QP.md'))
shutil.copy(os.path.join(SRC, 'MS.md'), os.path.join(sess, 'MS.md'))

# 3. clean/ subtree (exactly the §8 artifacts; no proposals — zero escalations)
os.makedirs(os.path.join(sess, 'clean'), exist_ok=True)
for f in ['QP.md', 'MS.md', 'clean-report.json']:
    shutil.copy(os.path.join(SRC, 'clean', f), os.path.join(sess, 'clean', f))

# 4. MANIFEST additive update (v1.1)
s = man['sessions']['2012-Jan']
s['documents']['QP'] = {
    'original_name': 'January 2012 QP - Paper 1C Edexcel Chemistry IGCSE.pdf '
                     '(vision-engine conversion batch 2026-09-17)',
    'path': 'QP.md', 'sha256': new_qp_sha,
    'size': os.path.getsize(os.path.join(sess, 'QP.md'))}
s['documents']['MS'] = {
    'original_name': 'January 2012 MS - Paper 1C Edexcel Chemistry IGCSE.pdf '
                     '(vision-engine conversion batch 2026-09-17)',
    'path': 'MS.md', 'sha256': new_ms_sha,
    'size': os.path.getsize(os.path.join(sess, 'MS.md'))}
man.setdefault('schema_version', '1.1')
man.setdefault('ops_log', []).append({
    'batch_id': 'raw-supersession-2012-Jan-20260917T-chain',
    'kind': 'raw-supersession',
    'date_utc': report['generated_at_utc'],
    'operator_directive': '"You can parse the pdf version add it. Make it complete yourself"',
    'reason': 'prior ocr.z.ai-website raw lost the printed total lines for Q5/Q11 and the MS '
              'paper total (session-92 T-C17 execution: G2 FAIL 120 vs 98, escalations '
              'E-001..E-004 awaiting operator); fresh full-document parse of the official PDFs '
              'recovers all printed totals (Q5=11, Q11=11, sum=120) and drops the prior '
              'in-table OCR artifacts',
    'engine': report['raw_provenance']['engine'],
    'prior_raw': {'qp_sha256': old_qp_sha, 'ms_sha256': old_ms_sha,
                  'archived_as': ['QP.raw-superseded-20260911.md', 'MS.raw-superseded-20260911.md'],
                  'assets': '11 image assets retained (referenced by the archived raw)'},
    'new_raw': {'qp_sha256': new_qp_sha, 'ms_sha256': new_ms_sha},
    'clean': {'qp_sha256': report['clean']['qp_sha256'], 'ms_sha256': report['clean']['ms_sha256'],
              'gates': report.get('gate_results', {})},
    'evidence': 'SyllabAI/syllabai .syllabai/evidence/t-c17/ (second-execution files)'})
man.setdefault('clean', {})['2012-Jan'] = {
    'qp_sha256': report['clean']['qp_sha256'],
    'ms_sha256': report['clean']['ms_sha256'],
    'report_ref': 'clean/clean-report.json'}

json.dump(man, open(man_path, 'w'), indent=2, ensure_ascii=False)
print('supersession applied to', paper)
print('new raw QP:', new_qp_sha[:16], '| MS:', new_ms_sha[:16])
print('clean QP:', report['clean']['qp_sha256'][:16], '| MS:', report['clean']['ms_sha256'][:16])
