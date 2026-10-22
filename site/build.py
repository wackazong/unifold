#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["markdown>=3.4", "pyyaml>=6"]
# ///
"""Build the static site for https://unifold.md into site/_out/.

    python3 site/build.py            # build
    python3 site/build.py --serve    # build, then serve on http://localhost:8000
    python3 site/build.py --check    # build, then check links, HTML and page weight

Everything is derived from README.md, docs/references/*.md and the
skill. Nothing is converted by hand: change the Markdown and run this again.
"""
from __future__ import annotations

import hashlib
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration. REPO_URL is a placeholder until the repository has its home.
# --------------------------------------------------------------------------
REPO_URL = "https://github.com/unifold-spec/unifold"
REPO_BRANCH = "main"
SITE_URL = "https://unifold.md"
DOMAIN = "unifold.md"

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
REF = ROOT / "docs" / "references"
SKILL = ROOT / "docs" / "skills" / "unifold" / "SKILL.md"
CONVERT_SKILL = ROOT / "docs" / "skills" / "unifold-convert" / "SKILL.md"
OUT = SITE / "_out"
DIAGRAMS = SITE / "diagrams"      # pre-rendered Mermaid, committed, keyed by content hash
STATIC = SITE / "static"          # copied as it is (og.png)

EXPL = ROOT / "docs" / "explanation"
TUT = ROOT / "docs" / "tutorials"

# slug (the URL), source file, name in the navigation, one line for indexes, kind
CHAPTERS = [
    ("spec", REF / "spec.md", "The standard", "The whole standard on one page: manifest, wiring, documents, what a checker guarantees.", "Standard"),
    ("documents", REF / "documents.md", "Documents", "The files of a unit, the four kinds of knowledge, README.md, the generated AGENTS.md, the explanation files, where a file may point.", "Reference"),
    ("writing", REF / "writing.md", "Writing", "How each document is written: context items, decisions, references, skills, tutorials, explanation files, the review checklist.", "Reference"),
    ("agents", REF / "agents.md", "Agents", "How coding agents find and use unifold, per agent.", "Reference"),
    ("tool", REF / "tool.md", "Tool", "The reference tool: commands, output, hooks, continuous integration.", "Reference"),
    ("tool-json", REF / "tool-json.md", "Tool JSON", "The JSON that the reference tool prints.", "Reference"),
    ("rules", REF / "rules.md", "Rules", "Every finding the reference tool reports.", "Reference"),
    ("requirements", EXPL / "requirements.md", "Requirements", "What the standard must achieve, for which repositories it fits, where the value is.", "Explanation"),
    ("reasoning", EXPL / "reasoning.md", "Reasoning", "Where the parts come from, what unifold adds, the design ideas behind it, Diátaxis and arc42.", "Explanation"),
    ("wiring", EXPL / "wiring.md", "Wiring", "Wiring in practice: names, passing needs up, several children on one provider, alternatives, adapters, services.", "Explanation"),
    ("invariants", EXPL / "invariants.md", "Invariants", "What is true of the standard, the skills and the tool at every moment.", "Explanation"),
    ("risks", EXPL / "risks.md", "Risks", "Risks and known limits of the standard.", "Explanation"),
    ("first-map", TUT / "first-map.md", "Your first map", "A tutorial: a root manifest, two units, a connection, the first diagram, documents for one unit.", "Tutorial"),
]
SLUG_OF = {src.resolve(): slug for slug, src, _, _, _ in CHAPTERS}
# old addresses that still get a page
REDIRECTS = {"guide": "/", "adopting": "/first-map", "design": "/reasoning"}

MERMAID_CONFIG = '{"theme":"neutral","htmlLabels":false,"flowchart":{"htmlLabels":false},"fontFamily":"system-ui, sans-serif"}'

WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"warning: {msg}", file=sys.stderr)


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


try:
    import markdown
    import yaml
except ImportError as exc:  # pragma: no cover
    die(f"{exc.name} is missing. Install with: python3 -m pip install markdown pyyaml  (or: uv run site/build.py)")

esc = html.escape
CUR = ' aria-current="page"'

# --------------------------------------------------------------------------
# Marks
# --------------------------------------------------------------------------
# The mark: one sheet with a crease. Left panel lies flat, right panel lifts.
LOGO = ('<svg class="mark" viewBox="0 0 32 32" width="{s}" height="{s}" aria-hidden="true">'
        '<path class="m1" d="M3 9l12-4v22L3 23z"/><path class="m2" d="M17 5l12 4v14l-12 4z"/></svg>')
FAVICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
           "<path fill='#0b6b5c' d='M3 9l12-4v22L3 23z'/><path fill='#5cc4ae' d='M17 5l12 4v14l-12 4z'/></svg>")
FAVICON_URI = "data:image/svg+xml," + FAVICON.replace("#", "%23").replace("<", "%3C").replace(">", "%3E")


# --------------------------------------------------------------------------
# Markdown helpers
# --------------------------------------------------------------------------
FENCE = re.compile(r"^(`{3,}|~{3,})\s*([\w+-]*)\s*$")


def split_fences(text: str) -> list[tuple]:
    """Split Markdown into ("md", text) and ("code", lang, body) at top-level fences."""
    out: list[tuple] = []
    buf: list[str] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m:
            mark, lang = m.group(1), m.group(2)
            j = i + 1
            while j < len(lines) and not re.match(rf"^{re.escape(mark[0])}{{{len(mark)},}}\s*$", lines[j]):
                j += 1
            if buf:
                out.append(("md", "\n".join(buf)))
                buf = []
            out.append(("code", lang, "\n".join(lines[i + 1:j])))
            i = j + 1
        else:
            buf.append(lines[i])
            i += 1
    if buf:
        out.append(("md", "\n".join(buf)))
    return out


