---
title: "Keeping interactive tutorials up to date with an orchestrator and AI subagents"
date: 2026-11-03
categories: [ai, llm, automation, documentation]
layout: post
description: "How to keep browser-based tutorials working with an orchestrator, a browser executor and a documentation improver, instead of hoping nobody follows the outdated step."
---

Interactive tutorials are the documentation that rots fastest, and they are also the hardest to keep
honest. A unit test tells you that a function broke. Nothing in your CI tells you that the first
step of your tutorial now sends the reader to a login page that does not exist, or that the console
wizard moved a button, or that the version your notebook pinned is two releases behind. I have been
fighting this problem with the CloudBank Showcase tutorials, where each tutorial asks the reader to
click through a real cloud console, and the approach that finally worked is a small multi-agent
system: one agent walks the tutorial in a real browser, another one fixes the documentation, and an
orchestrator decides when to stop.

This post is about the general pattern rather than that one project, because the same shape works
for any interactive tutorial: a Jupyter notebook you hand to students, a workshop walkthrough, a
README that asks the reader to click through a dashboard.

## Why interactive tutorials need a different kind of testing

The dependencies that break a tutorial live outside the repository. They are the login chain of a
research portal, the identity provider you have to pick in a dropdown, the name of the button that
creates a cluster, the version of a Helm chart, the IP address in the sample output block. A
`pytest` run cannot see any of it.

There is a second, subtler problem: documentation fails on a *fresh* account, not on the author's
account. The author's project already has the bucket, the service account and the disks that the
guide creates, so the guide "works" for them and breaks for everyone else. The one environment that
reproduces the real user experience is a new one, and creating a new one is exactly what nobody has
time to do by hand every quarter.

Browser automation can drive the clicks, but it cannot tell you that the instruction is now wrong.
That judgement is the part that needs a language model: someone (or something) has to read the page,
decide what a beginner would experience, and write it down. So the useful system is not "a bot that
clicks", it is "a bot that clicks, plus a reader that judges, plus a mechanism that turns the
judgement into a documentation fix".

## Three roles, separated by capability

The system I use has three roles. What matters is not the prompt of each role, it is the capability
each role has and, above all, the capability each role is denied.

| Role | Owns | Must never |
| --- | --- | --- |
| Orchestrator | Plans the rounds, dispatches the work, judges the severity of findings, decides when to stop, talks to the human when needed | Edit the tutorial |
| Executor (browser) | Walks the tutorial literally in the live console, captures evidence, cleans up what it created | Edit the tutorial |
| Improver (docs) | Reads the report, edits the documentation, researches version drift, commits and pushes | Touch the live console |

The "must never" column is the whole design. An executor that is also allowed to edit the
documentation will, sooner or later, "fix" the tutorial to match what it just did, and a failing
step quietly turns into a rewritten instruction. An improver that is allowed to run the console will
verify its own fix by doing something easier than what the guide actually says. And an orchestrator
that edits the docs itself leaves no trace of which finding produced which change, so the next round
has no clean input.

## Enforce the roles with permissions, not with instructions

"Do not edit any file" is a request. A denied `edit` permission is a fact. In OpenCode you can
declare subagents as Markdown files with a permission block, and use that to make the roles real:

```markdown
---
description: Tests the tutorial by following it literally as a new user
mode: subagent
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: allow
---
```

```markdown
---
description: Fixes the tutorial where a tester report shows it disagrees with reality
mode: subagent
permissions:
  - action: edit
    resource: "*"
    effect: allow
  - action: shell
    resource: "*"
    effect: deny
---
```

The rules are an ordered list and the last matching one wins, so a broad `deny` followed by narrow
`allow` entries is the way to carve out exceptions. In the real tutorial loop the improver does need
to run `git`, so its shell rule becomes a narrow allowlist instead of a blanket deny:

```yaml
permissions:
  - action: shell
    resource: "*"
    effect: deny
  - action: shell
    resource: "git status *"
    effect: allow
  - action: shell
    resource: "git add *"
    effect: allow
  - action: shell
    resource: "git commit *"
    effect: allow
```

