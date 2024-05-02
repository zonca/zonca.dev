---
date: '2024-04-25'
layout: post
title: Automate sending polls via WhatsApp

---

Polls in WhatsApp are so convenient for the users, but so painful for group admins.
Cannot modify them, cannot re-use or replicate them.

Best workaround I found is to use [`WPPConnect/WA-JS`](https://github.com/wppconnect-team/wa-js)

This creates a sort of API in the browser console that can be used to just copy-paste from an editor to create a poll.

* Install [Tampermonkey](https://www.tampermonkey.net/) in your browser (I tested with Chrome) 
* Select "Create new script"
* Paste from <https://github.com/wppconnect-team/wa-js?tab=readme-ov-file#tampermonkey-or-greasemonkey>, do not need to write anything where it says "Your code here"

Now after we login to [WhatsApp Web](https://web.whatsapp.com/) and select the target group chat,
we can open the "Developer tools", paste and execute:

```javascript
c = WPP.chat.getActiveChat()
WPP.chat.sendCreatePollMessage(
c.id,
'Title of the poll',
['9am', '9:30am', '10am', '2pm', '2:30pm', '3pm', 'No', 'Maybe']
);
```

This is very convenient especially if you send many polls that have mostly the same options.

You can also generate options dynamically in Javascript:

```javascript
c = WPP.chat.getActiveChat()
am = ['9am', '10am', '11am']
pm = ['2pm', '2:30pm', '3pm']
day = ['Sat', 'Sun']
other = ['No', 'Maybe']

options = []
for (i = 0; i < day.length; i++) {
    if (day[i] == 'Sun') {
        for (j = 0; j < am.length; j++) {
            options.push(day[i] + ' ' + am[j])
        }
    }
    for (j = 0; j < pm.length; j++) {
        options.push(day[i] + ' ' + pm[j])
    }
}
options = options.concat(other)

if (options.length > 12) {
    throw new Error('Number of options exceeds the limit of 12.');
} else {
    WPP.chat.sendCreatePollMessage(
        c.id,
        'Event title',
        options
    );
}
```