def highlight(code: str, lang: str, mark_wiring: bool = False, mark_names=()) -> str:
    """A very small highlighter: YAML keys and comments, console prompts and findings. With
    mark_wiring, the wiring lines and the needs and capabilities they name are marked."""
    out = []
    in_wiring = False
    block = entry = ""
    for line in code.split("\n"):
        e = esc(line, quote=False)
        if lang in ("yaml", "yml"):
            is_wiring_entry = in_wiring and line.startswith((" ", "\t")) and line.strip()
            if re.match(r"^\S", line):
                in_wiring = line.startswith("wiring:")
                block = line.split(":", 1)[0]
            if block in ("needs", "capabilities") and re.match(r"^  \S", line):
                entry = line.strip().split(":", 1)[0]
            named = block in ("needs", "capabilities") and line.startswith("  ") and entry in mark_names
            m = re.match(r"^(.*?)((?:^|\s)#.*)$", e)
            body, comment = (m.group(1), m.group(2)) if m else (e, "")
            body = re.sub(r"^(\s*(?:- )?)([^\s:#][^:#]*?)(:)(\s|$)", r'\1<span class="k">\2</span>\3\4', body)
            e = body + (f'<span class="c">{comment}</span>' if comment else "")
            if mark_wiring and (is_wiring_entry or named):
                e = f'<span class="hl">{e}</span>'
        elif lang in ("console", "text", "sh", "bash", "shell"):
            if lang == "console" and e.startswith("$ "):
                e = f'<span class="c">$</span> <span class="cmd">{e[2:]}</span>'
            elif re.match(r"^error\b", e):
                e = re.sub(r"^(error)(\s+\S+)?", r'<span class="err">\1\2</span>', e)
            elif re.match(r"^warn\b", e):
                e = re.sub(r"^(warn)(\s+\S+)?", r'<span class="wrn">\1\2</span>', e)
            elif lang in ("sh", "bash", "shell"):
                e = re.sub(r"(^|\s)(#.*)$", r'\1<span class="c">\2</span>', e)
        out.append(e)
    return "\n".join(out)


def code_block(code: str, lang: str, mark_wiring: bool = False, mark_names=()) -> str:
    cls = f' class="language-{esc(lang)}"' if lang else ""
    return f"<pre><code{cls}>{highlight(code, lang, mark_wiring, mark_names)}\n</code></pre>"


# ---- Mermaid ---------------------------------------------------------------
def find_mmdc() -> tuple[str | None, str | None]:
    """mmdc from $MMDC, site/node_modules or PATH; puppeteer config from $MMDC_PUPPETEER_CONFIG."""
    cands = [os.environ.get("MMDC"), str(SITE / "node_modules" / ".bin" / "mmdc"), shutil.which("mmdc")]
    exe = next((c for c in cands if c and Path(c).exists()), None)
    return exe, os.environ.get("MMDC_PUPPETEER_CONFIG")


USED_DIAGRAMS: set[str] = set()


def clean_svg(svg: str) -> str:
    svg = svg.strip()
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    if 'class="flowchart"' in svg[:400]:
        # The page's stylesheet draws flowcharts, so that they follow light and dark.
        svg = re.sub(r"<style>.*?</style>", "", svg, count=1, flags=re.S)
    m = re.search(r"max-width:\s*([\d.]+)px", svg[:400])
    width = f"max-width:{m.group(1)}px" if m else ""
    svg = re.sub(r'(<svg[^>]*?) style="[^"]*"', rf'\1 style="{width}"', svg, count=1)
    return svg


def render_mermaid(src: str) -> str:
    """Inline SVG from site/diagrams/<hash>.svg; rendered with mmdc if the file is missing
    and mmdc is there; otherwise the Mermaid source as a code block."""
    src = src.strip() + "\n"
    key = hashlib.sha256((MERMAID_CONFIG + "\n" + src).encode()).hexdigest()[:16]
    cached = DIAGRAMS / f"{key}.svg"
    if not cached.exists():
        exe, pp = find_mmdc()
        if exe:
            with tempfile.TemporaryDirectory() as tmp:
                t = Path(tmp)
                (t / "in.mmd").write_text(src, encoding="utf-8")
                (t / "config.json").write_text(MERMAID_CONFIG, encoding="utf-8")
                cmd = [exe, "-i", str(t / "in.mmd"), "-o", str(t / "out.svg"), "-c", str(t / "config.json"),
                       "-b", "transparent", "-I", f"d{key}", "-q"]
                if pp:
                    cmd += ["-p", pp]
                r = subprocess.run(cmd, capture_output=True, text=True)
                if r.returncode == 0 and (t / "out.svg").exists():
                    DIAGRAMS.mkdir(exist_ok=True)
                    cached.write_text(clean_svg((t / "out.svg").read_text(encoding="utf-8")) + "\n", encoding="utf-8")
                    print(f"rendered diagram {cached.relative_to(ROOT)} (commit it)")
                else:
                    warn(f"mmdc failed for diagram {key}: {(r.stderr or r.stdout).strip()[:300]}")
    if cached.exists():
        USED_DIAGRAMS.add(cached.name)
        svg = cached.read_text(encoding="utf-8").strip()
        return (f'<figure class="diagram">{svg}'
                f'<details><summary>Mermaid source</summary>{code_block(src.rstrip(), "mermaid")}</details></figure>')
    warn(f"no pre-rendered diagram site/diagrams/{key}.svg and no mmdc: showing the Mermaid source instead")
    return f'<figure class="diagram diagram-src">{code_block(src.rstrip(), "mermaid")}</figure>'


# ---- Links -------------------------------------------------------------------
def rewrite_href(href: str, base: Path, version: str) -> str:
    """Turn a link that is relative to a Markdown file of the repository into a link of the site."""
    if re.match(r"^([a-z][a-z0-9+.-]*:|#|//)", href, re.I):
        return href
    path, _, frag = href.partition("#")
    frag = "#" + frag if frag else ""
    target = Path(os.path.normpath(base / path))
    try:
        rel = target.relative_to(ROOT)
    except ValueError:
        warn(f"link leaves the repository: {href}")
        return href
    if target.resolve() in SLUG_OF:
        return f"/{SLUG_OF[target.resolve()]}{frag}"
    if target == REF / "unifold.schema.json":
        return f"/{version}/unifold.schema.json"
    if target.name in ("LICENSE-MIT", "LICENSE-APACHE"):
        return f"/{target.name}.txt"
    if target == SKILL:
        return "/skill/SKILL.md"
    if target == CONVERT_SKILL:
        return "/skill/unifold-convert/SKILL.md"
    if not target.exists():
        warn(f"link to a file that does not exist: {href} (from {base.relative_to(ROOT) or '.'})")
    kind = "tree" if target.is_dir() else "blob"
    return f"{REPO_URL}/{kind}/{REPO_BRANCH}/{rel.as_posix()}{frag}"


