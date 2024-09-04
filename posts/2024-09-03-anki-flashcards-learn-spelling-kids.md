---
categories:
- documentation
date: '2024-09-03'
layout: post
title: How to use Anki flashcards to help kids learn spelling
---

## Install Anki and initial setup

1. Go to the [Anki website](https://apps.ankiweb.net/) and download the Anki desktop app for Windows, Mac, or Linux.
2. Install the app on your computer.
3. Open the app, click "Add" to create a new profile with the name of the child who will be using the app.
4. Under "Tools", "Addons", "Get Addons", paste the code `111623432` to install the [HyperTTS addon](https://ankiweb.net/shared/info/111623432) for text-to-speech support.
5. Restart Anki to enable the addon.
6. Under "Tools", "HyperTTS Service Configuration", click "Enable" on "GoogleTranslate" (Free)
7. Back to the initial Anki page, click on "Create Deck" to create a new deck for your child's spelling words, call it "Spelling".
8. If you want to sync the progress across devices, for example have the kids use a phone or tablet to learn, go to [Ankiweb](https://ankiweb.net/account/signup) to create an online account, then click "Sync" in the Anki app to log in with the same credentials.

## Add spelling words to Anki

1. In the Anki Desktop app on your computer, from the main screen, click on the "Create Deck" button to create a new deck, name it "Spelling::Week1" or similar. This is going to create a subdeck, so that the kid can either study week by week or can study all the words at once.
2. Click on the deck you just created, then click on "Add" to add a new card.
3. In the "Front" field, just type a filling character, for example "a", then press "Tab" to move to the "Back" field. It will be overwritten.
4. In the "Back" field, type the spelling word, for example "apple".
5. Click "Add" to save the card (or press "Ctrl + Enter"). Add all the words.
6. Next click on "Browse" to see all the cards you just added. You can edit them if needed.
7. Select all the words (Edit -> Select All)
8. Click on the "HyperTTS" menu, click on "Add audio...(Collection)"
9. Configure "HyperTTS" (just on the first execution, then Anki will remember the settings):

    * Source field: Back
    * Target field: Front, sound tag only, remove other sound tags
    * Voice: GoogleTranslate English (US)

10. Click "Apply to notes" to add the audio to all the cards, this will take a few minutes.
11. If you need to sync across devices, click on "Sync" to upload the deck to the account Ankiweb.

## Study spelling words with Anki

Now the kid can study the spelling words using the Anki desktop app or the AnkiWeb website or the AnkiDroid Android or IOS app (the IOS app is paid, all other options are free).

1. Open the Anki app 
1. If they are not using the desktop app, click on "Sych" to download any new deck created under their account with the desktop app.
1. Select the deck you want to study.
2. Click on "Study Now" to start studying the cards.
3. The kid will see a blank page and hear the work spoken by the text-to-speech engine, they can then try to spell the word out loud.
4. Click on "Show Answer" to see the word spelled out
5. Click on "Again", "Good", or "Easy" to rate how well they remembered the word. They should use "Easy" sparingly, only for words they can spell without hesitation.

Anki will show the cards again based on the rating, so that the kid can review the words they have trouble with more often. With the standard settings, they should study their deck once a day.

If they want to study all cards again before a test, once they have completed they can click on "Custom Study" and select "Review ahead", specify 20 days, and click "Study now".