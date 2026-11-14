# Three commands

This lesson is for a developer who has cloned the unifold repository and wants to see what the reference tool says about a project. You follow one unit, the plug-in `unicode`, through three commands. Work in the folder `examples/slugline`, with `unifold` set as the alias from [README.md](../../README.md).

1. Run `unifold check`. It prints one summary line:

   ```console
   $ unifold check
   4 unit(s): 0 error(s), 0 warning(s), 0 info
   ```

   The map is consistent: every need of the four units is wired, both sides of each connection name the same contract, and every operation and event of every contract is used by a hop of a scenario.

2. Run `unifold show plugins/unicode`. It prints the unit, its responsibility and kind, what it does not do, its two capabilities, and the scenarios that pass through it:

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
     plugin-api: The trait of a transliteration plug-in, for Latin letters  contract docs/references/plugin-api.md
         used by core as need 'plugin-api'
   scenario  slug-from-arguments: The command turns its arguments into one slug with the plug-in  (held by the root)
   scenario  library-call: A program calls the library with the Latin plug-in  (held by the root)
   files     plugins/unicode/README.md
   ```

   Find the two lines that start with `used by`: `cli` uses the capability `transliteration`, and `core` uses the capability `plugin-api`. The lines `scenario` name the scenarios of the root whose hops pass through this unit; the explorer draws them.

3. Run `unifold capability plugins/unicode plugin-api`. It prints both ends of that one connection:

   ```console
   $ unifold capability plugins/unicode plugin-api
   --- plugins/unicode capabilities 'plugin-api': The trait of a transliteration plug-in, for Latin letters
       contract: docs/references/plugin-api.md

   --- core needs 'plugin-api': A transliteration plug-in, asked about each character outside ASCII
       contract: docs/references/plugin-api.md
       optional
   ```

   Both ends name the same contract, `docs/references/plugin-api.md`. The line `optional` says that `core` works without a plug-in too, as `slugify` does. The summaries and the contract say everything a reader needs about the connection.

You have read the map of slugline without opening a manifest. Next, [break the map](break-the-map.md).
