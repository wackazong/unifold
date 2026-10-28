# Three commands

This lesson is for a developer who has cloned the unifold repository and wants to see what the reference tool says about a project. You follow one unit, the plug-in `unicode`, through three commands. Work in the folder `examples/slugline`, with `unifold` set as the alias from [README.md](../../README.md).

1. Run `unifold check`. It prints one line:

   ```console
   $ unifold check
   4 unit(s): 0 error(s), 0 warning(s), 0 info
   ```

   The map is consistent: every need of the four units is wired, and both sides of each connection name the same contract.

2. Run `unifold show plugins/unicode`. It prints the unit, its responsibility and kind, what it does not do, its capability and its need, and the scenario that passes through it:

   ```console
   $ unifold show plugins/unicode
   unit      unicode  (plugins/unicode)
   does      Transliterates Latin letters with diacritics to ASCII
   status    active · kind logic
   not       the rules of a slug; it answers one character at a time
   manifest  plugins/unicode/unifold.yaml
   parent    slugline
   children  none
   capabilities
     transliteration (library): Replaces Latin letters that have diacritics, and ligatures, by ASCII letters  contract docs/references/transliteration.md
         used by cli as need 'transliteration'
   needs
     plugin-api (library): The trait a transliteration plug-in implements  contract docs/references/plugin-api.md
         provided by core capability 'plugin-api'
   scenario  slug-from-arguments: The command turns its arguments into one slug with the plug-in  (held by the root)
   files     plugins/unicode/README.md
   ```

   Find the two indented lines: `cli` uses the capability, and `core` provides the need. The last line names the scenario of the root whose hops pass through this unit; its generated diagram is `docs/diagrams/scenario-slug-from-arguments.md`.

3. Run `unifold capability plugins/unicode plugin-api`. It prints both ends of that one connection:

   ```console
   $ unifold capability plugins/unicode plugin-api
   --- plugins/unicode needs 'plugin-api' (library): The trait a transliteration plug-in implements
       contract: docs/references/plugin-api.md
       (no section for it in README.md)

   --- core capabilities 'plugin-api' (library): The trait a transliteration plug-in implements
       contract: docs/references/plugin-api.md
       (no section for it in README.md)
   ```

   Both ends name the same contract, `docs/references/plugin-api.md`. Neither `README.md` has a section for the entry: the summary and the contract say everything, so the command would print the section only where one adds to them.

You have read the map of slugline without opening a manifest. Next, [break the map](break-the-map.md).
