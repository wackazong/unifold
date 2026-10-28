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
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration. REPO_URL is a placeholder until the repository has its home.
# --------------------------------------------------------------------------
REPO_URL = "https://github.com/wackazong/unifold"
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
STATIC = SITE / "static"          # copied as it is: the heading font with its licence, og.png

EXPL = ROOT / "docs" / "explanation"
TUT = ROOT / "docs" / "tutorials"

# slug (the URL), source file, name in the navigation, one line for indexes, kind
CHAPTERS = [
    ("spec", REF / "spec.md", "The standard", "The whole standard on one page: manifest, wiring, documents, what a checker guarantees.", "Standard"),
    ("documents", REF / "documents.md", "Documents", "The files of a unit, the four kinds of knowledge, README.md, the generated AGENTS.md, the explanation files, where a file may point.", "Reference"),
    ("writing", REF / "writing.md", "Writing", "How each document is written: context items, decisions, references, contracts, skills, tutorials, explanation files, the review checklist.", "Reference"),
    ("contracts", REF / "contracts.md", "Contracts", "The one document of a connection: parts with signatures and examples, the fake, folders, the template.", "Reference"),
    ("agents", REF / "agents.md", "Agents", "How coding agents find and use unifold, per agent.", "Reference"),
    ("tool", REF / "tool.md", "Tool", "The reference tool: commands, output, hooks, continuous integration.", "Reference"),
    ("tool-json", REF / "tool-json.md", "Tool JSON", "The JSON that the reference tool prints.", "Reference"),
    ("rules", REF / "rules.md", "Rules", "Every finding the reference tool reports.", "Reference"),
    ("requirements", EXPL / "requirements.md", "Requirements", "What the standard must achieve, for which repositories it fits, where the value is.", "Explanation"),
    ("reasoning", EXPL / "reasoning.md", "Reasoning", "Where the parts come from, what unifold adds, the design ideas behind it, Diátaxis and arc42.", "Explanation"),
    ("wiring", EXPL / "wiring.md", "Wiring", "Wiring in practice: names, passing needs up, several children on one provider, alternatives, adapters, the kinds of units, scenarios, services.", "Explanation"),
    ("invariants", EXPL / "invariants.md", "Invariants", "What is true of the standard, the skills and the tool at every moment.", "Explanation"),
    ("risks", EXPL / "risks.md", "Risks", "Risks and known limits of the standard.", "Explanation"),
    ("first-map", TUT / "first-map.md", "Your first map", "A tutorial: a root manifest, two units, a connection, the first diagram, documents for one unit.", "Tutorial"),
]
SLUG_OF = {src.resolve(): slug for slug, src, _, _, _ in CHAPTERS}
# old addresses that still get a page
REDIRECTS = {"guide": "/", "adopting": "/first-map/", "design": "/reasoning/"}

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
# The mark: one sheet with a crease. Left panel lies flat, right panel lifts. Corners on a 32 grid;
# the logo, the SVG icon and the PNG icons are all drawn from them.
MARK = (((3, 9), (15, 5), (15, 27), (3, 23)), ((17, 5), (29, 9), (29, 23), (17, 27)))
MARK_D = ["M" + "L".join(f"{x} {y}" for x, y in panel) + "z" for panel in MARK]
MARK_LIGHT, MARK_DARK = ("#0b6b5c", "#5cc4ae"), ("#5fd3bb", "#2c8f7d")
LOGO = ('<svg class="mark" viewBox="0 0 32 32" width="{s}" height="{s}" aria-hidden="true">'
        f'<path class="m1" d="{MARK_D[0]}"/><path class="m2" d="{MARK_D[1]}"/></svg>')
FAVICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><style>"
           f".a{{fill:{MARK_LIGHT[0]}}}.b{{fill:{MARK_LIGHT[1]}}}@media (prefers-color-scheme:dark)"
           f"{{.a{{fill:{MARK_DARK[0]}}}.b{{fill:{MARK_DARK[1]}}}}}</style>"
           f"<path class='a' d='{MARK_D[0]}'/><path class='b' d='{MARK_D[1]}'/></svg>")


