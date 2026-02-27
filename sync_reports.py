#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import html
import re

SRC = Path('/Users/len/.openclaw/workspace/reports/x-daily')
DST = Path('/Users/len/Git/ai-news')
REPORTS_DST = DST / 'reports'


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out = []
    in_ul = False
    in_pre = False

    def close_ul():
        nonlocal in_ul
        if in_ul:
            out.append('</ul>')
            in_ul = False

    for line in lines:
        if line.startswith('```'):
            if not in_pre:
                close_ul()
                out.append('<pre><code>')
                in_pre = True
            else:
                out.append('</code></pre>')
                in_pre = False
            continue

        if in_pre:
            out.append(html.escape(line))
            continue

        if not line.strip():
            close_ul()
            continue

        if line.startswith('# '):
            close_ul(); out.append(f"<h1>{html.escape(line[2:].strip())}</h1>"); continue
        if line.startswith('## '):
            close_ul(); out.append(f"<h2>{html.escape(line[3:].strip())}</h2>"); continue
        if line.startswith('### '):
            close_ul(); out.append(f"<h3>{html.escape(line[4:].strip())}</h3>"); continue
        if line.startswith('> '):
            close_ul(); out.append(f"<blockquote>{html.escape(line[2:].strip())}</blockquote>"); continue
        if line.startswith('- '):
            if not in_ul:
                out.append('<ul>'); in_ul = True
            out.append(f"<li>{html.escape(line[2:].strip())}</li>")
            continue

        close_ul()
        text = html.escape(line)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        out.append(f"<p>{text}</p>")

    close_ul()
    return '\n'.join(out)


def page_template(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{html.escape(title)}</title>
<style>body{{max-width:900px;margin:40px auto;padding:0 16px;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.65}}code,pre{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}pre{{background:#f6f8fa;padding:12px;border-radius:8px;overflow:auto}}blockquote{{border-left:4px solid #ddd;padding-left:12px;color:#555}}a{{text-decoration:none;color:#0b57d0}}</style>
</head><body>
<p><a href=\"../index.html\">← 返回列表</a></p>
{body}
</body></html>"""


def main():
    REPORTS_DST.mkdir(parents=True, exist_ok=True)
    entries = []
    for md in sorted(SRC.glob('*.md')):
        txt = md.read_text(encoding='utf-8')
        title = txt.splitlines()[0].lstrip('# ').strip() if txt.strip() else md.stem
        body = md_to_html(txt)
        out = REPORTS_DST / f"{md.stem}.html"
        out.write_text(page_template(title, body), encoding='utf-8')
        entries.append((md.stem, title, datetime.fromtimestamp(md.stat().st_mtime)))

    entries.sort(reverse=True)
    items = '\n'.join([f'<li><a href="reports/{d}.html">{html.escape(t)}</a> <small>({dt:%Y-%m-%d %H:%M})</small></li>' for d,t,dt in entries])
    index = f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>AI News Daily</title>
<style>body{{max-width:900px;margin:40px auto;padding:0 16px;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.65}}a{{text-decoration:none;color:#0b57d0}}</style></head><body>
<h1>X 日报 HTML 索引</h1>
<p>自动同步自 <code>/Users/len/.openclaw/workspace/reports/x-daily</code></p>
<ul>{items}</ul>
</body></html>"""
    (DST / 'index.html').write_text(index, encoding='utf-8')


if __name__ == '__main__':
    main()