def render_md(text: str, base: Path, version: str, permalinks: bool = True) -> tuple[str, list]:
    """Markdown to HTML: Mermaid pre-rendered, code highlighted, tables wrapped, links rewritten."""
    parts, blocks = [], []
    for seg in split_fences(text):
        if seg[0] == "md":
            parts.append(seg[1])
        else:
            _, lang, body = seg
            blocks.append(render_mermaid(body) if lang == "mermaid" else code_block(body, lang))
            parts.append(f"\n\nUNIFOLDBLOCK{len(blocks) - 1}X\n\n")
    md = markdown.Markdown(
        extensions=["tables", "toc", "sane_lists"],
        extension_configs={"toc": {"permalink": "#" if permalinks else False, "permalink_title": "Link to this section",
                                   "permalink_class": "anchor"}},
        output_format="html",
    )
    out = md.convert("".join(parts))
    out = re.sub(r"<p>UNIFOLDBLOCK(\d+)X</p>", lambda m: blocks[int(m.group(1))], out)
    out = re.sub(r"UNIFOLDBLOCK(\d+)X", lambda m: blocks[int(m.group(1))], out)  # inside a list item
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    out = re.sub(r'href="([^"]*)"', lambda m: f'href="{esc(rewrite_href(html.unescape(m.group(1)), base, version))}"', out)
    out = re.sub(r'<a href="(https?://(?!unifold\.md)[^"]*)"', r'<a rel="noopener" href="\1"', out)
    return out, getattr(md, "toc_tokens", [])


# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------
def page(*, title: str, description: str, path: str, body: str, css_href: str, version: str,
         current: str = "", body_class: str = "", noindex: bool = False) -> str:
    nav = [("spec", "Standard"), ("documents", "Documents"), ("tool", "Tool"), ("first-map", "First map")]
    links = "".join(
        f'<a href="/{s}"{CUR if s == current else ""}>{n}</a>' for s, n in nav)
    url = SITE_URL + path
    og_image = f'<meta property="og:image" content="{SITE_URL}/og.png">\n<meta name="twitter:card" content="summary_large_image">' \
        if (STATIC / "og.png").exists() else '<meta name="twitter:card" content="summary">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{esc(url)}">'}
<meta property="og:type" content="website">
<meta property="og:site_name" content="unifold">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
{og_image}
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{FAVICON_URI}">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<link rel="stylesheet" href="{css_href}">
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="brand" href="/">{LOGO.format(s=24)}<span>unifold</span></a>
<span class="draft" title="This is a draft. It is not stable.">{esc(version)} draft</span>
<nav aria-label="Site">{links}<a class="gh" href="{REPO_URL}" rel="noopener" aria-label="unifold on GitHub">{icon("github", "icon sm")}<span>GitHub</span></a></nav>
</div></header>
{body}
<footer class="bottom"><div class="wrap">
<div class="foot-brand"><a class="brand" href="/">{LOGO.format(s=22)}<span>unifold</span></a>
<p>Architecture as code: a map kept in the folders and checked against the code. Draft {esc(version)}.</p></div>
<nav class="foot-cols" aria-label="Footer">
<div><h2>Standard</h2><a href="/spec">The standard</a><a href="/documents">Documents</a><a href="/writing">Writing</a><a href="/{esc(version)}/unifold.schema.json">JSON Schema</a></div>
<div><h2>Tool</h2><a href="/tool">Commands</a><a href="/rules">Rules</a><a href="/tool-json">JSON output</a><a href="/first-map">Your first map</a></div>
<div><h2>Agents</h2><a href="/agents">How agents use it</a><a href="/skill/SKILL.md">The skill</a><a href="/skill/unifold-convert/SKILL.md">The convert skill</a><a href="/llms.txt">llms.txt</a></div>
</nav>
<p class="fine">The text, the skills and the tool are licensed under <a href="/LICENSE-MIT.txt">MIT</a> or <a href="/LICENSE-APACHE.txt">Apache-2.0</a>, at your option. No scripts, no trackers, no fonts from elsewhere.</p>
</div></footer>
</body>
</html>
"""


def toc_html(tokens: list) -> str:
    items = []
    for t in tokens:
        for c in ([t] if t["level"] == 2 else t.get("children", [])):
            if c["level"] == 2:
                items.append(f'<li><a href="#{esc(c["id"])}">{esc(html.unescape(c["name"]))}</a></li>')
    return "<ol>" + "".join(items) + "</ol>" if items else ""


def chapter_page(slug: str, src: Path, text: str, css_href: str, version: str) -> str:
    body, tokens = render_md(text, src.parent, version)
    m = re.search(r"^#\s+(.+)$", text, re.M)
    h1 = re.sub(r"[`*]", "", m.group(1)).strip() if m else slug
    title = h1 if "unifold" in h1.lower() else f"{h1} | unifold"
    desc = next(d for s, _, _, d, _ in CHAPTERS if s == slug)
    chapters, kind_shown = "", None
    for s, _, n, _, kind in CHAPTERS:
        if kind != kind_shown:
            chapters += f'<li class="kind">{esc(kind)}</li>'
            kind_shown = kind
        chapters += (f'<li><a href="/{s}"{CUR if s == slug else ""}>{esc(n)}</a>'
                     f'{toc_html(tokens) if s == slug else ""}</li>')
    toc = toc_html(tokens)
    main = f"""<div class="wrap doc">
