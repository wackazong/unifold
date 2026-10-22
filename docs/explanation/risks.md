# Risks and known limits of unifold

What can go wrong with the standard as it stands, what it knowingly does not do, and what would remove each limit. Planned work is not listed here; the decisions and the front page say what is a draft.

## Risks

- **No evidence from use.** The standard has been tried by its authors' agents on two examples and two open-source repositories. No study has measured whether it helps people or agents more than a well-kept root file; studies of related techniques point both ways ([reasoning](reasoning.md)). Removed by: trials on repositories that are not ours, with a measure agreed beforehand.
- **Every decision is still proposed.** No person has accepted any of the decisions of this draft, although the root unit says `active`. Removed by: a review that accepts or rejects each.
- **A first map is a proposal.** The skill `unifold-convert` has an agent choose the units and write the manifests. The comparison with code catches a missed dependency, not a poor choice of units; a person must read the result ([0034](../decisions/0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md)).
- **Equal names connect.** Implicit pass-up joins a child's need to a parent's need of the same name, also when that was not meant ([0024](../decisions/0024-pass-needs-up-by-name-and-draw-shared-connections-once.md)). `unifold show` marks such connections.
- **Stamps record a command, not a comparison.** A stamp says that somebody ran `unifold stamp`, not that `Says` was read against its source. Restated values outside `context.md` are not covered at all.
- **Mentions in prose are not checked.** The direction rules are enforced for links only; a sibling named in a sentence is left to review.
- **Agents are reached unevenly.** Of ten agents examined, Kiro and Aider do not find the stubs, and a skill is not always called when it would apply ([agents](../references/agents.md)).
- **The tool is not published as a package yet.** Until it is, it runs from a clone or from the installed skill.

## Known limits

- **A clean check is not a true map.** The comparison with code works per pair of units: it cannot tell which capability of a provider is used, one wired need covers every dependency between two units, and it sees only what the extractors or a supplied list contain. No tool judges a summary.
- **One provider per need.** A set of providers at the same time, such as plug-ins, is modelled as one capability of the unit that owns the collection, or the other way round: each plug-in needs the API.
- **The tree is the only structure.** A unit has one parent, and a need has one provider at a time. Views across the folder tree, sets of plug-ins, and configurations that choose between alternatives are not modelled ([0010](../decisions/0010-units-follow-the-code-layout.md)).
- **A need used deep in the tree is declared at every level.** Implicit pass-up removes the wiring lines, not the declarations: a manifest shows everything its unit depends on, so that the unit can be understood alone.
- **Flat systems put all wiring in one file.** For a set of services without intermediate folders, the root manifest holds every connection, one line per need and child ([0032](../decisions/0032-write-every-unit-out-in-the-wiring.md)).
- **`verified-by` is never run**
  ([0030](../decisions/0030-let-contract-and-verified-by-point-anywhere-in-the-project.md)).
- **Boxes are fully clickable only in the explorer.** On code hosts it depends on the host.
- **One repository.** Relations between repositories are needs of the root; no map across repositories is produced.
