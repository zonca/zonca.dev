---
title: "Chatbot as a frontend for a Google Form"
author: "Andrea Zonca"
date: "2026-01-01"
categories: [ai]
---

Using a chatbot as a frontend for a Google Form can significantly improve user engagement and completion rates. Instead of a static form, users interact with a conversational interface that guides them through the questions, validates their input, and submits the data seamlessly. This approach is particularly useful for lead generation, surveys, and feedback collection, providing a modern and user-friendly experience.

### Step 1: Get Google AI Studio API Key

1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Create a free API key. It is always free for the free tier.
3.  Save it in a `.env` file in an empty folder:

```bash
GOOGLE_AI_STUDIO_API_KEY=your_api_key_here
```

### Step 2: Create the bot using Codex CLI

1.  Open your terminal.
2.  Navigate to the folder where you saved the `.env` file.
3.  Run the Codex CLI by typing `codex` in your terminal.
4.  Paste the following prompt to create the bot:

```markdown
Create a local **TypeScript (Node.js)** project: a **Gemini 3 Flash** chatbot that collects lead/contact info and **submits it to this Google Form**:

[https://docs.google.com/forms/d/e/1FAIpQLSeMLg8CT19TR38gzNso1kf5SnPOitt1-XTSC262addWlBnytQ/viewform?usp=dialog](https://docs.google.com/forms/d/e/1FAIpQLSeMLg8CT19TR38gzNso1kf5SnPOitt1-XTSC262addWlBnytQ/viewform?usp=dialog)

Constraints

* Read `GOOGLE_AI_STUDIO_API_KEY` from `.env`. Keep the key server-side (never expose to browser).
* Provide a minimal chat UI (`index.html`) served locally, calling a backend API (`/api/chat`, `/api/submit`).

Form handling (important)

* **Inspect/fetch the form HTML and automatically derive the required fields + their `entry.<id>` names** (do not hardcode field IDs).
* Build the mapping from the inspected form to the chatbot’s structured state, then POST to the form `formResponse` endpoint.

Bot behavior

* Ask for missing required fields one at a time, validate obvious formats (e.g., email), then show a final summary and require explicit user confirmation before submitting.

Testing

* Add unit tests (Vitest/Jest) for: form field extraction, validation, conversation state, and submission (HTTP mocked).
* Include a “test mode” flag that prevents real submissions and logs the payload.

Deliverables

* Working `npm` scripts: `dev`, `start`, `test`, and a short `README.md` to run locally.
```