def mark_png(size: int, scale: float, offset: float = 0, background: str | None = None) -> bytes:
    """The mark as a square PNG, for browsers and devices that take no SVG icon. A point of the
    grid lands at offset + scale * point; the coverage of a pixel is exact across and sampled down."""
    sub = 8
    cover = [[[0.0] * size for _ in MARK] for _ in range(size)]
    for py in range(size):
        for s in range(sub):
            y = (py + (s + .5) / sub - offset) / scale
            for k, panel in enumerate(MARK):
                xs = [ax + (y - ay) * (bx - ax) / (by - ay)
                      for (ax, ay), (bx, by) in zip(panel, panel[1:] + panel[:1]) if min(ay, by) <= y < max(ay, by)]
                if len(xs) < 2:
                    continue
                left, right = offset + scale * min(xs), offset + scale * max(xs)
                for px in range(max(0, int(left)), min(size, int(right) + 1)):
                    cover[py][k][px] += max(0.0, min(right, px + 1) - max(left, px)) / sub
    colors = [bytes.fromhex(c[1:]) for c in MARK_LIGHT]
    back = bytes.fromhex(background[1:]) if background else None
    raw = bytearray()
    for py in range(size):
        raw.append(0)
        for px in range(size):
            a = [cover[py][k][px] for k in range(len(MARK))]
            alpha = min(1.0, sum(a))
            rgb = [sum(c[i] * w for c, w in zip(colors, a)) / alpha if alpha else 0 for i in range(3)]
            if back:
                rgb, alpha = [v * alpha + b * (1 - alpha) for v, b in zip(rgb, back)], 1.0
            raw += bytes(round(v) for v in rgb) + bytes([round(alpha * 255)])

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def ico(images: list[tuple[int, bytes]]) -> bytes:
    """A favicon.ico that holds PNGs of the given sizes."""
    head, data = struct.pack("<HHH", 0, 1, len(images)), b""
    for size, png in images:
        head += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(png), 6 + 16 * len(images) + len(data))
        data += png
    return head + data


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
    if href.startswith(SITE_URL + "/"):                 # an absolute link to a chapter: the folder form
        path, _, frag = href[len(SITE_URL) + 1:].partition("#")
        if path in {s for s, _, _, _, _ in CHAPTERS}:
            return f"/{path}/" + (f"#{frag}" if frag else "")
        return href
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
        return f"/{SLUG_OF[target.resolve()]}/{frag}"
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
def hashed(name: str) -> str:
    """The address of a file of site/ with a hash of its content, so that browsers fetch it again after a change."""
    return f"/{name}?v={hashlib.sha256((SITE / name).read_bytes()).hexdigest()[:8]}"


def page(*, title: str, description: str, path: str, body: str, css_href: str, version: str,
         current: str = "", body_class: str = "", noindex: bool = False) -> str:
    nav = [("documents", "Documentation"), ("spec", "Standard"), ("tool", "Tool"), ("first-map", "Get Started")]
    links = "".join(
        f'<a href="/{s}/"{CUR if s == current else ""}>{n}</a>' for s, n in nav)
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
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<link rel="preload" href="/patua-one.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{css_href}">
<script src="{hashed("search.js")}" defer></script>
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="brand" href="/">{LOGO.format(s=24)}<span>unifold</span></a>
<span class="version" title="unifold {esc(version)}">{esc(version)}</span>
<nav aria-label="Site">{links}<a class="gh" href="{REPO_URL}" rel="noopener" aria-label="unifold on GitHub">{icon("github", "icon sm")}<span>GitHub</span></a></nav>
<form class="site-search" action="/search/" role="search"><input type="search" name="q" placeholder="Search" aria-label="Search the documentation" autocomplete="off" spellcheck="false"><button aria-label="Search">{icon("search", "icon sm")}</button></form>
</div></header>
{body}
<footer class="bottom"><div class="wrap">
<div class="foot-brand"><a class="brand" href="/">{LOGO.format(s=22)}<span>unifold</span></a>
<p>Your project structure is your architecture. Keep your documentation, architecture, and project structure aligned.</p></div>
<nav class="foot-cols" aria-label="Footer">
<div><h2>Standard</h2><a href="/documents/">Documentation</a><a href="/spec/">The standard</a><a href="/writing/">Writing</a><a href="/{esc(version)}/unifold.schema.json">JSON Schema</a></div>
<div><h2>Tool</h2><a href="/tool/">Commands</a><a href="/rules/">Rules</a><a href="/tool-json/">JSON output</a><a href="/first-map/">Get Started</a></div>
<div><h2>Agents</h2><a href="/agents/">How agents use it</a><a href="/skill/SKILL.md">The skill</a><a href="/skill/unifold-convert/SKILL.md">The convert skill</a><a href="/llms.txt">llms.txt</a></div>
</nav>
<p class="fine">The text, the skills and the tool are licensed under <a href="/LICENSE-MIT.txt">MIT</a> or <a href="/LICENSE-APACHE.txt">Apache-2.0</a>, at your option. Headings are set in Patua One by LatinoType, under the <a href="/patua-one-OFL.txt">SIL Open Font License</a>.</p>
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


