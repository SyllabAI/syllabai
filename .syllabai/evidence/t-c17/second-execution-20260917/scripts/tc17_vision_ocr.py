#!/usr/bin/env python3
"""T-C17 recovery batch: vision-endpoint OCR probe.

Sends one rasterized PDF page to the internal gateway /chat/completions/vision
and prints the returned markdown. Engine recorded honestly (see provenance).
"""
import base64
import json
import sys
import urllib.request

CONFIG = '/etc/.z-ai-config'


def headers(cfg):
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + cfg['apiKey'],
        'X-Z-AI-From': 'Z',
        'X-Chat-Id': cfg.get('chatId', ''),
        'X-User-Id': cfg.get('userId', ''),
        'X-Token': cfg.get('token', ''),
    }


PROMPT = (
    "Transcribe this scanned exam paper page to Markdown. Rules:\n"
    "1. Output ONLY the transcription, no commentary.\n"
    "2. Keep printed question numbers exactly as printed at line start "
    "(e.g. '1 Salt is soluble...' or '2 (a) ...').\n"
    "3. Keep part labels exactly as printed at line start: (a) (b) (i) (ii) etc.\n"
    "4. Keep printed mark annotations exactly as printed and as their own line where "
    "the print shows them separated, e.g. a line containing exactly (6) or a line "
    "containing exactly (Total for Question 5 = 11 marks) or TOTAL FOR PAPER = 120 MARKS.\n"
    "5. Transcribe word boxes / tables as HTML <table border=\"1\">...</table>, preserving "
    "rowspan/colspan attributes where the printed table merges cells.\n"
    "6. Transcribe chemical formulae and equations in LaTeX math with $...$ inline and $$...$$ display.\n"
    "7. Where a diagram or figure appears, output nothing for it (skip it silently).\n"
    "8. OMIT page furniture only: page numbers, barcodes, 'PMT' marks, centre/candidate "
    "number grids, and the black corner squares.\n"
    "9. NEVER use asterisk-based bold or italic markdown (** or *): transcribe bold or "
    "italic printed text as plain text with no asterisks. Never begin a line with '*'.\n"
    "10. Preserve dotted answer lines as printed (e.g. '...................').\n"
    "11. Keep the printed spelling exactly; do not correct, join or split words.\n"
    "12. For mark-scheme tables preserve the printed column structure exactly: one cell "
    "for the question number, one for the part letter, one for the roman sub-part, one "
    "for the mark-point code (M1, M2, MP1 etc) ALONE, one for the answer text, one for "
    "the notes, one for the marks value. NEVER merge a mark-point code into the answer "
    "cell; NEVER merge the marks value into another cell. Each mark-point row keeps its "
    "own code cell and its own marks cell.\n"
)


def ocr_page(png_path, cfg):
    b64 = base64.b64encode(open(png_path, 'rb').read()).decode()
    body = {
        'model': 'glm-4.5v',
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + b64}},
                {'type': 'text', 'text': PROMPT},
            ],
        }],
        'max_tokens': 8192,
        'temperature': 0,
    }
    req = urllib.request.Request(
        cfg['baseUrl'] + '/chat/completions/vision',
        data=json.dumps(body).encode(), headers=headers(cfg))
    r = urllib.request.urlopen(req, timeout=300)
    d = json.load(r)
    return d


def main():
    png = sys.argv[1]
    cfg = json.load(open(CONFIG))
    d = ocr_page(png, cfg)
    msg = d.get('choices', [{}])[0].get('message', {})
    print('== model:', d.get('model'))
    print('== usage:', d.get('usage'))
    print('== content ==')
    print(msg.get('content', ''))


if __name__ == '__main__':
    main()
