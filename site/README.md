# The site unifold.md

`build.py` writes the whole site into `site/_out/` from `README.md`,
`docs/references/unifold/*.md`, the skill and the examples. Nothing is
converted by hand; `_out/` is not committed.

## Build

```sh
python3 -m pip install markdown pyyaml    # or: uv run site/build.py
python3 site/build.py --check             # build; check links, HTML, page weight
python3 site/build.py --serve             # build; serve as GitHub Pages would (/spec, not spec.html)
```

| Address | File | From |
|---|---|---|
| `/` | `index.html` | `README.md`; the part before the first `##` becomes the first screen |
| `/spec`, `/documents`, `/reasoning`, `/first-map`, ... | `spec.html`, ... | the reference chapters from `docs/references/unifold/`, the explanation files from `docs/explanation/` and the tutorial from `docs/tutorials/`; `/guide`, `/adopting` and `/design` redirect |
| `/spec.md`, ... | the same chapters as plain Markdown | |
| `/0.1/unifold.schema.json` | | the schema; the build stops if it is missing |
| `/skill/SKILL.md`, `/skill/unifold-convert/SKILL.md`, `/llms.txt` | | the two skills; an index for agents |
| `/examples/<name>/` | `index.html` | every `examples/**/unifold.html` that exists |

GitHub Pages serves `spec.html` at `/spec`; `spec/index.html` would redirect to `/spec/`.

## Diagrams

A Mermaid block is replaced by an inline SVG from `site/diagrams/<hash>.svg`
(hash of the Mermaid source), coloured by `style.css` for light and dark.
These files are committed, so continuous integration needs no browser. When
a block changes, the build renders the missing file if it finds Mermaid CLI,
and otherwise warns and shows the Mermaid source:

```sh
npm install --prefix site @mermaid-js/mermaid-cli   # or set MMDC=/path/to/mmdc
python3 site/build.py                                # then commit site/diagrams/
```

`MMDC_PUPPETEER_CONFIG` may name a Puppeteer configuration. `shots.py` (needs
Playwright) takes screenshots and rewrites `static/og.png`; the build does not use it.

## Domain

In the repository: Settings, Pages, source "GitHub Actions", custom domain
`unifold.md`, then "Enforce HTTPS". With deployment from a workflow the
`CNAME` file in `_out/` is ignored; the setting counts. At the DNS provider
of `unifold.md`, as documented by GitHub
(<https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site>,
read 2026-10-07):

- `A` records for the apex: `185.199.108.153`, `185.199.109.153`,
  `185.199.110.153`, `185.199.111.153`
- `AAAA` records for the apex: `2606:50c0:8000::153`, `2606:50c0:8001::153`,
  `2606:50c0:8002::153`, `2606:50c0:8003::153`
- `CNAME` for `www` to `<owner>.github.io`, so that `www.unifold.md` redirects.

## Placeholders

- `REPO_URL`, `REPO_BRANCH` in `build.py` (`github.com/unifold-spec/unifold`, `main`).
- `<owner>` in the DNS record above.
