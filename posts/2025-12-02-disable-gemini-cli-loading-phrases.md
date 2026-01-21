---
title: "Disable Gemini CLI Loading Phrases"
description: "How to disable the annoying loading phrases in Gemini CLI for a smoother experience."
author: "Andrea Zonca"
date: "2025-12-02"
---

Tired of the loading phrases in Gemini CLI? You can easily disable them by adding a simple configuration to your `~/.gemini/settings.json` file. This is particularly useful for accessibility or if you simply prefer a less verbose output.

To disable the loading phrases, open or create the `~/.gemini/settings.json` file and add the following entry:

```json
{
  "ui.accessibility.disableLoadingPhrases": true
}
```

Here's a breakdown of the setting:

| Setting                                | Description                                       | Default Value |
| :------------------------------------- | :------------------------------------------------ | :------------ |
| `ui.accessibility.disableLoadingPhrases` | Disable loading phrases for accessibility.        | `false`       |

After saving the `settings.json` file, the Gemini CLI will no longer display the loading phrases, providing a more streamlined interaction.