---
title: "Tampermonkey Script for Audible Filtering"
author: "Zonca"
date: "2025-11-01"
categories: [javascript, web, automation]
---

This Tampermonkey script helps filter Audible search results by hiding items that do not meet certain criteria. Specifically, it hides audiobooks with a rating less than 4.0 stars or with fewer than 500 reviews.

The script injects JavaScript into the Audible.com website to dynamically modify the displayed content. It identifies book items on the page, parses their ratings and review counts, and then hides those that fall below the defined thresholds (`MIN_RATING = 4.0` and `MIN_REVIEWS = 500`).

Additionally, the script adds a small badge to the top right corner of the Audible page, indicating that the filter is active and showing the filtering criteria ("Audible filter: ≥4.0 & ≥500").

You can find the script here: [https://gist.github.com/zonca/e91085c6fcc74bc98f6acbe8074fe8b9](https://gist.github.com/zonca/e91085c6fcc74bc98f6acbe8074fe8b9)
