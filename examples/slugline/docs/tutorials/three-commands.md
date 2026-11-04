# Three commands

This lesson is for a developer who has cloned the unifold repository and wants to see what the reference tool says about a project. You follow one unit, the plug-in `unicode`, through three commands. Work in the folder `examples/slugline`, with `unifold` set as the alias from [README.md](../../README.md).

1. Run `unifold check`. It prints one finding and a summary line:

   ```console
   $ unifold check
   info N4 docs/references/transliteration.md:36: part 'transliterate' is used by no hop of a scenario
       fix: Write the scenario that uses the part, or remove the part from the contract.
   4 unit(s): 0 error(s), 0 warning(s), 1 info  [N4×1]
   ```

   The map is consistent: every need of the four units is wired, and both sides of each connection name the same contract. The `info` line is a hint, not a fault: the part `transliterate` of the contract `transliteration` appears in no scenario, because the unit that calls a plug-in, `core`, reaches it over the connection `plugin-api` and not over this one.

2. Run `unifold show plugins/unicode`. It prints the unit, its responsibility and kind, what it does not do, its capability and its need, and the scenario that passes through it:

   ```console
   $ unifold show plugins/unicode
   unit      unicode  (plugins/unicode)
   does      Transliterates Latin letters with diacritics to ASCII
   status    active · kind logic · runs as library
   not       the rules of a slug; it answers one character at a time
   manifest  plugins/unicode/unifold.yaml
   parent    slugline
   children  none
   capabilities
     transliteration: Replaces Latin letters that have diacritics, and ligatures, by ASCII letters  contract docs/references/transliteration.md
         used by cli as need 'transliteration'
   needs
     plugin-api: The trait a transliteration plug-in implements  contract docs/references/plugin-api.md
         provided by core capability 'plugin-api'
   scenario  slug-from-arguments: The command turns its arguments into one slug with the plug-in  (held by the root)
   files     plugins/unicode/README.md
   ```

   Find the two indented lines: `cli` uses the capability, and `core` provides the need. The last line names the scenario of the root whose hops pass through this unit; `unifold scenario . slug-from-arguments` draws it.

3. Run `unifold capability plugins/unicode plugin-api`. It prints both ends of that one connection:

   ```console
   $ unifold capability plugins/unicode plugin-api
   --- plugins/unicode needs 'plugin-api': The trait a transliteration plug-in implements
       contract: docs/references/plugin-api.md

   --- core capabilities 'plugin-api': The trait a transliteration plug-in implements
       contract: docs/references/plugin-api.md
   ```

   Both ends name the same contract, `docs/references/plugin-api.md`. The summary and the contract say everything a reader needs about the connection.

You have read the map of slugline without opening a manifest. Next, [break the map](break-the-map.md).
