from datetime import date
from html import escape
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent

DOCS = {
    "main": {
        "md": ROOT / "cfRNA_extraction_OT2_protocol.md",
        "html": ROOT / "cfRNA_extraction_OT2_protocol.html",
        "title": "cfRNA OT2 Protocol",
    },
    "pilot": {
        "md": ROOT / "OT2_PROTOCOL_PILOT_EXPERIMENT.md",
        "html": ROOT / "OT2_PROTOCOL_PILOT_EXPERIMENT.html",
        "title": "OT2_PROTOCOL_PILOT_EXPERIMENT",
    },
}

STYLE = """@page { margin: 0.45in; }
body { font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-size: 9.4pt; line-height: 1.22; color: #111; }
h1 { font-size: 18pt; margin: 0 0 8pt; }
h2 { font-size: 12.8pt; margin: 10pt 0 4pt; border-bottom: 1px solid #ddd; padding-bottom: 2pt; }
h3 { font-size: 10.8pt; margin: 8pt 0 3pt; }
h4 { font-size: 9.8pt; margin: 6pt 0 2pt; }
p { margin: 0 0 4pt; }
ul, ol { margin: 0 0 5pt 17pt; padding: 0; }
li { margin: 1pt 0; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0 6pt; page-break-inside: auto; }
th, td { border: 1px solid #bbb; padding: 2.5pt 3pt; vertical-align: top; }
th { background: #eee; font-weight: 700; }
code { font-family: Menlo, Consolas, monospace; font-size: 8.2pt; background: #f4f4f4; padding: 0 1pt; }
pre { background: #f4f4f4; padding: 5pt; overflow-wrap: break-word; white-space: pre-wrap; }
strong { font-weight: 800; }"""


def update_date(md_path):
    today = date.today().isoformat()
    text = md_path.read_text()
    updated, count = re.subn(r"(?m)^Date:\s+.*$", f"Date: {today}", text, count=1)
    if count == 0:
        raise SystemExit(f"No Date line found in {md_path}")
    if updated != text:
        md_path.write_text(updated)
    return updated


def inline(text):
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def parse_table(lines, start):
    header = [c.strip() for c in lines[start].strip().strip("|").split("|")]
    rows = []
    i = start + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
        i += 1
    out = ["<table><thead><tr>"]
    out.extend(f"<th>{inline(c)}</th>" for c in header)
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        out.extend(f"<td>{inline(c)}</td>" for c in row)
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out), i


def render(lines):
    out = []
    list_type = None
    in_code = False
    code_lines = []
    i = 0

    def close_list():
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    while i < len(lines):
        raw = lines[i].rstrip("\n")
        line = raw.rstrip()

        if line.startswith("```"):
            if in_code:
                out.append("<pre><code>" + escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(raw)
            i += 1
            continue

        if not line:
            close_list()
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[i + 1]):
            close_list()
            table, i = parse_table(lines, i)
            out.append(table)
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        unordered = re.match(r"^-\s+(.+)$", line)
        if ordered or unordered:
            kind = "ol" if ordered else "ul"
            if list_type != kind:
                close_list()
                out.append(f"<{kind}>")
                list_type = kind
            out.append(f"<li>{inline((ordered or unordered).group(1))}</li>")
            i += 1
            continue

        close_list()
        out.append(f"<p>{inline(line)}</p>")
        i += 1

    close_list()
    return "\n".join(out)


def render_doc(name):
    doc = DOCS[name]
    md_text = update_date(doc["md"])
    body = render(md_text.splitlines())
    doc["html"].write_text(
        f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(doc["title"])}</title><style>\n{STYLE}\n</style></head><body>{body}</body></html>\n'
    )
    print(doc["html"])


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "main"
    if target == "all":
        for name in DOCS:
            render_doc(name)
    elif target in DOCS:
        render_doc(target)
    else:
        raise SystemExit(f"Usage: python3 {Path(__file__).name} [main|pilot|all]")
