---
title: "Send email using UCSD SMTP with a GMAIL-based address"
date: "2026-04-13"
categories:
- Python
---

If you have a GMAIL-based UCSD email address and need to send email programmatically or via an email client using SMTP, you can use Google's SMTP servers.

First, you need to generate an App Password:
Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) to get an app password.

Then, configure your application or email client with the following settings:

*   **Username:** `username@ucsd.edu`
*   **Password:** your newly generated app password
*   **SMTP Server:** `smtp.gmail.com`
*   **Port:** `465` (for SSL)
