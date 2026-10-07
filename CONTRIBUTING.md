# Contributing to unifold

unifold is a draft. Changes are welcome and are made the way the standard
itself asks for.

## Corrections

A change that alters no rule, such as a typing mistake, a clearer sentence or
a broken link, is a plain pull request. It needs no decision record.

## Proposing a change to the standard

1. Write a decision record in `doc/decisions/` with the next free number and
   `status: proposed`: the problem, the options, the choice, the good and bad
   consequences. Use the template in `doc/skills/write-docs/assets/`.
2. Change the chapters in `doc/references/unifold/` that state the rule.
3. If the rule is checked by the tool, change
   `doc/skills/check-docs/scripts/unifold.py` and add a case to
   `tests/conformance.py`. A rule exists in three places that must agree:
   the chapter, the rule table, the tool.
4. Change the skills and templates if the procedure for agents changes.
5. Apply the change to `examples/plantwatch` and refresh its copy of the
   standard.
6. Run everything:

   ```sh
   python3 tests/conformance.py
   python3 doc/skills/check-docs/scripts/unifold.py generate
   python3 doc/skills/check-docs/scripts/unifold.py check --strict
   python3 doc/skills/check-docs/scripts/unifold.py init examples/plantwatch
   python3 doc/skills/check-docs/scripts/unifold.py generate examples/plantwatch
   python3 doc/skills/check-docs/scripts/unifold.py check --strict examples/plantwatch
   python3 doc/skills/check-docs/scripts/unifold.py generate examples/slugline
   python3 doc/skills/check-docs/scripts/unifold.py check --strict --deps examples/slugline/deps.json examples/slugline
   ```

A maintainer accepts the decision by setting `status: accepted` and naming
the decision-makers.

## Rules for the text

- The files in `doc/references/unifold/` and the three skills are copied
  into other projects. Links inside them stay within these folders.
- Every Markdown file has at most 200 lines.
- Claims about tools, studies or products carry a link to their source.

## Licence of contributions

Contributions are dual licensed under MIT or Apache-2.0, as stated in the
`README.md`.
