---
categories:
- openscience
date: 2025-10-10 00:00
layout: post
title: "Manage calendar of a scientific collaboration using Google Groups"
---

Managing a calendar for a large scientific collaboration can be challenging. Over the years, I have tried different approaches to solve this problem.

### Previous attempts

*   **[Organize calendars for a large scientific collaboration](/posts/2019-12-02-organize_calendars_large_collaboration.md)**: I proposed to split events across multiple calendars, for example one for each working group. This is a good solution, but it can be difficult to manage multiple calendars.
*   **[Allow users to self-invite to a Google Calendar event](/posts/2024-11-13-self-invite-calendar-event.md)**: I showed how to create a Google Form that allows users to subscribe to a Google Calendar event. This is useful for public events, but not for internal meetings.

### The Google Groups approach

A better solution is to use Google Groups to manage the calendar of a scientific collaboration. The idea is to create a single calendar and give writing permissions to all coordinators of the different groups within the collaboration.

Then, you create a Google Group for the entire collaboration and a Google Group for each working group. You can also create hierarchical groups. The advantage of using Google Groups is that they are also useful as mailing lists.

When you create a repeating event for a meeting, you can invite the Google Group (or multiple groups) to the event. This way, each member of the group receives an invitation in their calendar. This is very useful because if there is any rescheduling, everyone gets a notification automatically.

### The new member problem

The only downside of this technique is that if someone joins the Google Group after the repeating event has been created, they do not get a notification for that event.

The workaround for this is to invite the group again. I think the best way to handle this is to write a script with the Google Calendar APIs that once a day or once a week goes through the events and finds the events where some Google Groups are invited and then removes and adds them back.

This can be implemented with a simple Python script using the `google-api-python-client` library that runs on a server or as a GitHub Action.

I will write about this in a future post.
