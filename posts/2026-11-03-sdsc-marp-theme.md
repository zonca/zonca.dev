---
title: "A Marp theme that reproduces the official SDSC slide template"
date: 2026-11-03
categories: [sdsc, tools, documentation, github]
layout: post
description: "An open source Marp theme that reproduces the official SDSC slide template, extracted from the brand guide PowerPoint file, with a published HTML preview."
---

I recently built an open source Marp theme that reproduces the official San Diego Supercomputer Center (SDSC) slide template. This allows you to write your presentations in Markdown and have them look exactly like the official branded PowerPoint template, without actually having to use PowerPoint.

![Marp theme for SDSC - all slides preview](img/sdsc-marp-theme-preview.png)

## Why a Marp theme for the SDSC template?

The motivation for this project was simple: I prefer writing my slides in Markdown using [Marp](https://yhatt.github.io/marp/). However, for the SDSC tutorial and other SDSC talks, I needed the slides to strictly adhere to the official branded template. I wanted a way to achieve that professional, branded look directly from my Markdown source, ensuring the Markdown deck and the PowerPoint deck look identical.

The point of the exercise was to have a deck that is written in Markdown but is indistinguishable from the official branded template. I have published an [interactive HTML preview of the 11 slide demo deck](https://zonca.github.io/sdsc-marp-theme/) (you can navigate it with your arrow keys, and it is a single self-contained HTML file) so anyone can see the result before installing anything. There is also a [PDF of the same deck](https://zonca.github.io/sdsc-marp-theme/deck.pdf) available.

The theme lives in a public GitHub repository at [https://github.com/zonca/sdsc-marp-theme](https://github.com/zonca/sdsc-marp-theme). The code is MIT licensed, though all brand assets remain the property of SDSC and UC San Diego.

## Building the theme from the source of truth

![Title slide](img/sdsc-marp-theme-title.png)

Instead of approximating the brand values by eye, I extracted the real values directly from the official source of truth: the SDSC brand guide at [https://www.sdsc.edu/about/brand.html](https://www.sdsc.edu/about/brand.html), specifically the template file `SDSC-UCSanDiego-HSDSC.potx`.

*   **Colours**: Brand colours were extracted directly from `ppt/theme/theme1.xml` inside the `.potx` archive. This includes navy `#182B49` (PMS 2767), blue `#00629B`, gold `#C69214` (PMS 1245), bright gold `#FFCD00`, footer gray `#747678`, and light gray `#E7E6E6`.
*   **Typography**: The slide master uses Teko SemiBold for headlines and Source Sans 3 for body text. Both are brand approved and, conveniently, both are free on Google Fonts.
*   **Geometry**: The PowerPoint master is defined as 12192000 x 6858000 EMU. This maps perfectly to the standard Marp canvas of 1280 x 720 px (1 px = 9525 EMU). Every element is precisely positioned: side margins are 88 px, the title band starts 38 px from the top and is 154 px tall. Body text is 22 pt (29 px) and the title is 54 pt (72 px). The footer bar is 52.5 px tall with the SDSC wordmark at 46 px from the left and the UC San Diego / HSDSC logo at 46 px from the right.
*   **Assets**: The official logos (SVG, both colour and white variants), the dusk photograph of the SDSC building used on the title slide, and the other brand photographs were all extracted directly from the `.potx` package itself (`ppt/media/`). This means the theme ships with the real, official assets.

## Supported Layouts

The theme implements several slide layouts as CSS classes to match the PowerPoint options:

*   Default content slide
*   `title`
*   `reverse` (a navy background)
*   `section` (includes a navy divider)
*   `statement` (designed for one large, centred sentence)
*   `lead`
*   `columns` helper
*   Standard Marp background keywords are supported, such as `![bg right:45%](image.jpg)` for image right/left layouts.

The footer bar is implemented efficiently: it's drawn with a `section::before` pseudo element that carries the gray bar and both logos as background images. This ensures it always sits on top of full bleed background photos, matching exactly the "Image right + copy" layout found in the PowerPoint template.

To verify the accuracy, I rendered the official `.potx` with LibreOffice and compared it slide by slide with the Marp output to check the title band, margins, footer bar, and logo placement. You can find these official renders in the repository under `reference/official/` if you want to compare them yourself.

## How to use the theme

If you want to use this theme for your own presentations, here are the short installation instructions.

1.  Install the two brand fonts (both free from Google Fonts: [Teko](https://fonts.google.com/specimen/Teko) and [Source Sans 3](https://fonts.google.com/specimen/Source+Sans+3)).
2.  Copy the `themes/` and `assets/` folders from the [repository](https://github.com/zonca/sdsc-marp-theme) into your deck's folder.
3.  Add the following front matter to your Markdown deck:

```markdown
---
marp: true
theme: ../themes/sdsc.css
paginate: true
size: 16:9
---
```

4.  Render it using the Marp CLI:

```bash
npx @marp-team/marp-cli deck.md --theme ../themes/sdsc.css --allow-local-files --images png
npx @marp-team/marp-cli deck.md --theme ../themes/sdsc.css --allow-local-files --pdf
```

Note that the `--allow-local-files` flag is required because the theme references the local logo and photo files in the `assets/` folder. In Marp CLI 4 the PNG and the PDF outputs are separate options, hence the two commands.

**A note on reproducible environments (Linux)**: On Linux hosts where AppArmor blocks unprivileged user namespaces (such as Ubuntu 23.10 and newer), Chrome may abort with a `No usable sandbox!` error, and the Marp CLI cannot directly pass `--no-sandbox` to Puppeteer. To solve this, the repository ships with `scripts/chrome-wrapper.sh`, a tiny wrapper script that adds the necessary flag. You can pass this to Marp by setting the `CHROME_PATH` environment variable.

---

*Note: Please refer to the SDSC brand guide for the official rules and policies regarding the reuse of SDSC and UC San Diego logos.*
