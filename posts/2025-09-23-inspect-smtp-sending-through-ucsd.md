---
title: "Inspect SMTP sending through UCSD"
author: "Andrea Zonca"
date: "2025-09-23"
categories: [Python]
---

When configuring email sending through UCSD, it can be surprisingly unclear which SMTP server to use. The official documentation mentions three options: `smtp.ucsd.edu`, `smtp.gmail.com`, and `smtp.office365.com`. This ambiguity often leads to trial-and-error, making it difficult to set up applications or scripts that reliably send emails. To cut through the confusion, I developed a simple script to systematically test connectivity and sending capabilities for all three servers.

This script, available on GitHub at [https://github.com/zonca/test_smtp_ucsd](https://github.com/zonca/test_smtp_ucsd), helps identify the most suitable SMTP server for your specific needs within the UCSD environment. It provides a clear way to determine which server offers the best reliability and performance, saving you the hassle of manual testing and configuration guesswork.
