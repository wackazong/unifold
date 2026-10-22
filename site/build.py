#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["markdown>=3.4", "pyyaml>=6"]
# ///
"""Build the static site for https://unifold.md into site/_out/.

    python3 site/build.py            # build
    python3 site/build.py --serve    # build, then serve on http://localhost:8000
    python3 site/build.py --check    # build, then check links, HTML and page weight

Everything is derived from README.md, docs/references/unifold/*.md and the
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
REF = ROOT / "docs" / "references" / "unifold"
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


def highlight(code: str, lang: str, mark_wiring: bool = False) -> str:
    """A very small highlighter: YAML keys and comments, console prompts and findings."""
    out = []
    in_wiring = False
    for line in code.split("\n"):
        e = esc(line, quote=False)
        if lang in ("yaml", "yml"):
            is_wiring_entry = in_wiring and line.startswith((" ", "\t")) and line.strip()
            if re.match(r"^\S", line):
                in_wiring = line.startswith("wiring:")
            m = re.match(r"^(.*?)((?:^|\s)#.*)$", e)
            body, comment = (m.group(1), m.group(2)) if m else (e, "")
            body = re.sub(r"^(\s*(?:- )?)([^\s:#][^:#]*?)(:)(\s|$)", r'\1<span class="k">\2</span>\3\4', body)
            e = body + (f'<span class="c">{comment}</span>' if comment else "")
            if mark_wiring and is_wiring_entry:
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


def code_block(code: str, lang: str, mark_wiring: bool = False) -> str:
    cls = f' class="language-{esc(lang)}"' if lang else ""
    return f"<pre><code{cls}>{highlight(code, lang, mark_wiring)}\n</code></pre>"


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
    nav = [("spec", "Standard"), ("documents", "Documents"), ("tool", "Tool")]
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
<a class="brand" href="/">{LOGO.format(s=26)}<span>unifold</span></a>
<span class="draft" title="This is a draft. It is not stable.">draft {esc(version)}</span>
<nav aria-label="Site">{links}<a href="{REPO_URL}" rel="noopener">GitHub</a></nav>
</div></header>
{body}
<footer class="bottom"><div class="wrap">
<p>unifold {esc(version)} is a draft. The text, the skill and the tool are licensed under
<a href="/LICENSE-MIT.txt">MIT</a> or <a href="/LICENSE-APACHE.txt">Apache-2.0</a>, at your option.</p>
<p><a href="/spec">Standard</a> <a href="/guide">Guide</a> <a href="/{esc(version)}/unifold.schema.json">JSON Schema</a>
<a href="/skill/SKILL.md">Skill</a> <a href="/llms.txt">llms.txt</a> <a href="{REPO_URL}" rel="noopener">GitHub</a></p>
<p class="quiet">No scripts, no trackers, no fonts from elsewhere.</p>
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
                version=version, current=slug if slug in ("spec", "documents", "tool") else "")


# --------------------------------------------------------------------------
# Landing page, composed from README.md
# --------------------------------------------------------------------------
def inline_md(text: str, version: str) -> str:
    out, _ = render_md(text, ROOT, version, permalinks=False)
    return out


def landing(readme: str, explorers: list[tuple[str, str]], css_href: str, version: str) -> str:
    readme = re.sub(r"^#\s+.*\n", "", readme, count=1)          # the name is in the header
    pre, _, rest = readme.partition("\n## ")
    rest = "## " + rest if rest else ""

    # --- first screen: promise, lede, then every code block of the preamble as a figure
    segs = split_fences(pre)
    promise, lede = "", ""
    if segs and segs[0][0] == "md":
        paras = [p.strip() for p in re.split(r"\n\s*\n", segs[0][1]) if p.strip()]
        if paras:
            promise = re.sub(r"\s+", " ", paras[0].strip("*"))
            lede = "\n\n".join(paras[1:])
        segs = segs[1:]
    panels, figures, caption = [], [], ""
    for seg in segs:
        if seg[0] == "md":
            caption = seg[1].strip()
            continue
        _, lang, body = seg
        if lang in ("yaml", "yml") and not caption and not figures:
            label = ""
            first, _, tail = body.partition("\n")
            if first.startswith("#"):
                label, body = first.lstrip("# ").strip(), tail
            name = re.match(r"^(\S+)(.*)$", label)
            tab = f'<figcaption><code>{esc(name.group(1))}</code>{esc(name.group(2))}</figcaption>' if name else ""
            panels.append(f'<figure class="panel">{tab}{code_block(body, lang, mark_wiring=True)}</figure>')
        else:
            cap = f"<figcaption>{inline_md(caption, version)}</figcaption>" if caption else ""
            inner = render_mermaid(body) if lang == "mermaid" else code_block(body, lang)
            kind = "drawn" if lang == "mermaid" else "checked"
            figures.append(f'<div class="step {kind}">{cap}{inner}</div>')
            caption = ""
    hero = f"""<section class="hero"><div class="wrap">
