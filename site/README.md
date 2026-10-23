# The site unifold.md

`build.py` writes the whole site into `site/_out/` from `README.md`, `docs/references/*.md`, the skill and the examples. Nothing is converted by hand; `_out/` is not committed.

## Build

```sh
# build
uv run site/build.py
# build and check links, HTML, page weight
uv run site/build.py--check
# build and serve locally
uv run site/build.py --serve
```

| Address | File | From |
|---|---|---|
| `/` | `index.html` | `README.md`: the first sentence of the quote under the title becomes the title of the page, the rest of the quote the subtitle, and the text before `## Why` the introduction. The manifests of `## How it works` become the document beside the title; the rest of that section follows below, with its text block as a terminal and its root manifest as a drawn diagram. Known sections get their own layout (`What a unit has`, `Questions`, `Capabilities`, `Read next`, ...); any other section is shown as text under a heading with a coloured bar. |
| `/spec`, `/documents`, `/reasoning`, `/first-map`, ... | `spec.html`, ... | the reference chapters from `docs/references/`, the explanation files from `docs/explanation/` and the tutorial from `docs/tutorials/`; `/guide`, `/adopting` and `/design` redirect |
| `/spec.md`, ... | the same chapters as plain Markdown | |
| `/0.2/unifold.schema.json`, `/0.1/unifold.schema.json` | | the schema, at the current version and at 0.1, where manifests of 0.1 point; the build stops if it is missing |
| `/skill/SKILL.md`, `/skill/unifold-convert/SKILL.md`, `/llms.txt` | | the two skills; an index for agents |
| `/examples/<name>/` | `index.html` | every `examples/**/unifold.html` that exists |

GitHub Pages serves `spec.html` at `/spec`; `spec/index.html` would redirect to `/spec/`.

## Diagrams

A Mermaid block is replaced by an inline SVG from `site/diagrams/<hash>.svg` (hash of the Mermaid source), coloured by `style.css` for light and dark. These files are committed, so continuous integration needs no browser. When a block changes, the build renders the missing file if it finds Mermaid CLI, and otherwise warns and shows the Mermaid source:

```sh
npm install --prefix site @mermaid-js/mermaid-cli   # or set MMDC=/path/to/mmdc
python3 site/build.py                                # then commit site/diagrams/
```

`MMDC_PUPPETEER_CONFIG` may name a Puppeteer configuration. Files in `site/static/` are copied as they are: the heading font Patua One (`patua-one.woff2`, the Latin subset from [Fontsource](https://fontsource.org/fonts/patua-one) 5.3.0) with its licence, the SIL Open Font License. An `og.png` there would become the preview image of every page.

## Domain

In the repository: Settings, Pages, source "GitHub Actions", custom domain `unifold.md`, then "Enforce HTTPS". With deployment from a workflow the `CNAME` file in `_out/` is ignored; the setting counts. At the DNS provider of `unifold.md`, as documented by GitHub
(<https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site>,
read 2026-10-07):

- `A` records for the apex: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
- `AAAA` records for the apex: `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`
- `CNAME` for `www` to `<owner>.github.io`, so that `www.unifold.md` redirects.

## Placeholders

- `REPO_URL`, `REPO_BRANCH` in `build.py` (`github.com/unifold-spec/unifold`, `main`).
- `<owner>` in the DNS record above.
