# Risks and known limits of unifold

What can go wrong with the standard as it stands, what it knowingly does not do, and what would remove each limit. Planned work is not listed.

## Risks

- **No evidence from use.** The standard has been tried by its authors' agents on the three examples in this repository, and on two open-source repositories whose maps are not published here. No study has measured whether it helps people or agents more than a well-kept root file; studies of related techniques point both ways ([reasoning](reasoning.md)). Removed by: trials on repositories that are not ours, with a measure agreed beforehand.
- **A first map is a proposal.** The skill `unifold-convert` has an agent choose the units and write the manifests. A missed dependency and a poor choice of units are both left to the person who reads the result ([0016](../decisions/0016-one-tool-two-skills-and-the-way-in-for-agents.md)).
- **Context items can go stale.** An item says what a source from above means for the unit, and nothing notices when the source changes. `unifold impact FILE` lists the items to read again, but only when somebody runs it.
- **Mentions in prose are not checked.** The rule against sideways links is enforced for links only; a sibling named in a sentence is left to review.
- **Agents are reached unevenly.** Not every agent searches the folders in which the skill stubs are written, and a skill is not always called when it would apply ([agents](../references/agents.md)).

## Known limits

- **A clean check is not a true map.** The map is not compared with the code. Code can use a unit that no need names, or stop using one that the wiring still connects; only tests and review find that. No tool judges a summary.
- **One provider per need.** A set of providers at the same time, such as plug-ins, is modelled as one capability of the unit that owns the collection, or the other way round: each plug-in needs the API.
- **The tree is the only structure.** A unit has one parent. Views across the folder tree, and configurations that choose between alternatives, are not modelled ([0001](../decisions/0001-a-unit-is-a-folder-with-a-manifest.md)).
- **A need used deep in the tree costs a line at every level.** It is declared in each unit on the way up, as an empty entry that takes its summary and contract from the level above, and passed up by a line in each parent: a manifest shows everything its unit needs, and the wiring every connection, so that each can be read alone ([0002](../decisions/0002-needs-never-name-a-provider-the-unit-above-wires.md)).
- **Flat systems put all wiring in one file.** For a set of services without intermediate folders, the root manifest holds every connection, one line per need and child ([0002](../decisions/0002-needs-never-name-a-provider-the-unit-above-wires.md)).
- **The body of a contract is checked for its form, not its truth.** A part with a fenced block, examples and a fake can still be wrong; the examples are tests only once somebody runs them, and `unifold trace --active --strict` in the build fails for an example of an active unit that no test names ([0003](../decisions/0003-one-contract-per-connection.md)).
- **A derived decision can claim what its source does not say** ([0007](../decisions/0007-decisions-use-madr-agents-propose-people-accept.md)). The form shows the passage; review reads it.
- **Diagrams exist only in the explorer.** A reader on the code host sees the manifests and the documents, but no diagram ([0005](../decisions/0005-structure-is-generated-reasons-are-written.md)).
- **One repository.** Relations between repositories are needs of the root; no map across repositories is produced.
- **Tools for decision records are untried.** Whether [adr-tools](https://github.com/npryce/adr-tools) or [log4brains](https://github.com/thomvaill/log4brains) work on the `docs/decisions/` folder of a unit is not known.
