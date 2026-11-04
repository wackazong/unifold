# Contributing to unifold

Changes are welcome.

## Corrections

A change that alters no rule, such as a typing mistake, a clearer sentence or a broken link, is a plain pull request.

## Changing the standard

1. Write a decision record in `docs/decisions/` with the next free number and `status: proposed`: the problem, the options, the choice, and the good and bad consequences. Start from the [template](docs/skills/unifold/assets/decision.template.md), and add a row to the [index](docs/decisions/index.md).
2. Change the standard, [spec.md](docs/references/spec.md), [spec-wiring.md](docs/references/spec-wiring.md) or [spec-conformance.md](docs/references/spec-conformance.md), if the change concerns manifests, wiring or generated files; otherwise the chapter that covers it ([documents.md](docs/references/documents.md) says which kind holds what). Every hand-written page stays within the word limit; `rules.md` is generated.
3. If the tool reports the rule, change the rule table in `docs/skills/unifold/scripts/unifold.py` and the tool, and add a case to [tests/conformance.py](tests/conformance.py). The site build writes [rules.md](docs/references/rules.md) from the table; never edit that file by hand.
4. Change the skills and their templates if the procedure for agents changes.
5. Run everything:

   ```sh
   uv run tests/conformance.py
   uv run docs/skills/unifold/scripts/unifold.py check --fix examples/slugline
   uv run docs/skills/unifold/scripts/unifold.py check --fix examples/serial-line
   uv run docs/skills/unifold/scripts/unifold.py check --fix examples/plantwatch
   uv run site/build.py
   uv run site/build.py --check
   ```

   The workflow `check` runs the same commands, with `--strict` in place of `--fix`, on every push and pull request. `examples/serial-line` is a copy of the example of [maike](https://github.com/wackazong/maike), which checks its original against this copy at the version of unifold it pins; a change here reaches maike when maike moves its pin.

A maintainer accepts the decision by setting `status: accepted` and naming the decision-makers.

## Releasing

A maintainer releases the tool:

1. Set the new version in `pyproject.toml`, in `TOOL_VERSION` of `docs/skills/unifold/scripts/unifold.py` and in the two outputs of [tool-json.md](docs/references/tool-json.md) that print it, and commit the three files as `chore(release): unifold X.Y.Z`.
2. Tag the commit `vX.Y.Z` and push the branch and the tag.
3. The workflow `publish` checks that the tag names the version, runs the conformance tests, builds the package, runs the built wheel and uploads it to PyPI through a trusted publisher, once a maintainer approves the environment `pypi`. The workflow `deploy` rebuilds the site.

## Commands

```sh
uv run tests/conformance.py                                     # test the tool
uv run docs/skills/unifold/scripts/unifold.py check examples/plantwatch    # check an example
uv run docs/skills/unifold/scripts/unifold.py explore examples/plantwatch  # open its explorer
uv run site/build.py --check                                  # build the site and check its links
```

## Rules for the text

- Write in the [Markdown style](docs/references/writing.md#markdown-style) of the standard: language that a human reader understands easily, at most 1,500 words per file, one line per paragraph, one term for one thing, one home for every fact.
- Keep the [invariants](docs/explanation/invariants.md): where chapters may link, where rule ids appear, and that every claim about a tool, a study or a product links to its source.

## Licence of contributions

Contributions are dual licensed under MIT or Apache-2.0, as stated in the [README](README.md).
