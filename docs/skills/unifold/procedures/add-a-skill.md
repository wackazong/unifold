# Add a skill

1. Write `docs/skills/<name>/SKILL.md` in the lowest unit in which the whole procedure happens, from [SKILL.template.md](../assets/SKILL.template.md). `name` equals the folder name.
2. Run `unifold check --fix`. It writes the stubs through which agents find the skill, where `.agents/skills/` and `.claude/skills/` exist. `check --fix` names the stub ([agents](https://unifold.md/agents#where-skills-are-found)).
3. Tell the human that the skill is new and unreviewed.
4. [Finish](../SKILL.md#4-finish).
