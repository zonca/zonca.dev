---
title: "Organizing events with GitHub and AI agents"
date: 2026-09-26
categories: [events, github, ai, automation]
layout: post
---
Organizing conferences and workshops can quickly become overwhelming when plans, decisions,
contracts, and meeting notes are scattered across multiple platforms. To streamline this process, I
use a single public GitHub repository as the source of truth for all project details, combined with
the power of AI agents to assist with the heavy lifting.

## GitHub as a single source of truth

Everything goes into the GitHub repository. Plans, decisions, people involved, contracts, and
meeting notes are all documented as issues or markdown files. Since it is all text-based and in one
place, it provides perfect visibility for collaborators. More importantly, it creates a structured
knowledge base that an AI agent can easily digest.

## Issues and the project board

Every activity is an issue, and the issue tracks its state over time: something you are doing now
versus something you will do later. This matters because organizing an event is a long process —
deadlines change, things get postponed, and without tracked state it is easy to lose sight of what
is actually going on.

The project board is the view that ties it all together. One column per state, and in a single
glance I can see what we are working on right now and what is waiting in the queue: `Working` shows
the tasks in progress, `ToDo` shows what to pick next, and `Snoozed` keeps postponed tasks visible
until their new due date arrives.

## The AI agent assistant

With the AI agent having access to all this information, it can understand the full context of the
event at any time. Instead of me writing everything from scratch, the agent can automatically
prepare drafts for emails to participants, sponsors, or speakers. It can also summarize where things
stand and suggest concrete next actions, like creating new documents or scheduling specific
meetings.

Nothing is fully autonomous. The agent acts as an assistant that proposes draft actions, and the
human always makes the final decision. Once actions are executed, everything is recorded back into
the repository and its issues, preserving the complete history of the event organization.

## The check issues routine

One of the most effective workflows is the check issues routine. At the start of a work session, I
ask the agent to review all my assigned issues that are in the ToDo or Working state. The agent
reads the related documents and proposes the next concrete action for each issue. This immediately
unblocks me and ensures continuous progress without having to spend time remembering where I left
off on various tasks.

I trigger this routine by saying "check issues" — or simply "Go".

We go through the issues one at a time. For each one I see the proposed action and decide: say
`yes` to execute it, `skip` to move on, or give a date to postpone it. Only after I approve the
final draft does the agent actually do anything.
