---
title: "Terminal-based AI Assistant with GitHub for Education"
date: "2026-01-20"
categories: [ai, github]
---

GitHub offers to all academic people a free GitHub Pro account which allows to use the Coding Assistant, which includes access to the latest and most powerful models from OpenAI, Anthropic, and Google.

The easiest way of using these tools is through the [GitHub Copilot extension for VS Code](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot). However, the most efficient method is to use a terminal-based coding assistant like Codex CLI or Gemini.

[OpenCode Assistant](https://opencode.ai) is an open source tool that allows you to leverage these models.

## Activate academic discount for GitHub

The first step is to activate the academic discount. For this, you need to first create a free account on GitHub.com and then click on the education link below:

[https://github.com/settings/education/benefits?locale=en-US](https://github.com/settings/education/benefits?locale=en-US)

You will need to have a `.edu` email address and also upload a copy of your badge.

## Install opencode in the terminal

First we need to install node and the easiest way is to use `nvm` (see [instructions](https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script)).

Currently the command is:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

Then run:

```bash
nvm install --lts
```

to install the last stable version of nodejs.

Then install `opencode-ai`:

```bash
npm i -g opencode-ai
```

Launch with `opencode` in your terminal.

## Authenticate opencode with Github Copilot

In OpenCode, run `/connect` and select **GitHub Copilot**.
Complete the GitHub device login flow.

## Start coding

You can use `/models` to choose a model. GitHub Copilot has free and premium models, you can check your usage under [https://github.com/settings/copilot/features](https://github.com/settings/copilot/features).

For simpler tasks, the best unlimited model is **Grok Code Fast 1**, alternatively if you need a larger context you can use **GPT 4.1**.

For more complicated tasks, the 2 best premium models are **GPT-5.2-codex** and **Gemini 3 pro**. You have 300 requests per month to these models.
