# The site unifold.md

`build.py` writes the whole site into `site/_out/` from `README.md`, `docs/references/*.md`, the skill and the examples. Nothing is converted by hand; `_out/` is not committed.

## Build

```sh
# build
uv run site/build.py
# build and check links, HTML, page weight
uv run site/build.py --check
# build and serve locally
uv run site/build.py --serve
```

| Address | File | From |
|---|---|---|
| `/` | `index.html` | `README.md`: the first sentence of the quote under the title becomes the title of the page, the rest of the quote the subtitle, and the text before `## Why` the introduction. The manifests of `## How it works` become the document beside the title; the rest of that section follows below, with its text block as a terminal and its root manifest as a drawn diagram. Known sections get their own layout (`What a unit has`, `Questions`, `Capabilities`, `Read next`, ...); any other section is shown as text under a heading with a coloured bar. |
| `/spec/`, `/documents/`, `/reasoning/`, `/first-map/`, ... | `spec/index.html`, ... | the reference chapters from `docs/references/`, the explanation files from `docs/explanation/` and the tutorial from `docs/tutorials/`; `/guide`, `/adopting` and `/design` redirect |
| `/spec.md`, ... | the same chapters as plain Markdown | |
| `/0.3/unifold.schema.json` | | the schema, at the current version; the build stops if it is missing |
| `/skill/SKILL.md`, `/skill/assets/...`, `/skill/scripts/unifold.py`, `/skill/<name>/...`, `/llms.txt` | | `docs/skills/` copied as it is, templates and scripts included: the unifold skill at `/skill/`, every skill folder at `/skill/<name>/` (`/skill/unifold-convert/SKILL.md` among them), so that the relative links of a skill resolve; `--check` checks those links. `llms.txt` is an index for agents |
| `/examples/<name>/` | `index.html` | every `examples/**/unifold.html` that exists |
| `/search/` | `search/index.html` | the search: `search.js` searches `search.json` in the browser as you type, in the field in the header of every page and here, where all sections found are listed. The build writes that index with one entry per section of every chapter (down to `###`) and per band of the start page; `--check` checks its addresses. Without JavaScript the field in the header leads here. |
| `/favicon.svg`, `/favicon.ico`, `/apple-touch-icon.png` | | the mark, drawn by the build from the corners in `MARK`: an SVG with light and dark colours, an ICO with 16, 32 and 48 pixels for browsers without SVG icons, a PNG for home screens |

Every page is a folder with an `index.html`, so that any web server serves it; a link without the trailing slash, such as `https://unifold.md/spec`, is redirected by the server.

## Diagrams

A Mermaid block is replaced by an inline SVG from `site/diagrams/<hash>.svg` (hash of the Mermaid source), coloured by `style.css` for light and dark. These files are committed, so continuous integration needs no browser. When a block changes, the build renders the missing file if it finds Mermaid CLI, and otherwise warns and shows the Mermaid source:

```sh
npm install --prefix site @mermaid-js/mermaid-cli   # or set MMDC=/path/to/mmdc
uv run site/build.py                                 # then commit site/diagrams/
```

`MMDC_PUPPETEER_CONFIG` may name a Puppeteer configuration. Files in `site/static/` are copied as they are: the heading font Patua One (`patua-one.woff2`, the Latin subset from [Fontsource](https://fontsource.org/fonts/patua-one) 5.3.0) with its licence, the SIL Open Font License. An `og.png` there would become the preview image of every page.

## Deployment

The workflow [deploy.yml](../.github/workflows/deploy.yml) builds the site, checks it and uploads `_out/` with rsync over SSH to the host that serves `unifold.md`; the DNS of the domain points at that host. It runs for every push to main, for a tag `v*` and by hand from the Actions tab. The host, user, web root and port are repository variables, the private key of the deploy user is the secret `DEPLOY_KEY`; the head of the workflow lists them. The workflow [check.yml](../.github/workflows/check.yml) runs the tests, the examples and `build.py --check` on every push.
