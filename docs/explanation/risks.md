# Risks and known limits of unifold

What can go wrong with the standard as it stands, what it knowingly does not do, and what would remove each limit. Planned work is not listed.

## Risks

- **No evidence from use.** The standard has been tried by its authors' agents on two examples and two open-source repositories. No study has measured whether it helps people or agents more than a well-kept root file; studies of related techniques point both ways ([reasoning](reasoning.md)). Removed by: trials on repositories that are not ours, with a measure agreed beforehand.
- **A first map is a proposal.** The skill `unifold-convert` has an agent choose the units and write the manifests. Nothing compares the map with the code, so a missed dependency and a poor choice of units are both left to the person who reads the result ([0034](../decisions/0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md)).
- **Stamps record a command, not a comparison.** A stamp says that somebody ran `unifold stamp`, not that `Says` was read against its source. Restated values outside `context.md` are not covered at all.
- **Mentions in prose are not checked.** The direction rules are enforced for links only; a sibling named in a sentence is left to review.
- **Agents are reached unevenly.** Of ten agents examined, Kiro and Aider do not find the stubs, and a skill is not always called when it would apply ([agents](../references/agents.md)).

## Known limits

- **A clean check is not a true map.** The map is not compared with the code. Code can use a unit that no need names, or stop using one that the wiring still connects; only tests and review find that. No tool judges a summary.
- **One provider per need.** A set of providers at the same time, such as plug-ins, is modelled as one capability of the unit that owns the collection, or the other way round: each plug-in needs the API.
- **The tree is the only structure.** A unit has one parent. Views across the folder tree, and configurations that choose between alternatives, are not modelled ([0010](../decisions/0010-units-follow-the-code-layout.md)).
- **A need used deep in the tree costs a line at every level.** It is declared in each unit on the way up and passed up by a line in each parent: a manifest shows everything its unit needs, and the wiring every connection, so that each can be read alone ([0048](../decisions/0048-write-every-connection-out-and-let-a-unit-wire-its-own-need.md)).
- **Flat systems put all wiring in one file.** For a set of services without intermediate folders, the root manifest holds every connection, one line per need and child ([0032](../decisions/0032-write-every-unit-out-in-the-wiring.md)).
- **`verified-by` is never run** ([0030](../decisions/0030-let-contract-and-verified-by-point-anywhere-in-the-project.md)).
- **Boxes are fully clickable only in the explorer.** On code hosts it depends on the host.
- **One repository.** Relations between repositories are needs of the root; no map across repositories is produced.
