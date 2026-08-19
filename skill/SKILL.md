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

After pushing the branch, Jules **must** create and open the pull request — do not stop after committing and pushing. Use `gh pr create` (or `jules`' own PR flow) to open the PR with a descriptive title and body. The task is only complete once the PR has been created and its URL is reported to the user.
