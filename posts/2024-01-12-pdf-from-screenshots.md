---
date: '2024-01-12'
layout: post
title: Make a PDF from a series of screenshots

---

You might need to digitize some web content by taking screenshots and then bundling them up in a PDF.

Here I am using Linux from the command line, leveraging `convert` from `Imagemagick` and `pdftk`.

Screenshots are usually in `png` format, we first want to compress them by turning them into PDF:

```bash
for f in *.png
do
    convert "$f" "$f".jpg
done
```

next we want to convert to PDF, but we need to set the right page size.
`1224x792` is the size of 2 sheets in `letter` format in portrait orientation side by side:

```bash
for f in *.jpg
do
    convert "$f" -density 72 -page 1224x792  "${f// /_}".pdf
done
```

Finally we can concatenate the pdf page to a single document:

```bash
pdftk *.pdf cat output document.pdf
```
