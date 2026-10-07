# Living with what a repository already has

Most repositories that adopt youmedoc are not empty. This chapter says how the
standard relates to things that are usually there already.

## The README and package registries

A unit's `README.md` is often published: by a code host as the front page of
the folder, by a package registry as the page of the package. YAML front
matter shows up there as a table or as stray text.

A unit therefore keeps its manifest in a file `unit.yaml` next to the
`README.md` ([manifest.md](manifest.md)), and the `README.md` is plain
Markdown. Front matter is an option for units whose `README.md` is read
only inside the repository.

A published `README.md` usually names the project it belongs to and links to
its home page, licence, user documentation and issue tracker. Write these as
full URLs, for example in a section `## Project`. Relative links upward are
not allowed in a unit, and they would be dead on a registry anyway.

The root `README.md` stays the front page of the project. It may contain
whatever a front page needs: installation, status, how to contribute, licence
([unit-files.md](unit-files.md)).

## An existing doc or docs folder

youmedoc uses a folder named `doc/`, singular, in every unit. Many projects
have a `docs/` folder at the root that holds the source of a documentation
site. The two do not collide: `docs/` remains what it is.

If a unit already has a `doc/` folder with other content, the checker manages
only the entries the standard defines ([doc-folder.md](doc-folder.md)) and
reports anything else as a warning (`S5`) without checking it.

## Documentation sites

A site built with mdBook, Docusaurus, MkDocs or a similar tool is for users of
the product. youmedoc documents are for the people and agents who work on the
code. Keep both.

- Do not copy text between them. Link from the site to a unit's `README.md`
  on the code host where that helps.
- API reference generated from code belongs to the site or to the language's
  own documentation tool, not to `doc/references/`.

## Existing decision records

Decision records that follow MADR or a similar format move into
`doc/decisions/` of the unit they concern, renamed to `NNNN-short-title.md`
with numbers local to that unit. Records that concern the whole project go to
the root unit. Keep their status and date.

## Owners files

The manifest key `owner` ([manifest.md](manifest.md)) names the team or
person responsible for a unit. It is inherited by the units below until one
of them names another owner. A CODEOWNERS file can be derived from it:
one line per unit that sets `owner`, with the unit's path.

A wiring line connects two units. A change to it concerns the owners of both.

## Contributing, licence, changelog

`CONTRIBUTING.md`, licence files, `CHANGELOG.md`, `SECURITY.md` and similar
files stay at the repository root. They are not managed by youmedoc and the
writing rules do not apply to them.

- The root `README.md` links to them.
- A unit below the root does not link to them, because that would be an
  upward link. A unit that is published on its own carries its own licence
  file, as packaging requires anyway.
- `CONTRIBUTING.md` SHOULD tell contributors that the project uses youmedoc
  and what that asks of them. A text to paste is in the
  [write-docs](../../skills/write-docs/SKILL.md) skill.

## Instruction files and skill folders of coding agents

- Agents that load a file named differently from `AGENTS.md` need a bridge
  file that points to it. youmedoc does not define it.
- Agents discover skills in folders of their own. youmedoc keeps skills in
  `doc/skills/` of each unit and announces them in `AGENTS.md`. A project MAY
  additionally expose them where its agent looks, for example by symbolic
  links. Then skill names MUST be unique in the project.

## Generated files in version control

Generated diagrams and decision indexes are committed, so that a reader on the
code host sees them. To keep them out of the way:

- mark `doc/diagrams/*.md` and `doc/decisions/index.md` as generated for the
  code host, for example with `linguist-generated` in `.gitattributes`, so
  that reviews collapse them;
- run the generator before every commit or in a pre-commit hook
  ([checker.md](checker.md)).

## Several repositories

A youmedoc project is one folder tree. Things in other repositories are the
outside world: the root unit states them as needs.

- If another repository is itself a youmedoc project, say so in the summary
  of the need and link to its `README.md` by URL in the root `README.md`.
- A repository that is embedded in the tree, for example as a submodule, and
  has its own root manifest is a nested project. The outer project links only
  to its `README.md` and wires nothing into it.

## Folders that must not be scanned

Third-party code inside the repository may contain manifests of its own. List
such folders under `ignore` in the root manifest ([manifest.md](manifest.md)).
Folders whose name starts with a dot are never scanned.
