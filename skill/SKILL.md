---
name: zonca.dev
description: Create a new blog post on zonca.dev using Jules.
---

# zonca.dev blog post skill

Send the entire content you want to post about into Jules, then let Jules handle it from there.

## Usage

```bash
jules new --repo zonca/zonca.dev "<paste all the useful content, notes, links, and context for the post here>"
```

Jules will read the project's `AGENTS.md` for instructions on how to format and create the post, then commit and push the new branch.

## PR creation is MANDATORY — Jules must not stop before it

Jules often commits and pushes a branch but **stops before creating the pull request**, leaving the work unmerged. The repo's `AGENTS.md` "Publishing workflow" is ambiguous ("push to main, or open a PR"), which lets Jules consider the job done after push. Do not rely on the repo instructions to produce the PR — force it in the prompt.

**Always wrap the task like this** (never paste content alone):

```bash
jules new --repo zonca/zonca.dev "<all content, notes, links, context for the post. After creating the blog post: create a new branch from main, commit, and push it. THEN, as the FINAL step, create and open a pull request using: gh pr create --title '<concise title>' --body '<summary>'. Do NOT stop before opening the PR — the task is only complete once the PR is open and its URL is reported back. Opening the PR is the very last action; don't stop after commit+push.\""
```

**Completion rule:** the task is complete ONLY when (1) the new branch is pushed AND (2) the PR has been created and its URL reported back. If Jules returns without a PR URL, treat it as incomplete: send a follow-up instructing it to open the PR (or report the pushed branch to Andrea for manual merge).
