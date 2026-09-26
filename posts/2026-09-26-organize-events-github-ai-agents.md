---
title: "Organizing events with GitHub and AI agents"
date: 2026-09-26
categories: [events, github, ai, automation]
layout: post
---
Organizing conferences and workshops can quickly become overwhelming when plans, decisions,
contracts, and meeting notes are scattered across multiple platforms. To streamline this process, I
use a single public GitHub repository as the source of truth for all project details, combined with
the power of AI agents that assist me with the heavy lifting.

In the past I used Trello together with GitHub. In that setup Trello was mostly a to-do list used to
keep ongoing tasks alive by snoozing them until a later date. I think GitHub Projects can replace
exactly that role, while living next to the issues and the code in a single place.

## The repository as a single source of truth

Everything goes into the GitHub repository as Markdown: plans, meeting notes, decisions, people
involved, and agreements — one folder for each kind of information. It is all text-based and in one
place, so it gives complete visibility to every collaborator. More importantly, it creates a
structured knowledge base that an AI agent can digest at any time.

## Issues and the project board

Every activity is an issue, and the issue tracks its state over time: something you are doing now
versus something you will do later. This matters because organizing an event is a long process —
deadlines change, things get postponed, and without tracked state it is easy to lose sight of what
is actually going on.

The project board is the view that ties it all together. One column per state, and in a single
glance I can see what we are working on right now and what is waiting in the queue: `Working` shows
the tasks in progress, `ToDo` shows what to pick next, and `Snoozed` keeps postponed tasks visible
until their new due date arrives.

## Feedback through pull requests

Documents are reviewed through pull requests: changes are proposed, discussed, and recorded. This
works for drafts, proposals, and any document worth getting a second look at.

## The AI agent assistant

Each collaborator works with their own agent. A personal file
(`user_agent/AGENTS_<github-username>.md`) holds that collaborator's contacts and preferences —
for example, which email account the agent should use — and is read together with the shared
guidelines in `AGENTS.md`.

With the whole repository as context, the agent understands what is going on at any time. It can
automatically prepare drafts for emails to participants, sponsors, or speakers, summarize where
things stand, and suggest concrete next actions like creating a document or scheduling a meeting.

Nothing is fully autonomous. The agent proposes draft actions, and the human always makes the
final decision. Once an action is executed, it is recorded back into the issue, preserving the
complete history of the event organization.

## The check issues routine

At the start of a work session, I trigger the check issues routine by saying "check issues" — or
simply "Go". The agent reviews all my issues that are in the `ToDo` or `Working` state, reads the
related documents, and proposes the next concrete action for each one.

We go through the issues one at a time. For each one I see the proposed action and decide: say
`yes` to execute it, `skip` to move on, or give a date to postpone it. Only after I approve the
final draft does the agent actually do anything.

## Promotion and reminders

When the work behind an issue is finished, the outcome is promoted back into the repository — a
decision record, a meeting summary, an updated plan. And a daily automated check keeps deadlines
honest: issues come back from `Snoozed` to `ToDo` when their due date arrives, and if something is
a week overdue, the assignee gets a single notification.

The result is a workflow where all the state lives in one place, every change is recorded, and AI
agents do the legwork without ever taking decisions away from people.
