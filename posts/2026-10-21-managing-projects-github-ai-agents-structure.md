---
title: "Managing projects with GitHub and AI agents: the structure problem"
date: 2026-10-21
categories: [events, github, ai, automation]
layout: post
---
In my previous post about [managing projects with GitHub and AI agents](/posts/2026-09-26-managing-projects-github-ai-agents.html) I described how I organize events and workshops with a single GitHub repository as the source of truth, issues for every activity, and an agent per collaborator. A reader asked me a question that made the remaining gap explicit: with one agent per collaborator, what part of keeping the shared repo, issues, and decisions in sync is still manual?

The short answer: the structure itself. The repo holds everything as Markdown, plans, meeting notes, decisions, people involved, agreements, one folder per kind of information, and the agents can digest any of it. But deciding where a new piece of information belongs, and getting collaborators to put it there, is still on me.

Early on I deliberately avoided a rigid layout, because I did not know what the project would need: a folder for meeting notes, one for decisions, maybe something else entirely. Flexibility was the right call, but it has a cost. Without an enforced structure, people do not see why a note should live in one file rather than another. Information ends up scattered across files and folders, and finding it again becomes manual work.

So in practice the division of labor is this: the agents keep issues and deadlines in sync, and I keep the structure in sync, or the absence of one.

What I would want from a tool: something that helps a team discover the right structure as the project evolves, and gently nudges people where to put things, without becoming rigid.
