---
categories:
- openscience
date: 2024-11-13 00:00
layout: post
slug: self-invite-calendar-event
title: Allow users to self-invite to a Google Calendar event
---

Google Calendar is the most popular calendar service, and it is widely used in academia, often Scientific Collaborations maintain one or multiple shared calendars to keep track of events, deadlines, and meetings.

One of the missing features of Google Calendar is the ability to allow users to self-invite to an event, without the need for the event organizer to manually add them.

Currently if you want to share an event with users and allow them to be notified of any changes, you have to manually add them to the event, which can be cumbersome if you have a large number of users. The situation is better if you have all your users already in a Google Group, as you can add the group to the event, but this is not always the case.

The other option is to just share the entire calendar with the users, but this is not always desirable, as the users will be able to see all the events in the calendar, and not just the one they are interested in.

In this post, I will show you how to create a Google Form that allows users to subscribe to a Google Calendar event, without the need for the event organizer to manually add them.

We will use Google Apps Script to create a trigger that runs every time the form is submitted, and adds the user to the event.

First, we need the Calendar ID of the calendar we want to add the users to.

From the "Integrate calendar" section of the Calendar settings, copy the "Calendar ID",
which is in the format:

    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@group.calendar.google.com

Create a Google Form, in settings, activate "Collect email addresses" as "Responder input",
so that they can subscribe even if they do not have a Google Account associated with that email address.
It would be best, if possible, to set "Collect email addresses" to "Verified", so that users are required to verify their email address before submitting the form by logging in to Google.

Next go to "Responses", click on "Link to Sheets" and create a new spreadsheet.

Create a new Project in the Google Cloud Platform at the URL <https://console.cloud.google.com>  and enable the Calendar API under "APIs & Services" -> "Library".

Get the Project number from the "Project info" section and paste it in the "Project number" field in the Apps Script.
This will require to configure the OAuth consent screen, just set it to External and add yourself as a test user.

In the spreadsheet, go to "Extensions" -> "Apps Script" and paste the following code:

<https://github.com/zonca/google_calendar_autoinvite/blob/main/add_email_to_event.js>

Inspired by this [Gist](https://gist.github.com/medvedev/b67eedc5c0303c8eee6555aab5ee857c).

Next, we need the Event ID of the event we want to add the users to, 

1. Open event editor in Calendar Web UI
2. Paste in the Google Apps script the last part of the URL after "...eventedit/"

Go under Services and add the Calendar API.

Then go to "Triggers" and add a new trigger that runs the function we create every time the form is submitted.

You need to grant permissions, so go to the Apps Script and click on the "Run" or "Debug" button, and select the `test_addEmailToEvent` function then click on "Review Permissions" and grant the permissions.

Now you can test the form, and you should see the user added to the event in the calendar, they will also receive an email notification.