# --------------------------------------------------------------------------
# Search: one entry per section, [address, page, heading, text]; site/search.js searches them
# --------------------------------------------------------------------------
SEARCH: list[list[str]] = []


def text_of(fragment: str) -> str:
    """The text of an HTML fragment, without diagrams, icons and permalinks."""
    s = re.sub(r'<figure class="diagram.*?</figure>|<svg.*?</svg>|<a class="anchor".*?</a>', " ", fragment, flags=re.S)
    s = re.sub(r"</?(?:p|li|ul|ol|t[dhr]|table|pre|div|h\d|br|blockquote|figure|figcaption|details|summary)\b[^>]*>",
               " ", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def index_chapter(url: str, name: str, body: str) -> None:
    """A chapter in the search index: the part before the first section, then every section down to h3."""
    parts = re.split(r'(<h[1-3] id="[^"]+">.*?</h[1-3]>)', body, flags=re.S)
    for head, text in zip(parts[1::2], parts[2::2]):
        m = re.match(r'<h([1-3]) id="([^"]+)">(.*?)</h\1>', head, re.S)
        SEARCH.append([url if m.group(1) == "1" else f"{url}#{m.group(2)}", name, text_of(m.group(3)), text_of(text)])


def search_page(css_href: str, version: str) -> str:
    chapters = "".join(f'<li><a href="/{s}/">{esc(n)}</a></li>' for s, _, n, _, _ in CHAPTERS)
    main = f"""<main id="main" class="wrap search-main">
<h1>Search</h1>
<form class="search-big" action="/search/" role="search">
<input type="search" name="q" placeholder="Search the documentation" aria-label="Search the documentation" autocomplete="off" spellcheck="false" autofocus>
</form>
<p class="search-status" id="search-status" aria-live="polite"></p>
<ol class="results" id="results"></ol>
<noscript><p>The search runs in your browser and needs JavaScript. These are all the chapters:</p><ul>{chapters}</ul></noscript>
</main>"""
    return page(title="Search | unifold", description="Search the standard, the references, the explanations and the tutorial.",
                path="/search/", body=main, css_href=css_href, version=version, body_class="search-page", noindex=True)


def chapter_page(slug: str, src: Path, text: str, css_href: str, version: str) -> str:
    body, tokens = render_md(text, src.parent, version)
    m = re.search(r"^#\s+(.+)$", text, re.M)
    h1 = re.sub(r"[`*]", "", m.group(1)).strip() if m else slug
    title = h1 if "unifold" in h1.lower() else f"{h1} | unifold"
    name, desc = next((n, d) for s, _, n, d, _ in CHAPTERS if s == slug)
    index_chapter(f"/{slug}/", name, body)
    chapters, kind_shown = "", None
    for s, _, n, _, kind in CHAPTERS:
        if kind != kind_shown:
            chapters += f'<li class="kind">{esc(kind)}</li>'
            kind_shown = kind
        chapters += (f'<li><a href="/{s}/"{CUR if s == slug else ""}>{esc(n)}</a>'
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
    return page(title=title, description=desc, path=f"/{slug}/", body=main, css_href=css_href,
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
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>',
    "github": '<path fill="currentColor" stroke="none" d="M12 2.5a9.5 9.5 0 0 0-3 18.5c.5.1.7-.2.7-.5v-1.7c-2.7.6-3.3-1.2-3.3-1.2-.4-1.1-1-1.4-1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.1-.2-4.4-1.1-4.4-4.8 0-1 .4-1.9 1-2.6-.1-.3-.4-1.2.1-2.6 0 0 .8-.3 2.6 1a9 9 0 0 1 4.8 0c1.8-1.3 2.6-1 2.6-1 .5 1.4.2 2.3.1 2.6.6.7 1 1.6 1 2.6 0 3.7-2.3 4.6-4.4 4.8.3.3.6.9.6 1.8v2.7c0 .3.2.6.7.5A9.5 9.5 0 0 0 12 2.5z"/>',
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


ACCENTS = ("teal", "blue", "amber", "coral", "violet")


def band(sid: str, heading: str, inner: str, n: int, cls: str = "") -> str:
    """A full-width section whose heading carries the highlighter bar of its colour; it goes into the search."""
    SEARCH.append([f"/#{sid}", "Start page", heading, text_of(inner)])
    return (f'<section class="band {ACCENTS[n % len(ACCENTS)]} {cls}" id="{sid}"><div class="wrap">'
            f'<h2><span>{esc(heading)}</span></h2>{inner}</div></section>')


def first_link(md: str) -> str | None:
    m = re.search(r"\[[^\]]+\]\(([^)]+)\)", md)
    return m.group(1) if m else None


def how_it_works(body: str, version: str) -> tuple[str, str]:
    """The section 'How it works': (the manifests as one sheet, the rest of the section)."""
    sheet, manifests, parts = [], [], []
    for seg in split_fences(body):
        if seg[0] == "md":
            if seg[1].strip():
                parts.append(("md", seg[1].strip()))
            continue
        _, lang, code = seg
        if lang in ("yaml", "yml"):
            first, _, tail = code.partition("\n")
            label = first.lstrip("# ").strip() if first.startswith("#") else ""
            code = tail if label else code
            try:
                data = yaml.safe_load(code) or {}
            except yaml.YAMLError:
                data = {}
            manifests.append((label, data))
            sheet.append((label, code, data))
        else:
            parts.append(("term", code))
    names = {k.rsplit(".", 1)[-1] for _, d in manifests if isinstance(d, dict)
             for k in (d.get("wiring") or {})}
    panels = []
    for label, code, data in sheet:
        role = "connects" if "wiring" in data else "provides" if "capabilities" in data \
            else "needs" if "needs" in data else ""
        file_name, _, note = label.partition(" ")
        panels.append(f'<figure class="panel"><figcaption><code>{esc(file_name)}</code>'
                      f'<span class="note">{esc(note)}</span>'
                      f'{f"<span class={chr(34)}role{chr(34)}>{role}</span>" if role else ""}</figcaption>'
                      f'{code_block(code.rstrip(), "yaml", mark_wiring=True, mark_names=names)}</figure>')
    root_name = next((str(d.get("name")) for _, d in manifests if d.get("name")), "")
    diagram = wiring_diagram(manifests)
    before, after, figures = [], [], []
    for kind, text in parts:
        if kind == "term":
            figures.append(terminal(text, "unifold check", f"~/{root_name}" if root_name else ""))
        elif kind == "md":
            (after if figures else before).append(f'<div class="text">{inline_md(text, version)}</div>')
    if diagram:
        figures.append(f'<figure class="diagram-card"><figcaption><code>docs/diagrams/component.md</code>'
                       f'<span class="role generated">generated</span></figcaption>{diagram}</figure>')
    sheet_html = f'<div class="sheet" role="group" aria-label="The manifests">{"".join(panels)}</div>' if panels else ""
    rest = [*before, f'<div class="duo">{"".join(figures)}</div>' if figures else "", *after]
    return sheet_html, "".join(rest)


def landing(readme: str, explorers: list[tuple[str, str]], css_href: str, version: str) -> str:
    m = re.match(r"^#\s+(.+)\n", readme)
    title = m.group(1).strip() if m else "unifold"
    pre, _, rest = (readme[m.end():] if m else readme).partition("\n## ")
    sections = parse_sections("## " + rest) if rest else []

    # --- the first screen: the quote under the title is the claim; its first sentence is the
    # title of the page, the rest the subtitle. Everything else is ordinary text.
    quote, intro = "", []
    for para in (p.strip() for p in re.split(r"\n\s*\n", pre) if p.strip()):
        if para.startswith(">") and not quote:
            quote = re.sub(r"(?m)^>\s?", "", para).strip()
        else:
            intro.append(para)
    how = next((b for h, b in sections if h.lower().startswith("how it works")), "")
    sheet_html, how_rest = how_it_works(how, version) if how else ("", "")
    claim, _, subtitle = (quote or title).partition(". ")
    claim = claim if claim.endswith((".", "!", "?")) else claim + "."
    hero = f"""<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1>{esc(claim)}</h1>
{f'<p class="subtitle">{strip_p(inline_md(subtitle, version))}</p>' if subtitle else ''}
<div class="hero-actions">
<a class="button primary" href="/first-map/">Get Started</a>
<a class="button" href="/spec/">Read the standard</a>
<p class="install"><code>uvx unifold init</code></p>
</div>
</div>
{sheet_html}
</div></section>"""
    blocks = [hero]
    lead = inline_md(chr(10) + chr(10).join(intro), version) if intro else ""
    if intro:
        blocks.append(f'<section class="intro"><div class="wrap"><div class="lead">{lead}</div></div></section>')
    SEARCH.append(["/", "Start page", claim, text_of(f"<p>{inline_md(subtitle, version)}</p>{lead}")])

    n = 0
    i = 0
    while i < len(sections):
        heading, body = sections[i]
        low, sid = heading.lower(), slug(heading)
        nxt = sections[i + 1] if i + 1 < len(sections) else None
        if low.startswith("how it works"):
            blocks.append(band(sid, heading, how_rest, n, "how"))
        elif low.startswith("what a unit has") and table_rows(body):
            tiles = []
            for k, (name, what) in enumerate(r[:2] for r in table_rows(body) if len(r) >= 2):
                plain = name.strip("`")
                generated = what.lower().startswith("generated")
                what = re.sub(r"^Generated:\s*", "", what)
                what = what[:1].upper() + what[1:]
                tiles.append(f'<div class="tile t{k % 4}{" generated" if generated else ""}">'
                             f'<p class="tile-name"><code>{esc(plain)}</code>'
                             f'{"<span>generated</span>" if generated else ""}</p>'
                             f'<p>{strip_p(inline_md(what, version))}</p></div>')
            intro_md = re.split(r"(?m)^\|", body, maxsplit=1)[0].strip()
            inner = (f'<div class="text">{inline_md(intro_md, version)}</div>' if intro_md else "") + \
                f'<div class="tiles">{"".join(tiles)}</div>'
            blocks.append(band(sid, heading, inner, n, "anatomy"))
        elif low.startswith("how people") and nxt and nxt[0].lower().startswith("how agents"):
            cols = "".join(f'<div class="col" id="{slug(h)}"><h3>{esc(h)}</h3>{inline_md(b, version)}</div>'
                           for h, b in (sections[i], nxt))
            blocks.append(band("readers", "People and agents", f'<div class="cols two">{cols}</div>', n, "readers"))
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
            blocks.append(band(sid, heading, f'<div class="faq">{"".join(items)}</div>', n, "questions"))
        elif (low == "capabilities" or low.startswith("what this")) and subsections(body):
            intro_md = re.split(r"(?m)^### ", body, maxsplit=1)[0].strip()
            cols = []
            for h, b in subsections(body):
                target = first_link(b)
                more = f'<a class="button" href="{esc(rewrite_href(target, ROOT, version))}">Learn more</a>' if target else ""
                cols.append(f'<div class="col">{icon(icon_for(h), "icon lg")}<h3>{esc(h)}</h3>'
                            f'{inline_md(b, version)}{more}</div>')
            inner = (f'<p class="section-lede">{strip_p(inline_md(intro_md, version))}</p>' if intro_md else "") + \
                f'<div class="cols three">{"".join(cols)}</div>'
            blocks.append(band(sid, heading, inner, n, "capabilities dark"))
        elif low == "needs" and nxt and nxt[0].lower() == "commands":
            needs = "".join(f'<p><strong>{esc(h)}.</strong> {strip_p(inline_md(b, version))}</p>'
                            for h, b in subsections(body)) or inline_md(body, version)
            cmd = render_md(nxt[1], ROOT, version, permalinks=False)[0]
            blocks.append(band(slug(nxt[0]), nxt[0], f'<div class="run">{cmd}<div class="needs">{needs}</div></div>',
                               n, "commands"))
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
                        f'<a href="/examples/{esc(n_)}/">{esc(n_)}</a>' for n_, _ in explorers) + ".</p>"
                cards.append(f'<div class="index"><h3>{strip_p(inline_md(row[0], version))}</h3><ul>{items}</ul>{maps}</div>')
            cards.append(f'<div class="index"><h3>For agents</h3><ul><li><a href="/skill/SKILL.md">The skill</a></li>'
                         f'<li><a href="/llms.txt">llms.txt</a></li><li><a href="/{esc(version)}/unifold.schema.json">JSON Schema</a></li></ul>'
                         f'<p>Every chapter is also plain Markdown, for example <code>/spec.md</code>.</p></div>')
            blocks.append(band(sid, heading, f'<div class="index-grid">{"".join(cards)}</div>', n, "read-next"))
        else:
            inner, _ = render_md(body, ROOT, version, permalinks=False)
            blocks.append(band(sid, heading, f'<div class="text">{inner}</div>', n,
                               "closing" if i == len(sections) - 1 else ""))
        n += 1
        i += 1

    main = f'<main id="main">{"".join(blocks)}</main>'
    description = f"{claim} {subtitle}".strip() + \
        " An open standard for repository architecture, checked for consistency, for people and coding agents."
    return page(title=title, description=description, path="/", body=main, css_href=css_href,
                version=version, body_class="home")


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def build() -> None:
    schema = REF / "unifold.schema.json"
    if not schema.exists():
        die(f"{schema.relative_to(ROOT)} is missing. The site serves it at /<version>/unifold.schema.json; "
            "the build cannot continue without it.")
    for need in [ROOT / "README.md", SKILL, CONVERT_SKILL, SITE / "style.css", SITE / "search.js"] + \
            [src for _, src, _, _, _ in CHAPTERS]:
        if not need.exists():
            die(f"{need.relative_to(ROOT)} is missing.")

    version = "0.3"
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

    # chapters, as HTML at /slug/ (file slug/index.html, which every web server serves) and as Markdown at /slug.md
    for slug, src, _, _, _ in CHAPTERS:
        text = src.read_text(encoding="utf-8")
        (OUT / slug).mkdir()
        (OUT / slug / "index.html").write_text(chapter_page(slug, src, text, css_href, version), encoding="utf-8")
        (OUT / f"{slug}.md").write_text(text, encoding="utf-8")
    for old, new in REDIRECTS.items():
        (OUT / old).mkdir()
        (OUT / old / "index.html").write_text(
            f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>'
            f'<meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="{SITE_URL}{new}">'
            f'</head><body><p>This page moved to <a href="{new}">{SITE_URL}{new}</a>.</p></body></html>\n',
            encoding="utf-8")

    (OUT / "index.html").write_text(
        landing((ROOT / "README.md").read_text(encoding="utf-8"), explorers, css_href, version), encoding="utf-8")

    # search: the index of every section, which search.js fetches the first time someone searches
    (OUT / "search.json").write_text(json.dumps(SEARCH, ensure_ascii=False, separators=(",", ":")) + "\n",
                                     encoding="utf-8")
    shutil.copyfile(SITE / "search.js", OUT / "search.js")
    (OUT / "search").mkdir()
    (OUT / "search" / "index.html").write_text(search_page(css_href, version), encoding="utf-8")

    # machine-readable files
    (OUT / version).mkdir()
    shutil.copyfile(schema, OUT / version / "unifold.schema.json")
    # the skills as they are in the repository, with their templates and scripts: the unifold skill
    # at /skill/, the address that README.md and llms.txt give, and every folder of docs/skills/
    # at /skill/<name>/, so that a relative link from one skill into another resolves too
    skip = shutil.ignore_patterns(".*", "__pycache__", "*.egg-info")
    shutil.copytree(SKILL.parent, OUT / "skill", ignore=skip)
    for d in sorted(p for p in SKILL.parent.parent.iterdir() if p.is_dir()):
        shutil.copytree(d, OUT / "skill" / d.name, ignore=skip)
    for lic in ("LICENSE-MIT", "LICENSE-APACHE"):
        if (ROOT / lic).exists():
            shutil.copyfile(ROOT / lic, OUT / f"{lic}.txt")
        else:
            die(f"{lic} is missing.")

    llms = [
        "# unifold", "",
        f"> unifold {version} is an open standard for writing down how the parts of a repository depend on "
        "each other. A folder becomes a unit by getting a `unifold.yaml` that lists what it provides and what it "
        "needs; the unit above connects each need to a provider; a checker keeps this consistent and "
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
    # scale and offset put the upright edges of the panels on whole pixels, so that small icons stay sharp
    (OUT / "favicon.ico").write_bytes(ico([(16, mark_png(16, .5, .5)), (32, mark_png(32, 1)), (48, mark_png(48, 1.5, .5))]))
    (OUT / "apple-touch-icon.png").write_bytes(mark_png(180, 4, 26, "#ffffff"))
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    urls = ["/"] + [f"/{s}/" for s, _, _, _, _ in CHAPTERS] + [f"/examples/{n}/" for n, _ in explorers]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    if STATIC.exists():
        for f in STATIC.iterdir():
            if f.is_file():
                shutil.copyfile(f, OUT / f.name)
    nf = f"""<main id="main" class="wrap prose notfound">
<h1>This page does not exist</h1>
<p>The address may be mistyped, or the page has moved.</p>
<ul><li><a href="/">Start page</a></li><li><a href="/spec/">The standard</a></li><li><a href="/first-map/">Get Started</a></li></ul>
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
    """The file a plain web server serves for a path, or None. A folder serves its index.html;
    a folder path without the trailing slash is redirected to it by the server."""
    p = url_path.split("#")[0].split("?")[0]
    f = OUT / p.lstrip("/")
    if f.is_dir():
        return f / "index.html" if (f / "index.html").exists() else None
    if f.is_file() and not p.endswith("/"):
        return f
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
    # addresses in the index of the search
    for url, *_ in json.loads((OUT / "search.json").read_text(encoding="utf-8")):
        n_links += 1
        path, _, frag = url.partition("#")
        target = resolve(path)
        if target is None:
            problems.append(f"search.json: broken link {url}")
        elif frag and target in parsed and frag not in parsed[target].ids:
            problems.append(f"search.json: no anchor #{frag} in {target.relative_to(OUT)}")
    # links inside the copied skills: relative ones must name a published file or folder,
    # those to the site a page and its anchor (code is skipped; templates hold placeholders)
    n_raw = 0
    for f in sorted((OUT / "skill").rglob("SKILL.md")):
        text = re.sub(r"^```.*?^```", "", f.read_text(encoding="utf-8"), flags=re.S | re.M)
        text = re.sub(r"`[^`\n]*`", "", text)
        for ref in re.findall(r"\]\(\s*<?([^)\s>]+)", text) + re.findall(r"<(https?://[^>\s]+)>", text):
            if ref.startswith(SITE_URL):
                path, _, frag = (ref[len(SITE_URL):] or "/").partition("#")
                target = resolve(path)
            elif re.match(r"^([a-z][a-z0-9+.-]*:|#|/)", ref, re.I):
                continue
            else:
                path, frag = ref.split("#")[0], ""
                target = Path(os.path.normpath(f.parent / path))
                target = target if target.is_relative_to(OUT) and target.exists() else None
            n_raw += 1
            if target is None:
                problems.append(f"{f.relative_to(OUT)}: broken link {ref}")
            elif frag and target in parsed and frag not in parsed[target].ids:
                problems.append(f"{f.relative_to(OUT)}: no anchor #{frag} in {target.relative_to(OUT)}")
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
                 "spec/index.html", "spec.md", "search/index.html", "search.js", "search.json", "favicon.ico", "favicon.svg",
                 "apple-touch-icon.png"):
        if not (OUT / name).exists():
            problems.append(f"missing {name}")
    for pr in problems:
        print(f"check: {pr}", file=sys.stderr)
    print(f"checked {len(own)} pages, {n_links} internal links, {n_raw} links in the skills; start page {weight / 1000:.1f} kB with its assets; "
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
