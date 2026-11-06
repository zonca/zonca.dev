---
title: "Set up an AI coding agent with free NRP models (November 2026)"
date: 2026-11-06
categories: [ai, llm, tools]
layout: post
description: "Set up OpenCode with the free NRP models in a few minutes, with safe permissions, model advice and the seminar checklist."
---

This is the setup companion to my seminar
"Best Practices for AI-Assisted Coding: GitHub, Testing, and Continuous Integration"
(November 6, 2026). It gets you from zero to a working coding agent in your terminal,
using the free Large Language Models hosted by the
[National Research Platform](https://nrp.ai) (NRP). It updates my
[January post](./2026-01-29-configure-nrp-llm-opencode-crush.md): the model catalog changed a lot since then.

If you already use an agent (Claude Code, Codex, Copilot CLI, Cursor), you only need the
[API key](#get-an-api-key) and the [model advice](#which-model): NRP documents
configurations for several clients in its
[client configurations page](https://nrp.ai/documentation/userdocs/ai/llm-managed/client-configs/).

## Get an API key

1. Log in at [nrp.ai](https://nrp.ai) with CILogon, choosing your institution
   (Google, GitHub or Microsoft work if your institution is not listed).
2. You need to be a member of a group with LLM access:
   * SDSC staff are added automatically to the `sdsc-llm` group, within about half an hour of the first login.
   * Students: ask your advisor to add you to their namespace.
   * Faculty, staff and postdocs can request their own namespace and add their group.
   * Check your memberships on the [namespaces page](https://nrp.ai/namespaces).
3. Create a key at [nrp.ai/llmtoken](https://nrp.ai/llmtoken).

Store the key in an environment variable, for example in `~/.bashrc`, never inside a
configuration file you might share or commit:

```bash
export NRP_API_KEY="your_key_here"
```

Do not send protected data to these models: the
[NRP Acceptable Use Policy](https://nrp.ai/NRP-AUP.pdf) excludes HIPAA, PII, CUI, FERPA and any data
covered by a data-use agreement. Prompt caches are shared between users unless you set a `cache_salt`
(see the [API access page](https://nrp.ai/documentation/userdocs/ai/llm-managed/api-access/)).

Check that it works by listing the models:

```bash
curl -s https://ellm.nrp-nautilus.io/v1/models -H "Authorization: Bearer $NRP_API_KEY"
```

## Install OpenCode

[OpenCode](https://opencode.ai) is an open source coding agent that runs in the terminal
and works with any OpenAI-compatible provider:

```bash
curl -fsSL https://opencode.ai/install | bash
```

## Configure OpenCode for NRP

Create `~/.config/opencode/opencode.json`. The key is read from the environment with
`{env:NRP_API_KEY}`, so the file contains no secret. This is the OpenCode 2 format (the install script gives you
OpenCode 2; for OpenCode 1 see my [January post](./2026-01-29-configure-nrp-llm-opencode-crush.md)):

```bash
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/opencode.json <<'JSON'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "nrp/deepseek-v4-flash",
  "providers": {
    "nrp": {
      "name": "NRP Nautilus",
      "package": "@ai-sdk/openai-compatible",
      "settings": {
        "baseURL": "https://ellm.nrp-nautilus.io/v1",
        "apiKey": "{env:NRP_API_KEY}",
        "headerTimeout": 120000,
        "chunkTimeout": 90000
      },
      "models": {
        "deepseek-v4-flash": { "name": "DeepSeek V4.1 Flash", "limit": { "context": 1048576, "output": 65536 },
          "capabilities": { "tools": true, "input": ["text", "image"], "output": ["text"] } },
        "glm-5": { "name": "GLM 5.3", "limit": { "context": 1048576, "output": 65536 },
          "capabilities": { "tools": true, "input": ["text"], "output": ["text"] } },
        "minimax": { "name": "MiniMax M3.1 Flash", "limit": { "context": 1048576, "output": 65536 },
          "capabilities": { "tools": true, "input": ["text", "image"], "output": ["text"] } },
        "qwen3": { "name": "Qwen 3.8 Flash Next", "limit": { "context": 1000000, "output": 65536 },
          "capabilities": { "tools": true, "input": ["text", "image"], "output": ["text"] } }
      }
    }
  }
}
JSON
```

`headerTimeout` and `chunkTimeout` (milliseconds) handle the rare NRP request that stalls and never answers: in my
rehearsals, two requests hung for over 20 minutes. With these settings OpenCode gives up after 2 minutes without
a response, or 90 seconds without new output, and retries up to three times (the defaults are 5 and 15 minutes).

Test it:

```bash
opencode run -m nrp/deepseek-v4-flash "Say hello in one sentence"
```

The very first run can take a little longer, because OpenCode downloads the provider package;
later runs answer in seconds.

Then start the interactive agent inside a project with `opencode`. Switch models with `/models` (in OpenCode 2
the interactive command has no `-m` flag: the default comes from `"model"` in the config), start a fresh
session for each new task with `/new`, and press Shift+Tab to switch between the `build` agent and the `plan` agent,
which reads and plans but cannot edit files: plan first, then build.

## Decide what the agent may do without asking

Out of the box OpenCode allows every action, including any shell command, and OpenCode 2 also allows
reading and editing files outside the project. I recommend asking before the actions that are hard to undo.
Add a `permission` block to `opencode.json`, either the global one or one in the project:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": {
      "*": "allow",
      "git push *": "ask",
      "gh pr merge *": "ask",
      "rm *": "ask"
    }
  }
}
```

The last matching rule wins, so the catch all comes first. When a rule says `ask`, OpenCode stops and offers
Allow once, Always allow, or Reject. This syntax works in OpenCode 1 and 2; OpenCode 2 also has a native
ordered `permissions` list, described in its
[permissions documentation](https://opencode.ai/v2/docs/permissions/).
Note that `opencode run` without `--auto` waits forever on an `ask` rule, so scripts need `--auto`
plus explicit `deny` rules for what must never happen.

## Which model?

My advice, based on daily use and checked against public benchmarks (November 2026):

| Model | API name | Parameters, total / active | Images | Context | Use it for |
|---|---|---|---|---|---|
| DeepSeek V4.1 Flash (1017) | `deepseek-v4-flash` | 552B / 8B to 16B | yes | 1M | everyday coding: fast and strong |
| GLM-5.3 (NVFP4) | `glm-5` | 753B / about 41B | no | 1M | harder problems that need more reasoning; slower, at most 2 parallel requests |
| MiniMax M3.1 Flash | `minimax` | 428B / 23B | yes, also video | 1M | alternative for complex code, uses few tokens; double check factual claims |
| Qwen3.8 Flash Next (FP8) | `qwen3` | 125B / 6B | yes, also video | 1M | fallback when the others are down, and a good "simple" model to test whether instructions are clear |

All are Mixture of Experts models: only the active parameters are used for each token, which is why
they are fast for their size. Parameter counts are from the Hugging Face model cards; the GLM-5.3 active
count is computed from its published configuration.

The catalog changes often, check the
[NRP models page](https://nrp.ai/documentation/userdocs/ai/llm-managed/models/) and the
[fair use policy](https://nrp.ai/documentation/userdocs/ai/llm-managed/fair-use/)
(48,000 output tokens per minute per key and model, double limits for SDSC and Internet2 affiliates).

## Optional: GitHub and Google Drive from the agent

The agent can use any command line tool you have installed. In the seminar I use:

* [GitHub CLI](https://cli.github.com) (`gh auth login`), to open pull requests and read CI logs
* [gog](https://github.com/steipete/gogcli), to read and download files from Google Drive

The GitHub CLI ships an official skill that teaches agents how to use it well (JSON output, pagination, picking the
right repository). Install it once for OpenCode, for all your projects (`gh skill` is a recent command, in preview: update `gh` if it is missing):

```bash
gh skill install cli/cli gh --agent opencode --scope user
```

It lands in `~/.config/opencode/skills/gh/`, and OpenCode loads it when a task involves `gh`. Use another `--agent`
value for other agents (for example `claude-code` or `codex`), and `gh skill update` to refresh it.

List the tools you want the agent to use in the `AGENTS.md` file of your project, and give each tool the narrowest
access that works. For example, gog can be limited to Drive and to one account, so the agent can neither read
your email nor switch accounts:

```bash
export GOG_ACCOUNT=you@example.edu GOG_ENABLE_COMMANDS=drive
```

## Optional: subagents that keep your README working

In the seminar, a primary agent runs two subagents in a loop: a tester that follows `README.md` literally
in a fresh directory and cannot edit files, and a fixer that changes only the lines the tester reported as
failing and runs the changed steps to check them. Each subagent starts with a fresh context, and its own model:
DeepSeek runs the loop, Qwen tests (if a small model can follow the README, a person can) and MiniMax fixes.
The tester, for example:

```markdown
---
description: Tests README.md by following it literally as a new user, from a fresh clone. Reports every step as PASS or FAIL. Never edits files.
mode: subagent
model: nrp/qwen3
permission:
  edit: deny
  bash: allow
---
You are a tutorial tester. ...
```

The three files (`readme-loop.md`, `readme-tester.md`, `readme-fixer.md`) are in `.opencode/agents/` of the
demo repository (from tag `checkpoint-5`): copy them into your project, press Shift+Tab to select `readme-loop`, and type `Check README.md.`
The same pattern, applied to browser tutorials, is described in
[Keeping interactive tutorials up to date with an orchestrator and AI subagents](./2026-11-03-keep-interactive-tutorials-up-to-date-with-subagents.md).

## Checklist

The seminar in eight lines, for any agent:

* Write an `AGENTS.md`: test command, available tools, what not to touch, "do not commit unless I ask".
* Add permission rules: ask before `git push`, merges and deletions.
* Name the file, the function and what **not** to change; start in plan mode, then let it write code.
* One task per session; commit before experiments, so `git reset --hard` makes a bad attempt free.
* Read every diff, the tests included: agents sometimes weaken a test to make it pass.
* Reproduce a bug with a failing test before fixing it.
* Run the tests in CI and protect `main`, so nothing merges while CI is red.
* Give separate roles separate agents, and enforce the roles with permissions, not with prompts.

## Next

The demo repository used in the seminar, with a tag for each step (`checkpoint-0` to `checkpoint-5`), is at
[github.com/zonca/weather-agent-demo](https://github.com/zonca/weather-agent-demo).
Check out any tag to start from that point of the seminar. The recording will be linked here.