<h1>{esc(promise)}</h1>
<div class="lede">{inline_md(lede, version)}</div>
<p class="actions"><a class="button" href="/spec">Read the standard</a>
<a href="/adopting">Try it on a repository</a>
<a href="{REPO_URL}" rel="noopener">Source on GitHub</a></p>
</div>
<div class="wrap">
<div class="fold" role="group" aria-label="Three manifests">{''.join(panels)}</div>
<div class="steps">{''.join(figures)}</div>
</div></section>"""

    # --- sections of the README
    sections = re.split(r"(?m)^(?=## )", rest)
    html_sections = []
    for i, sec in enumerate(s for s in sections if s.strip()):
        body, _ = render_md(sec, ROOT, version)
        heading = re.match(r"## (.+)", sec).group(1).strip()
        sid = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        extra = ""
        if heading.lower().startswith("example") and explorers:
            items = "".join(f'<li><a href="/examples/{esc(n)}/">{esc(n)}</a>{"" if t == n else ": " + esc(t)}</li>' for n, t in explorers)
            extra = f'<p>Each map can be explored in the browser, as written by <code>unifold site</code>:</p><ul class="explorers">{items}</ul>'
        cls = "band start" if i == 0 else "band"
        html_sections.append(f'<section class="{cls}" data-s="{sid}"><div class="wrap prose">{body}{extra}</div></section>')
        if i == 0:
            html_sections.append(read_on(explorers, version))
    main = f'<main id="main">{hero}{"".join(html_sections)}</main>'
    return page(title="unifold: an architecture map kept in the folders and checked against the code",
                description=promise + " A draft open standard for documenting repository architecture, for people and AI agents.",
                path="/", body=main, css_href=css_href, version=version, body_class="home")


def read_on(explorers: list[tuple[str, str]], version: str) -> str:
    ex = "".join(f'<a href="/examples/{esc(n)}/">{esc(n)}</a>' for n, _ in explorers)
    ex_card = f'<div><h3>Explore an example</h3><p>The map of a repository, as a page you can click through.</p><p class="links">{ex}</p></div>' if explorers else ""
    return f"""<section class="band readon"><div class="wrap"><div class="cards">
<div><h3><a href="/spec">The standard</a></h3><p>One page: the manifest, wiring, what a checker guarantees. Read this first.</p></div>
<div><h3><a href="/first-map">Your first map</a></h3><p>A tutorial, then the reference: <a href="/documents">documents</a>, <a href="/agents">agents</a>, the <a href="/tool">tool</a> and its <a href="/rules">rules</a>; and the explanation: <a href="/requirements">requirements</a>, <a href="/reasoning">reasoning</a>, <a href="/wiring">wiring</a>, <a href="/risks">risks</a>.</p></div>
{ex_card}
<div><h3>For agents and editors</h3><p class="links"><a href="/skill/SKILL.md">The skill</a><a href="/llms.txt">llms.txt</a><a href="/{esc(version)}/unifold.schema.json">JSON Schema</a></p><p>Every chapter is also plain Markdown: <code>/spec.md</code>.</p></div>
</div></div></section>"""


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
