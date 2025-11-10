---
categories:
- github
- ai
- python
date: '2025-11-10'
layout: post
title: Going Full Agentic for Scientific Software Development
---

The landscape of scientific software development is being transformed by AI coding agents. Over the past few weeks, I've been exploring GitHub Copilot's AI coding agent capabilities for maintaining [healpy](https://github.com/healpy/healpy), and the experience has been remarkable. What started as an experiment has evolved into a workflow that feels like managing a team of experienced developers rather than coding alone.

## The Workflow: Assigning Issues to AI Agents

My approach has been straightforward: I take existing issues from the healpy repository—some of which have been open for 5 years or more—and assign them to GitHub Copilot. The AI agent then automatically analyzes the issue, explores the codebase, and opens a pull request with a proposed fix.

Once Copilot completes its first pass at solving the problem, it requests my review. This is where the real collaboration begins.

## The Quality Spectrum: From Quick Wins to Iterative Refinement

The results have been remarkably varied. The simplest tasks were fixed perfectly on the first try, requiring no changes from me. These were often straightforward bug fixes or documentation updates where the solution was clear-cut.

However, most issues required a more collaborative approach. Typically, I would provide feedback two or three times before being satisfied with the result. The most common types of feedback I found myself giving were:

- **Requesting more comprehensive tests**: While Copilot would often add tests, I frequently asked for additional test cases to cover edge cases or ensure more thorough validation.
- **Requesting changelog entries**: Scientific software projects need proper documentation of changes. I regularly asked Copilot to add appropriate references to the changelog, explaining what was fixed and why it matters to users.
- **Refining implementation details**: Sometimes the approach was correct but needed adjustment to match the project's coding style or architectural patterns.

## Managing Multiple Pull Requests Simultaneously

One of the most impressive aspects of this workflow is the ability to work on multiple issues in parallel. At my peak, I was managing five different pull requests at the same time, with Copilot working on each one independently.

This parallel approach fundamentally changed my role. Instead of being the sole developer writing every line of code, I became a technical reviewer and project manager, guiding multiple AI agents toward the right solutions. It genuinely felt like having a team of five experienced developers working for me—each one capable, but needing direction and review to ensure quality meets project standards.

## Adding Another Layer: Automated Code Review with Codex

To enhance this workflow further, I enabled Codex, the AI-powered code review agent developed by OpenAI. This adds another dimension to the process:

1. Copilot creates and updates pull requests
2. Codex automatically reviews the changes and provides feedback
3. I can then ask Copilot to address Codex's feedback

This creates a fascinating dynamic where AI agents are reviewing each other's work. It's like having five developers and an additional maintainer on the team. Codex often catches issues I might miss in my initial review, such as potential security vulnerabilities, performance concerns, or edge cases that need better handling.

The immediate feedback loop is invaluable. Instead of waiting for human reviewers, the code gets an initial review instantly, allowing me to iterate faster and catch issues earlier in the development process.

## Streamlining with Auto-Merge

The final piece of this agentic workflow is enabling GitHub's auto-merge feature. Once the iterative review process is complete and all parties (human and AI) are satisfied with the changes, I enable auto-merge. This ensures that:

1. All required tests pass one final time
2. The pull request meets all branch protection requirements
3. The merge happens automatically without manual intervention

This eliminates the need to babysit pull requests waiting for final test runs. I can approve a PR, enable auto-merge, and move on to reviewing the next one, confident that it will merge once everything is green.

For more details on setting up and using auto-merge effectively, see my [previous post on auto-merging GitHub pull requests](2025-10-20-github-actions-auto-merge.md).

## The Mobile Advantage: Reviewing On the Go

An unexpected benefit of this workflow is how well it works from a mobile device. Since my primary role has shifted from writing code to providing feedback and guidance, I can effectively manage the process from my phone.

I no longer need to be in front of my laptop to keep development moving forward. I can:

- Review pull requests during coffee breaks
- Provide quick feedback to AI agents while commuting
- Approve changes and enable auto-merge from anywhere
- Check test results and Codex reports on the go

This flexibility means the AI agents can continue working even when I'm away from my desk. I give feedback, they iterate on the solution, and the development process continues smoothly. It's a remarkably efficient use of time that wouldn't be possible with traditional development workflows.

## What This Means for Scientific Software Development

This agentic approach to software development represents a significant shift in how we can maintain scientific software projects. The bottleneck is no longer the time it takes to write code—it's my capacity to review and guide the work effectively.

For scientific software projects that are often maintained by researchers with limited time, this is transformative. Issues that languished for years can now be addressed systematically. The AI agents provide the development capacity, while the human maintainer provides the scientific domain knowledge and quality standards.

The workflow isn't perfect—it requires active management, clear communication of requirements, and careful review. But it's remarkably effective, and it's only going to improve as these AI coding agents continue to evolve.

If you maintain scientific software, I highly recommend exploring this workflow. Start with a few straightforward issues, get comfortable with the review process, and gradually scale up. You might find, as I did, that it fundamentally changes how you approach software maintenance and development.

## Getting Started

If you're interested in trying this workflow yourself:

1. Explore [GitHub Copilot](https://github.com/features/copilot) and sign up for access (academic institutions often have free access)
2. Review my guide on [using GitHub Copilot for scientific computing](2025-05-23-github-copilot-scientific-computing.md)
3. Enable Codex on your repository for automated code review
4. Set up [auto-merge](2025-10-20-github-actions-auto-merge.md) to streamline your workflow
5. Start with simple issues to build confidence with the process

The future of scientific software development is looking increasingly collaborative—with AI agents as valuable team members working alongside human expertise.

---

*Yes, of course, this post was also created by Copilot from my speech-to-text raw inputs.*