Two details from the [permissions documentation](https://opencode.ai/v2/docs/permissions) are worth
knowing. A custom subagent uses its own permissions, not a subset of its parent's, so the executor
can drive a browser even when the orchestrator cannot. And the parent's `subagent` permission
decides which children the orchestrator is allowed to launch at all, which is the place to put the
rule "the orchestrator may start the executor and the improver, and nothing else".

## Give every round a fresh context, and pass no hints

Subagents start with a fresh context, which is exactly what you want: the tester must not inherit
the improver's belief about what the tutorial says. The subtle part is the message the orchestrator
writes to the next round. If it summarizes the previous report, or mentions what was fixed, the
tester inherits the story it is supposed to check and starts to confirm it. The rule I settled on is
to pass the report verbatim and add nothing else, literally "Test the tutorial" and nothing more.

This is not theoretical. In a rehearsal of the smaller version of this loop, the second-round tester
was given a hint about what had just been fixed, and it reported PASS on a step that was still
broken. Removing the hint fixed it.

## The interface between the roles is a machine-readable report

Each round produces one JSON file with a fixed schema. This is the contract between the roles, and
it buys three things: the run is resumable after a crash or a human interruption, the orchestrator
can decide "clean" or "not clean" mechanically, and you can diff two rounds to see exactly what
changed.

```json
{
  "round": 2,
  "phase": "live_walkthrough",
  "results": [
    {
      "guide": "1_access_gcp.md",
      "status": "fail",
      "severity": "critical",
      "detail": "The guide sends the reader to a Google account chooser that never appears",
      "evidence": "evidence/r2_login_wall.png"
    }
  ],
  "resources": {"cluster": "toy-hydro-cluster", "project_id": "..."},
  "actual_versions": {"kubernetes": "v1.36.4-gke.1495002"},
  "cleaned_up": true,
  "needs_human": null,
  "summary": "..."
}
```

Keep the reports private (they contain resource identifiers and console details) and keep the
*process* public. I wrote the reusable version of this process as a playbook that any project can
copy, with the provider-specific details deliberately left out: [the CloudBank Showcase verification
playbook](https://github.com/cloudbank-project/cloudbank_showcase/blob/main/verification/README.md).

## Severity, stop rules, and the run budget

Findings get a severity that describes the damage to the reader, not the difficulty for the agent:

- **critical**: the step fails as written, the reader cannot finish.
- **major**: the step works but misleads, or fails on a fresh account (wrong ordering, stale pin,
  missing prerequisite).
- **minor**: copy and formatting, does not affect the outcome.

A clean run is one with no critical and no major findings. Minor findings can be collected and fixed
in the same pass. Beyond that, the loop needs hard limits, because an autonomous loop with no limit
is just an expensive way to burn cloud credits:

- Stop as soon as a live run is clean.
- Cap the number of live runs per tutorial (I use four). When the cap is reached, report the status
  honestly and escalate.
- If the same critical finding survives two consecutive rounds, the tutorial is blocked, not "still
  in progress". Report the concrete condition instead of trying again.

One rule matters more than all the others: **an environment failure is not a documentation
finding**. A dead web terminal, a lost session, a transient capacity error or a failed consent
dialog is a problem with the machine you are running on. Repair it, retry once, and do not let it
consume the run budget. The mirror image is just as important: a guide that fails on a genuinely
fresh environment *is* a documentation defect, usually major or critical. Conflating the two
produces the worst possible outcome, a tutorial rewritten to match a broken environment.

## The browser is the hard part

Everything above works on a laptop with no cloud account, but the browser side has its own rules,
all of them learned the hard way:

- **Use a dedicated automation profile**, not your daily browsing profile. Headless by default so
  nothing pops up on your screen, with the debug endpoint checked before the run starts.
- **Share the profile across rounds** so the session persists, and so you cannot silently land in a
  different account halfway through.
- **Multi-factor authentication and consent screens are human gates.** The agent stops, you complete
  the login in a visible window, and then the agent resumes the *same* subagent, because the browser
  state lives in that session. The agent never types your credentials and never clicks a consent
  button.
- **Web terminals are the most fragile surface of the whole thing.** A cloud shell is usually an
  xterm.js canvas that ignores the generic "type this text" call of most automation tools. What
  works is per-character trusted key events, or a synthetic paste of one line at a time followed by
  a trusted Enter. Probe it with a single trivial command and confirm that it echoes before you
  start a walkthrough, and record the method that worked so you never have to rediscover it.
- **Check the account and the project before creating anything.** Local CLI credentials can point at
  a completely different, personal project. Do the CLI work inside the browser terminal of the
  tutorial project, and verify the active account and project there at the start of every round.

## What actually breaks

Across the tutorials I have verified with this loop, the failures cluster into a small number of
categories, and they are worth keeping in mind because they are the same everywhere:

1. **The access path.** The login instructions are the single most likely thing to be wrong. Portals
   change their identity providers and their consent screens. In one run the guide told the reader
   to continue with a Google account that the portal does not use; the working path was a completely
   different identity provider, and picking the wrong one produced an account-level denial that cost
   a full round to diagnose.
2. **Prerequisites that are conditional.** "Enable the Kubernetes API" fails on a project where the
   API is already enabled. Every conditional step needs an if-already-enabled path.
3. **Hardcoded names that collide.** Re-runs and the author's own testing leave buckets and service
   accounts with the exact names the guide uses, and the create command returns "you already own
   it". Every nameable resource needs a documented fallback, and the fallback name has to be used
   consistently by every later command that refers to it.
4. **Version drift.** Chart versions, machine images, driver versions, kernel names and library pins
   all move. A guide that resolves "latest" breaks on a fresh install while the author's cached
   environment keeps working.
5. **Sample output blocks.** The external IP, the node version, the pod status printed in the guide
   are all facts that were true once. They drift silently and they are the part readers trust most.
6. **Permissions one notch too weak.** A bucket role that grants object creation but not listing
   looks fine in the guide and fails at the first `ls` of the bucket.
7. **Scripts that ignore the documented input.** A helper that reads a different environment
   variable than the one the guide sets runs a placeholder query and returns a plausible, wrong
   answer.
8. **Teardown that is asynchronous or unsafe.** Deleting a cluster takes minutes, and a cleanup
   script that removes resources it did not create is worse than no cleanup script at all.

Version drift deserves one more note, because the wrong fix is so tempting: do not bump to the
newest release. Find the upstream commit that introduced the breaking behavior, take the newest
release strictly before it, and cross-check the constraints of the other packages in the set so the
pin resolves to a consistent environment. Then pin it explicitly in the guide, say why it is pinned,
and refresh the expected-output blocks byte-exact from the captured evidence rather than from
memory.

## Evidence, cleanup, and cost

An agent that says "the tutorial works" is worth very little. An agent that says "the tutorial
works" and attaches a screenshot of the created resource, the terminal output with the exit code,
the resolved versions, and the executed notebook is worth a lot, because the next round can use
those artifacts as the source of truth for the documentation.

Cleanup belongs in the same round as the walkthrough, with proof: delete what this run created, show
a listing where those resources are gone, and never touch a resource that existed before the run
started. The cleanup has to remain possible without the browser terminal too, because the terminal
is exactly the thing that tends to die halfway through. And never leave a billable resource behind
on the theory that someone will clean it up later.

## Start smaller: the same loop without a browser

Before you point any of this at a cloud console, run the miniature version on something that only
needs a terminal. Two subagents, a primary agent that loops them, at most two rounds, and no cloud
account, no login and no cleanup:

> Check that README.md works for a new user, using two subagents in a loop. Each round: call the
  readme-tester subagent with exactly the message "Test README.md." and nothing else, no hints. If
  it reports failures, give the readme-fixer subagent the tester's report word for word. Do at most
  2 rounds, and stop early if the tester reports ALL PASS. Do not edit files yourself. At the end,
  summarize each round: what failed and what changed.

The tester runs every command in a fresh temporary directory and cannot edit anything. The fixer
changes only the lines the report complains about and cannot run commands. The whole loop takes ten
to fifteen minutes end to end, and it teaches you the part that is hard to learn from theory:
whether your prompts are specific enough to be executed literally. When the tester reports a failure
that you did not expect, the tutorial is usually under-specified, and that is a finding worth having
before you discover it with a real user.

## What the system does not replace

The loop produces trustworthy evidence that the tutorial works. It does not decide whether the
tutorial is a good tutorial, and it does not have the right to publish anything. Pull requests,
merges, issue comments, anything that writes to the outside world still goes through explicit human
approval, and so do the logins that need a second factor. The right way to think about it is that
the automation removes the boring part of maintenance, so the human attention goes to the parts that
actually need a human.

If you want the long version of the process, with the report schema, the round protocol and the
checklist, it is all in the [CloudBank Showcase verification
playbook](https://github.com/cloudbank-project/cloudbank_showcase/blob/main/verification/README.md).
The agent definitions above are plain OpenCode subagent files, and the [agents
documentation](https://opencode.ai/v2/docs/agents) covers the rest of the format.
