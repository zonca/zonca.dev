---
categories:
- github
date: '2025-10-20'
layout: post
title: Auto-merge GitHub Pull Requests After GitHub Actions Pass
---

Pull request auto-merge is a small feature that keeps teams from babysitting green builds. Once every required check is green, GitHub merges the PR for you—no extra clicks, no late-night merges. Here is how to get it running safely with GitHub Actions.

## Prerequisites

You need **maintainer access** (admin or repository maintainer) to change repository settings. Auto-merge depends on branch protection rules, so make sure you already have a default branch (for example, `main`) and that your GitHub Actions workflows have run at least once so their check names appear in the UI.

## 1. Allow auto-merge on the repository

1. Open `Settings → General`.
2. Scroll to **Pull Requests** and enable **Allow auto-merge**.

This only needs to be done once per repository. Without it the **Auto-merge** button will never appear on PRs.

## 2. Require the GitHub Actions checks in a branch protection rule

1. Go to `Settings → Branches`.
2. Add or edit the branch protection rule for your main integration branch (for example, `main`).
3. (Optional) Turn on **Require a pull request before merging** and set **Require approvals** to `1` if you want at least one review before auto-merge.
4. Check **Require status checks to pass before merging**.
5. In the status check picker, select every GitHub Actions workflow that must be green.
6. (Recommended) Enable **Require branches to be up to date before merging** so the PR is rebased/merged only when it matches the latest base branch.
7. Save the rule.

Once this rule is in place, GitHub knows exactly which GitHub Actions jobs must succeed before it is allowed to merge automatically.

## 3. Turn on auto-merge from a pull request

When a contributor opens a PR against the protected branch:

1. Scroll to the merge box and click **Enable auto-merge**.
2. Choose the merge strategy you want GitHub to apply (merge commit, squash, or rebase). The available options depend on the repository’s merge policy.
3. Confirm.

GitHub now keeps the PR queued. When the branch has the required approvals (if any) and every required GitHub Actions check is green, the merge happens automatically. If **Require branches to be up to date** is active, GitHub may ask the author to `Update branch` before it flips the merge switch.

### CLI shortcut

You can enable the same behavior from the terminal:

```bash
gh pr merge <pr-number> --auto --squash
```

Adjust the merge strategy flag (`--squash`, `--merge`, `--rebase`) to match your repository defaults.

## Troubleshooting checklist

- **Auto-merge button missing**: confirm the repository-level **Allow auto-merge** toggle is on and that you have permission to merge.
- **Specific workflow missing from the status check list**: trigger the GitHub Actions workflow at least once; only executed jobs appear as selectable checks.
- **Auto-merge stuck on “Waiting for status to be reported”**: the branch protection rule references a stale check name. Update the rule to match the new workflow or job name.
- **Dependabot PRs**: enable **Allow auto-merge** in the repository settings and grant Dependabot permission to auto-merge, or add `github.actor == "dependabot[bot]"` to your policies if you are using GitHub’s CodeQL or security features.

Once everything is wired up, teams can queue PRs as soon as reviews are done. GitHub takes care of merging the moment your Actions pipeline says the coast is clear.