<aside class="side">
<details class="toc-small"><summary>On this page</summary>{toc}</details>
<nav class="chapters" aria-label="Chapters"><ul>{chapters}</ul></nav>
</aside>
<main id="main" class="prose">
{body}
<p class="source">This page as <a href="/{slug}.md">plain Markdown</a>, and its
<a href="{REPO_URL}/blob/{REPO_BRANCH}/{src.relative_to(ROOT).as_posix()}" rel="noopener">source on GitHub</a>.</p>
</main>
</div>"""
    return page(title=title, description=desc, path=f"/{slug}", body=main, css_href=css_href,
                version=version, current=slug if slug in ("spec", "documents", "tool", "first-map") else "")


# --------------------------------------------------------------------------
# Landing page, composed from README.md
# --------------------------------------------------------------------------
def inline_md(text: str, version: str) -> str:
    out, _ = render_md(text, ROOT, version, permalinks=False)
    return out


def strip_p(fragment: str) -> str:
    """The inner HTML of a single paragraph."""
    return re.sub(r"^<p>(.*)</p>$", r"\1", fragment.strip(), flags=re.S)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# Small line icons, drawn on a 24 grid; they take the colour of the text.
ICONS = {
    "standard": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>',
    "skills": '<path d="M12 3l2.2 5.3L20 9l-4.4 3.7L17 18.5 12 15.6 7 18.5l1.4-5.8L4 9l5.8-.7z"/>',
    "tool": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 10l3 2-3 2M12 15h5"/>',
    "people": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-3.6 3.6-5.5 7-5.5s6.2 1.9 7 5.5"/>',
    "agents": '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 4v4M9.5 13h.01M14.5 13h.01M2 13v2M22 13v2"/>',
    "file": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/>',
    "folder": '<path d="M3 6h6l2 2h10v11H3z"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "github": '<path d="M12 2.5a9.5 9.5 0 0 0-3 18.5c.5.1.7-.2.7-.5v-1.7c-2.7.6-3.3-1.2-3.3-1.2-.4-1.1-1-1.4-1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.1-.2-4.4-1.1-4.4-4.8 0-1 .4-1.9 1-2.6-.1-.3-.4-1.2.1-2.6 0 0 .8-.3 2.6 1a9 9 0 0 1 4.8 0c1.8-1.3 2.6-1 2.6-1 .5 1.4.2 2.3.1 2.6.6.7 1 1.6 1 2.6 0 3.7-2.3 4.6-4.4 4.8.3.3.6.9.6 1.8v2.7c0 .3.2.6.7.5A9.5 9.5 0 0 0 12 2.5z"/>',
}


def icon(name: str, cls: str = "icon") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def icon_for(heading: str) -> str:
    h = heading.lower()
    for key in ("standard", "skill", "tool", "people", "agent"):
        if key in h:
            return {"skill": "skills", "agent": "agents"}.get(key, key)
    return "file"


def wiring_diagram(manifests: list[tuple[str, dict]]) -> str:
    """An SVG of the connections that the root manifest wires, drawn as the generated
    component diagram draws them: the framing unit, its children, an arrow from need to provider."""
    root = next((m for _, m in manifests if isinstance(m.get("wiring"), dict)), None)
    if root is None:
        return ""
    summaries = {label.split("/")[0]: m.get("summary", "") for label, m in manifests if "/" in label}
    units, edges = [], []
    for key, value in root["wiring"].items():
        if not (isinstance(value, str) and "." in key and "." in value):
            continue
        (src, need), dst = key.rsplit(".", 1), value.rsplit(".", 1)[0]
        for u in (src, dst):
            if u not in units:
                units.append(u)
        edges.append((src, dst, need))
    if not units:
        return ""
    w, h, gap, pad, top = 184, 64, 120, 28, 52
    width = pad * 2 + len(units) * w + (len(units) - 1) * gap
    height = top + h + pad + 8
    x = {u: pad + i * (w + gap) for i, u in enumerate(units)}
    y = top
    out = [f'<svg class="wiring" viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="{esc(root.get("name", "root"))}: ' +
           esc(", ".join(f"{s} needs {n} from {d}" for s, d, n in edges)) + '">',
           '<defs><marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="head"/></marker></defs>',
           f'<rect class="frame" x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14"/>',
           f'<text class="frame-name" x="{pad - 6}" y="32">{esc(str(root.get("name", "root")))}</text>',
           f'<text class="frame-summary" x="{width - pad + 6}" y="32" text-anchor="end">'
           f'{esc(str(root.get("summary", "")))}</text>']
    for u in units:
        out.append(f'<rect class="box" x="{x[u]}" y="{y}" width="{w}" height="{h}" rx="10"/>'
                   f'<text class="box-name" x="{x[u] + w / 2}" y="{y + 27}" text-anchor="middle">{esc(u)}</text>'
                   f'<text class="box-summary" x="{x[u] + w / 2}" y="{y + 46}" text-anchor="middle">'
                   f'{esc(str(summaries.get(u, ""))[:30])}</text>')
    for src, dst, need in edges:
        forward = x[src] < x[dst]
        x1 = x[src] + (w if forward else 0)
        x2 = x[dst] + (0 if forward else w)
        mid, ly = (x1 + x2) / 2, y + h / 2
        out.append(f'<path class="edge" d="M{x1 + (4 if forward else -4)} {ly}H{x2 + (-4 if forward else 4)}" '
                   f'marker-end="url(#arrowhead)"/>'
                   f'<text class="edge-label" x="{mid}" y="{ly - 10}" text-anchor="middle">{esc(need)}</text>')
    out.append("</svg>")
    return "".join(out)


def terminal(code: str, command: str, title: str = "") -> str:
    lines = [f'<span class="prompt">$</span> <span class="cmd">{esc(command)}</span>']
    for line in code.rstrip("\n").split("\n"):
        e = esc(line, quote=False)
        e = re.sub(r"^(error)(\s+\S+)", r'<span class="err">\1\2</span>', e)
        e = re.sub(r"^(warn)(\s+\S+)", r'<span class="wrn">\1\2</span>', e)
        e = re.sub(r"^(\s+)(fix:)", r'\1<span class="fix">\2</span>', e)
        e = re.sub(r"`([^`]+)`", r'<span class="tick">\1</span>', e)
        lines.append(f'<span class="line">{e}</span>')
    return (f'<figure class="card terminal"><figcaption><span class="dots" aria-hidden="true"><i></i><i></i><i></i>'
            f'</span><span>{esc(title or command)}</span></figcaption><pre><code>{"".join(lines)}</code></pre></figure>')


def parse_sections(text: str) -> list[tuple[str, str]]:
    """(heading, body) for every ## section."""
    out = []
    for sec in re.split(r"(?m)^(?=## )", text):
        m = re.match(r"## (.+)\n", sec)
        if m:
            out.append((m.group(1).strip(), sec[m.end():].strip()))
    return out


