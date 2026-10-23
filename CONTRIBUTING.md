# Contributing to unifold

Changes are welcome.

## Corrections

A change that alters no rule, such as a typing mistake, a clearer sentence or a broken link, is a plain pull request.

## Changing the standard

1. Write a decision record in `docs/decisions/` with the next free number and `status: proposed`: the problem, the options, the choice, and the good and bad consequences. Start from the [template](docs/skills/unifold/assets/decision.template.md), and add a row to the [index](docs/decisions/index.md).
2. Change [spec.md](docs/references/spec.md) if the change concerns manifests, wiring, generated files or the comparison with code; otherwise the chapter that covers it ([documents.md](docs/references/documents.md) says which kind holds what). The standard stays on one page of at most 200 lines.
3. If the tool reports the rule, change [rules.md](docs/references/rules.md), the rule table in `docs/skills/unifold/scripts/unifold.py`, and the tool, and add a case to [tests/conformance.py](tests/conformance.py).
4. Change the skills and their templates if the procedure for agents changes.
5. Run everything:

   ```sh
   python3 tests/conformance.py
   python3 docs/skills/unifold/scripts/unifold.py check --fix examples/slugline
   python3 docs/skills/unifold/scripts/unifold.py check --fix examples/plantwatch
   python3 site/build.py --check
   ```

A maintainer accepts the decision by setting `status: accepted` and naming the decision-makers.

## Rules for the text

- Write in the [Markdown style](docs/references/writing.md#markdown-style) of the standard: at most 200 lines per file, one line per paragraph, short sentences, one term for one thing, one home for every fact.
- Keep the [invariants](docs/explanation/invariants.md): where chapters may link, where rule ids appear, and that every claim about a tool, a study or a product links to its source.

## Licence of contributions

Contributions are dual licensed under MIT or Apache-2.0, as stated in the [README](README.md).
