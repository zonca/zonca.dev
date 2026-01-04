---
title: "Voice chatbot with Gemini Live"
date: "2026-01-04"
categories: [ai]
---

If you go to [Google AI Studio](https://aistudio.google.com/) under playground, you can click **Live** and select the latest available model, at the moment: `models/gemini-2.5-flash-native-audio-preview-12-2025`.

Here you can choose configuration options on the right like the voice.
Once you have a configuration you like, you can copy the code with the **Get code** button on top.

Then we will be following the same procedure we did for the [text based chatbot](./2026-01-01-ai-chatbot-google-form-frontend.md).

Again the purpose of the AI assistant is to assist filling a google form: [PROMPT.md](https://github.com/san-diego-data-science/chatbot_voice/blob/main/PROMPT.md).

Here is the built application which is specialized to my own simple form with name, email, phone number and note, but if you run the same prompt with your own Google Form you can have it customized.

The entire app is at [https://github.com/san-diego-data-science/chatbot_voice](https://github.com/san-diego-data-science/chatbot_voice).

The app is deployed at [https://chatbot-voice.onrender.com/](https://chatbot-voice.onrender.com/). Note that this is on the free tier so it might take 30s to spin up.

You can follow instructions in the README to run it locally.

Enjoy!