def table_rows(md: str) -> list[list[str]]:
    rows = [r for r in md.splitlines() if r.startswith("|")]
    out = []
    for r in rows[2:]:
        out.append([c.strip() for c in r.strip().strip("|").split("|")])
    return out


def subsections(md: str) -> list[tuple[str, str]]:
    out = []
    for sec in re.split(r"(?m)^(?=### )", md):
        m = re.match(r"### (.+)\n", sec)
        if m:
            out.append((m.group(1).strip().strip("`"), sec[m.end():].strip()))
    return out


def section_shell(sid: str, heading: str, inner: str, cls: str = "", rail: bool = False) -> str:
    head = f'<h2>{esc(heading)}</h2>'
    if rail:
        return (f'<section class="band rail {cls}" id="{sid}"><div class="wrap"><div class="rail-head">{head}</div>'
                f'<div class="rail-body">{inner}</div></div></section>')
    return f'<section class="band {cls}" id="{sid}"><div class="wrap">{head}{inner}</div></section>'


def landing(readme: str, explorers: list[tuple[str, str]], css_href: str, version: str) -> str:
    m = re.match(r"^#\s+(.+)\n", readme)
    title = m.group(1).strip() if m else "unifold"
    pre, _, rest = (readme[m.end():] if m else readme).partition("\n## ")
    sections = parse_sections("## " + rest) if rest else []

    # --- the first screen: the bold lead sentence is the promise, the blockquote the tagline
    tagline, lead, lede = "", "", []
    for para in (p.strip() for p in re.split(r"\n\s*\n", pre) if p.strip()):
        if para.startswith(">"):
            tagline = re.sub(r"(?m)^>\s?", "", para).strip()
            continue
        bold = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", para, re.S)
        if bold and not lead:
            lead = bold.group(1).strip()
            para = bold.group(2)
        if para:
            lede.append(para)
    promise = lead or tagline or title
    words = promise.rstrip(".").rsplit(" ", 1)
    h1 = (f'{esc(words[0])} <span class="grad">{esc(words[1])}</span>{"." if promise.endswith(".") else ""}'
          if len(words) == 2 else esc(promise))
    eyebrow = title.split(":", 1)[1].strip() if ":" in title else "An open standard"
    eyebrow = eyebrow[:1].upper() + eyebrow[1:]

    # --- How it works: the manifests become the folded sheet, the text block the terminal
    how = next(((h, b) for h, b in sections if h.lower().startswith("how it works")), None)
    panels, manifests, term, prose = [], [], "", []
    if how:
        for seg in split_fences(how[1]):
            if seg[0] == "md":
                if seg[1].strip():
                    prose.append(seg[1].strip())
                continue
            _, lang, body = seg
            if lang in ("yaml", "yml"):
                first, _, tail = body.partition("\n")
                label = first.lstrip("# ").strip() if first.startswith("#") else ""
                body = tail if label else body
                try:
                    data = yaml.safe_load(body) or {}
                except yaml.YAMLError:
                    data = {}
                manifests.append((label, data))
                panels.append((label, body, data))
            elif not term:
                term = body
    names = set()
    for _, data in manifests:
        for key in (data.get("wiring") or {}) if isinstance(data, dict) else {}:
            names.add(key.rsplit(".", 1)[-1])
    sheet = []
    for label, body, data in panels:
        role = "connects" if "wiring" in data else "provides" if "capabilities" in data else "needs" if "needs" in data else ""
        file_name, _, note = label.partition(" ")
        sheet.append(f'<figure class="panel"><figcaption>{icon("file")}<code>{esc(file_name)}</code>'
                     f'<span class="note">{esc(note)}</span>'
                     f'{f"<span class={chr(34)}role {role}{chr(34)}>{role}</span>" if role else ""}</figcaption>'
                     f'{code_block(body.rstrip(), "yaml", mark_wiring=True, mark_names=names)}</figure>')

    facts = []
    rules_md = REF / "rules.md"
    if rules_md.exists():
        n = len(re.findall(r"(?m)^\| <a id=", rules_md.read_text(encoding="utf-8")))
        facts.append(f"{n} rules, each with a fix")
    facts.append(f"The standard in {len((REF / 'spec.md').read_text(encoding='utf-8').splitlines())} lines")
    facts.append("Agent Skills included")
    hero = f"""<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<p class="eyebrow"><span class="dot" aria-hidden="true"></span>{esc(eyebrow)} <span class="sep">·</span> draft {esc(version)}</p>
<h1>{h1}</h1>
{f'<p class="tagline">{strip_p(inline_md(tagline, version))}</p>' if tagline else ''}
<div class="lede">{inline_md(chr(10).join(lede), version)}</div>
<p class="actions"><a class="button primary" href="/spec">Read the standard {icon("arrow", "icon sm")}</a>
<a class="button" href="/first-map">Your first map</a>
<a class="button ghost" href="{REPO_URL}" rel="noopener">{icon("github", "icon sm")} GitHub</a></p>
<ul class="facts">{"".join(f"<li>{esc(f)}</li>" for f in facts)}</ul>
</div>
<div class="sheet" role="group" aria-label="Three manifests">{''.join(sheet)}</div>
</div></section>"""

    blocks = [hero]
    if how:
        diagram = wiring_diagram(manifests)
        root_name = next((str(m.get("name")) for _, m in manifests if m.get("name")), "")
        term = terminal(term, "unifold check", f"~/{root_name}" if root_name else "") if term else ""
        right = term + (f'<figure class="card diagram-card"><figcaption>{icon("file")}<code>docs/diagrams/component.md</code>'
                        f'<span class="role generated">generated</span></figcaption>{diagram}</figure>' if diagram else "")
        body = "".join(inline_md(p, version) for p in prose)
        blocks.append(f'<section class="band how" id="{slug(how[0])}"><div class="wrap how-grid">'
                      f'<div class="how-copy"><h2>{esc(how[0])}</h2><div class="prose">{body}</div></div>'
                      f'<div class="how-figures">{right}</div></div></section>')

    rest_sections = [(h, b) for h, b in sections if not h.lower().startswith("how it works")]
    i = 0
    while i < len(rest_sections):
        heading, body = rest_sections[i]
        low, sid = heading.lower(), slug(heading)
        nxt = rest_sections[i + 1] if i + 1 < len(rest_sections) else None
        if low == "why":
            paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
            first, _, more = paras[0].partition(". ") if paras else ("", "", "")
            paras = ([first + ".", more] if more else paras[:1]) + paras[1:]
            inner = "".join(f'<p{" class=" + chr(34) + "statement" + chr(34) if k == 0 else ""}>{strip_p(inline_md(p, version))}</p>'
                            for k, p in enumerate(paras))
            blocks.append(section_shell(sid, heading, inner, "why", rail=True))
        elif low.startswith("what a unit has") and table_rows(body):
            rows = []
            for name, what in (r[:2] for r in table_rows(body) if len(r) >= 2):
                plain = name.strip("`")
                generated = what.lower().startswith("generated")
                what = re.sub(r"^Generated:\s*", "", what)
                what = what[:1].upper() + what[1:]
                rows.append(f'<li>{icon("folder" if plain.endswith("/") else "file")}<code>{esc(plain)}</code>'
                            f'{"<span class=" + chr(34) + "role generated" + chr(34) + ">generated</span>" if generated else ""}'
                            f'<span class="what">{strip_p(inline_md(what, version))}</span></li>')
            intro = re.split(r"(?m)^\|", body, maxsplit=1)[0].strip()
            inner = (inline_md(intro, version) if intro else "") + \
                f'<div class="card explorer"><p class="explorer-head">{icon("folder")}<code>&lt;unit&gt;/</code></p>' \
                f'<ul>{"".join(rows)}</ul></div>'
            blocks.append(section_shell(sid, heading, inner, "anatomy", rail=True))
        elif low.startswith("how people") and nxt and nxt[0].lower().startswith("how agents"):
            cards = "".join(
                f'<article class="card feature" id="{slug(h)}">{icon(icon_for(h), "icon lg")}<h3>{esc(h)}</h3>'
                f'{inline_md(b, version)}</article>' for h, b in (rest_sections[i], nxt))
            blocks.append(f'<section class="band readers"><div class="wrap"><div class="pair">{cards}</div></div></section>')
            i += 1
        elif low == "questions":
            items = []
            for p in (p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()):
                q = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", p, re.S)
                if q:
                    items.append(f'<details><summary><span>{strip_p(inline_md(q.group(1), version))}</span></summary>'
                                 f'<div class="answer">{inline_md(q.group(2), version)}</div></details>')
                else:
                    items.append(inline_md(p, version))
            blocks.append(section_shell(sid, heading, f'<div class="faq">{"".join(items)}</div>', "questions", rail=True))
        elif low == "capabilities" and subsections(body):
            intro = re.split(r"(?m)^### ", body, maxsplit=1)[0].strip()
            cards = "".join(
                f'<article class="card feature">{icon(icon_for(h), "icon lg")}<h3>{esc(h)}</h3>{inline_md(b, version)}</article>'
                for h, b in subsections(body))
            inner = (f'<p class="section-lede">{strip_p(inline_md(intro, version))}</p>' if intro else "") + \
                f'<div class="trio">{cards}</div>'
            blocks.append(section_shell(sid, heading, inner, "capabilities"))
        elif low == "needs" and nxt and nxt[0].lower() == "commands":
            needs = "".join(f'<p><strong>{esc(h)}.</strong> {strip_p(inline_md(b, version))}</p>' for h, b in subsections(body)) \
                or inline_md(body, version)
            cmd = render_md(nxt[1], ROOT, version, permalinks=False)[0]
            inner = f'<div class="run">{cmd}<div class="needs"><h3>{esc(heading)}</h3>{needs}</div></div>'
            blocks.append(section_shell(slug(nxt[0]), nxt[0], inner, "commands", rail=True))
            i += 1
        elif low == "read next" and table_rows(body):
            cards = []
            for row in table_rows(body):
                if len(row) < 2:
                    continue
                parts = [p.strip() for p in row[1].split(";" if ";" in row[1] else ",") if p.strip()]
                items = "".join(f"<li>{strip_p(inline_md(p, version))}</li>" for p in parts)
                maps = ""
                if row[0].lower().startswith("example") and explorers:
                    maps = "<p>Click through their maps: " + ", ".join(
                        f'<a href="/examples/{esc(n)}/">{esc(n)}</a>' for n, _ in explorers) + ".</p>"
                cards.append(f'<article class="card index{" accent" if maps else ""}">'
                             f'<h3>{strip_p(inline_md(row[0], version))}</h3><ul>{items}</ul>{maps}</article>')
            cards.append(f'<article class="card index"><h3>For agents</h3><ul><li><a href="/skill/SKILL.md">The skill</a></li>'
                         f'<li><a href="/llms.txt">llms.txt</a></li><li><a href="/{esc(version)}/unifold.schema.json">JSON Schema</a></li></ul>'
                         f'<p>Every chapter is also plain Markdown, for example <code>/spec.md</code>.</p></article>')
            blocks.append(section_shell(sid, heading, f'<div class="index-grid">{"".join(cards)}</div>', "read-next"))
        else:
            inner, _ = render_md(body, ROOT, version, permalinks=False)
            cls = "closing" if i == len(rest_sections) - 1 else ""
            blocks.append(section_shell(sid, heading, f'<div class="prose">{inner}</div>', cls, rail=True))
        i += 1

    main = f'<main id="main">{"".join(blocks)}</main>'
    description = (promise + " " + (tagline or "")).strip() + \
        " A draft open standard for repository architecture, checked against the code, for people and coding agents."
    return page(title=f"unifold: {eyebrow.lower()}", description=description,
                path="/", body=main, css_href=css_href, version=version, body_class="home")


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def build() -> None:
    schema = REF / "unifold.schema.json"
    if not schema.exists():
        die(f"{schema.relative_to(ROOT)} is missing. The site serves it at /<version>/unifold.schema.json; "
            "the build cannot continue without it.")
    for need in [ROOT / "README.md", SKILL, CONVERT_SKILL, SITE / "style.css"] + [src for _, src, _, _, _ in CHAPTERS]:
        if not need.exists():
            die(f"{need.relative_to(ROOT)} is missing.")

    version = "0.1"
    for name in ("unifold.yaml",):
        f = ROOT / name
        if f.exists():
            version = str((yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("unifold", version))
    front = re.match(r"^---\n(.*?)\n---\n", SKILL.read_text(encoding="utf-8"), re.S)
    skill_meta = yaml.safe_load(front.group(1)) if front else {}
    front = re.match(r"^---\n(.*?)\n---\n", CONVERT_SKILL.read_text(encoding="utf-8"), re.S)
    convert_meta = yaml.safe_load(front.group(1)) if front else {}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    css = (SITE / "style.css").read_text(encoding="utf-8")
    css_href = f"/style.css?v={hashlib.sha256(css.encode()).hexdigest()[:8]}"
    (OUT / "style.css").write_text(css, encoding="utf-8")

    # explorers: every unifold.html below examples/
    explorers = []
    for f in sorted((ROOT / "examples").rglob("unifold.html")) if (ROOT / "examples").exists() else []:
        name = f.parent.name
        dest = OUT / "examples" / name
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, dest / "index.html")
        t = re.search(r"<title>(.*?)</title>", f.read_text(encoding="utf-8", errors="replace"), re.S)
        title = re.sub(r"\s*[·|-]\s*unifold\s*$", "", html.unescape(t.group(1)).strip()) if t else name
        explorers.append((name, title))
    if not explorers:
        warn("no examples/**/unifold.html found: the site has no explorer pages")

    # chapters, as HTML at /slug (file slug.html) and as Markdown at /slug.md
    for slug, src, _, _, _ in CHAPTERS:
        text = src.read_text(encoding="utf-8")
        (OUT / f"{slug}.html").write_text(chapter_page(slug, src, text, css_href, version), encoding="utf-8")
        (OUT / f"{slug}.md").write_text(text, encoding="utf-8")
    for old, new in REDIRECTS.items():
        (OUT / f"{old}.html").write_text(
            f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>'
            f'<meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="{SITE_URL}{new}">'
            f'</head><body><p>This page moved to <a href="{new}">{SITE_URL}{new}</a>.</p></body></html>\n',
            encoding="utf-8")

    (OUT / "index.html").write_text(
        landing((ROOT / "README.md").read_text(encoding="utf-8"), explorers, css_href, version), encoding="utf-8")

    # machine-readable files
    (OUT / version).mkdir()
    shutil.copyfile(schema, OUT / version / "unifold.schema.json")
    (OUT / "skill").mkdir()
    shutil.copyfile(SKILL, OUT / "skill" / "SKILL.md")
    (OUT / "skill" / "unifold-convert").mkdir()
    shutil.copyfile(CONVERT_SKILL, OUT / "skill" / "unifold-convert" / "SKILL.md")
    for lic in ("LICENSE-MIT", "LICENSE-APACHE"):
        if (ROOT / lic).exists():
            shutil.copyfile(ROOT / lic, OUT / f"{lic}.txt")
        else:
            die(f"{lic} is missing.")

    llms = [
        "# unifold", "",
        f"> unifold {version} (draft) is an open standard for writing down how the parts of a repository depend on "
        "each other. A folder becomes a unit by getting a `unifold.yaml` that lists what it provides and what it "
        "needs; the unit above connects each need to a provider; a checker compares this with the code and "
        "generates the diagrams.", "",
        "All pages below are plain Markdown. The same pages exist as HTML without the `.md` ending.", "",
        "## Standard", "",
        f"- [unifold {version}: the standard]({SITE_URL}/spec.md): {CHAPTERS[0][3]}",
        f"- [JSON Schema of the manifest]({SITE_URL}/{version}/unifold.schema.json): For validating `unifold.yaml`.",
    ]
    for kind in ("Reference", "Explanation", "Tutorial"):
        llms += ["", f"## {kind}", ""]
        llms += [f"- [{n}]({SITE_URL}/{s}.md): {d}" for s, _, n, d, k in CHAPTERS if k == kind]
    llms += ["", "## Agents", "",
             f"- [The unifold skill]({SITE_URL}/skill/SKILL.md): {str(skill_meta.get('description', 'The Agent Skill.')).split('. ')[0]}.",
             f"- [The unifold-convert skill]({SITE_URL}/skill/unifold-convert/SKILL.md): {str(convert_meta.get('description', 'Convert a repository to unifold.')).split('. ')[0]}.",
             "", "## Optional", "",
             f"- [Repository]({REPO_URL}): The standard, the skill, the reference tool and the examples."]
    llms += [f"- [Example: {n}]({SITE_URL}/examples/{n}/): HTML explorer of the example's map." for n, _ in explorers]
    (OUT / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")

    # hosting files
    (OUT / "CNAME").write_text(DOMAIN + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "favicon.svg").write_text(FAVICON + "\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    urls = ["/"] + [f"/{s}" for s, _, _, _, _ in CHAPTERS] + [f"/examples/{n}/" for n, _ in explorers]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    if STATIC.exists():
        for f in STATIC.iterdir():
            if f.is_file():
                shutil.copyfile(f, OUT / f.name)
    nf = f"""<main id="main" class="wrap prose notfound">
<h1>This page does not exist</h1>
<p>The address may be mistyped, or the page has moved while the standard is a draft.</p>
<ul><li><a href="/">Start page</a></li><li><a href="/spec">The standard</a></li><li><a href="/first-map">Your first map</a></li></ul>
</main>"""
    (OUT / "404.html").write_text(
        page(title="Page not found | unifold", description="This page does not exist.", path="/404", body=nf,
             css_href=css_href, version=version, noindex=True), encoding="utf-8")

    if DIAGRAMS.exists():
        for f in sorted(DIAGRAMS.glob("*.svg")):
            if f.name not in USED_DIAGRAMS:
                print(f"note: {f.relative_to(ROOT)} is no longer used; delete it")
    n = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"built {n} files in {OUT.relative_to(ROOT)}/ ({len(WARNINGS)} warning(s))")


# --------------------------------------------------------------------------
# Checks: internal links, well-formed HTML, weight of the start page
# --------------------------------------------------------------------------
def resolve(url_path: str) -> Path | None:
    """The file GitHub Pages serves for a path, or None."""
    p = url_path.split("#")[0].split("?")[0]
    f = OUT / p.lstrip("/")
    if p.endswith("/"):
        return f / "index.html" if (f / "index.html").exists() else None
    if f.is_file():
        return f
    if f.with_name(f.name + ".html").is_file():
        return f.with_name(f.name + ".html")
    return None


def check() -> int:
    from html.parser import HTMLParser
    void = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
    problems: list[str] = []
    n_links = 0

    class P(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.stack: list[str] = []
            self.refs: list[str] = []
            self.ids: set[str] = set()
            self.errors: list[str] = []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if "id" in a:
                if a["id"] in self.ids:
                    self.errors.append(f"duplicate id '{a['id']}'")
                self.ids.add(a["id"])
            for k in ("href", "src"):
                if a.get(k):
                    self.refs.append(a[k])
            if tag not in void:
                self.stack.append(tag)

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if tag not in void:
                self.stack.pop()

        def handle_endtag(self, tag):
            if tag in void:
                return
            if not self.stack or self.stack[-1] != tag:
                self.errors.append(f"line {self.getpos()[0]}: </{tag}> closes <{self.stack[-1] if self.stack else 'nothing'}>")
                if tag in self.stack:
                    while self.stack.pop() != tag:
                        pass
            else:
                self.stack.pop()

    own = [p for p in OUT.rglob("*.html") if "examples" not in p.relative_to(OUT).parts]
    parsed = {}
    for f in own:
        p = P()
        p.feed(f.read_text(encoding="utf-8"))
        p.close()
        if p.stack:
            p.errors.append(f"unclosed: {p.stack}")
        problems += [f"{f.relative_to(OUT)}: {e}" for e in p.errors]
        parsed[f] = p
    for f, p in parsed.items():
        here = "/" + f.relative_to(OUT).as_posix()
        for ref in p.refs:
            if re.match(r"^(https?:|mailto:|data:)", ref):
                if ref.startswith(SITE_URL):
                    ref = ref[len(SITE_URL):] or "/"
                else:
                    continue
            n_links += 1
            path, _, frag = ref.partition("#")
            if not path:
                target = f
            else:
                if not path.startswith("/"):
                    path = os.path.normpath(os.path.join(os.path.dirname(here), path))
                target = resolve(path)
                if target is None:
                    problems.append(f"{f.relative_to(OUT)}: broken link {ref}")
                    continue
            if frag and target in parsed and frag not in parsed[target].ids:
                problems.append(f"{f.relative_to(OUT)}: no anchor #{frag} in {target.relative_to(OUT)}")
    # links inside llms.txt and the sitemap
    for name in ("llms.txt", "sitemap.xml"):
        for u in re.findall(re.escape(SITE_URL) + r"(/[^\s)<]*)", (OUT / name).read_text(encoding="utf-8")):
            n_links += 1
            if resolve(u) is None:
                problems.append(f"{name}: broken link {u}")
    # weight of the start page: the HTML and everything it loads from this site
    index = OUT / "index.html"
    weight = index.stat().st_size
    for ref in set(parsed[index].refs):
        if ref.startswith("/") and re.search(r"\.(css|js|png|svg|jpg|woff2?)(\?|$)", ref):
            t = resolve(ref)
            weight += t.stat().st_size if t else 0
    if weight > 200_000:
        problems.append(f"index.html weighs {weight} bytes with its assets (limit 200000)")
    for name in ("CNAME", ".nojekyll", "404.html", "llms.txt", "skill/SKILL.md", "skill/unifold-convert/SKILL.md",
                 "spec.html", "spec.md"):
        if not (OUT / name).exists():
            problems.append(f"missing {name}")
    for pr in problems:
        print(f"check: {pr}", file=sys.stderr)
    print(f"checked {len(own)} pages, {n_links} internal links; start page {weight / 1000:.1f} kB with its assets; "
          f"{len(problems)} problem(s)")
    return 1 if problems else 0


def serve(port: int) -> None:
    import http.server

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(OUT), **kw)

        def send_head(self):
            p = self.path.split("?")[0].split("#")[0]
            f = resolve(p) if p != "/" else OUT / "index.html"
            if f is None:
                self.send_response(404)
                body = (OUT / "404.html").read_bytes()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                import io
                return io.BytesIO(body)
            self.path = "/" + f.relative_to(OUT).as_posix()
            return super().send_head()

    print(f"serving {OUT.relative_to(ROOT)}/ on http://localhost:{port} as GitHub Pages would (Ctrl-C stops)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    args = sys.argv[1:]
    build()
    rc = check() if "--check" in args else 0
    if "--serve" in args:
        i = args.index("--serve")
        serve(int(args[i + 1]) if len(args) > i + 1 and args[i + 1].isdigit() else 8000)
    sys.exit(rc)
