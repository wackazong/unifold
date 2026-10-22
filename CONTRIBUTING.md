# Contributing to unifold

unifold is a draft. Changes are welcome.

## Corrections

A change that alters no rule, such as a typing mistake, a clearer sentence
or a broken link, is a plain pull request.

## Changing the standard

1. Write a decision record in `docs/decisions/` with the next free number
   and `status: proposed`: the problem, the options, the choice, and the
   good and bad consequences. The template is in
   [docs/skills/unifold/assets/](docs/skills/unifold/assets/decision.template.md).
2. Change [spec.md](docs/references/unifold/spec.md) if the change concerns
   level `core`, otherwise the reference chapter or the explanation file
   that covers it ([documents.md](docs/references/unifold/documents.md)
   says which kind holds what). The standard stays on one page of at most
   200 lines.
3. If the tool reports the rule, change
   [rules.md](docs/references/unifold/rules.md), the tool in
   `docs/skills/unifold/scripts/unifold.py`, and add a case to
   [tests/conformance.py](tests/conformance.py).
4. Change the skill and its templates if the procedure for agents changes.
5. Run everything:

   ```sh
   python3 tests/conformance.py
   python3 docs/skills/unifold/scripts/unifold.py check --fix
   python3 docs/skills/unifold/scripts/unifold.py check
   ```

   and run `check` in each example, which is a project of its own.

A maintainer accepts the decision by setting `status: accepted` and naming
the decision-makers.

## Rules for the text

- Every Markdown file has at most 200 lines. Prose is wrapped at about 78
  characters.
- Plain, precise English that a non-native reader and an agent parse
  equally well. One home for every fact; other places link to it.
- The chapters in `docs/references/unifold/` link only to each other, to
  the explanation and tutorial files of this repository, and to full URLs.
  The skill links to the site by `https://unifold.md/...` URL.
- Prose does not cite rule IDs; it links to `rules.md`.
- A claim about a tool, a study or a product carries a link to its source.

## Licence of contributions

Contributions are dual licensed under MIT or Apache-2.0, as stated in the
[README](README.md).
