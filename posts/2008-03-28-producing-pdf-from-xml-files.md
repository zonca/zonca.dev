---
categories:
- linux
date: 2008-03-28 15:44
layout: post
slug: producing-pdf-from-xml-files
title: Producing PDF from XML files

---

[xmlto](http://cyberelk.net/tim/software/xmlto/) is a bash script for converting XML files to various formats, it uses xsltproc (from libxml2) and a tool for post-processing.
For PDF it uses either [PassiveTeX](http://www.tei-c.org.uk/Software/passivetex/) or [FOP](http://xmlgraphics.apache.org/fop/).
The main issue is that PassiveTeX is very old (2002/2003) so it's quite difficult to install on modern distros, FOP is better maintained (it's in Java) but it's very picky about the XML file, in my case I got some errors like `validation error`.

So I switched to another toolchain:

[docbook2X](http://docbook2x.sourceforge.net/) converts XML to Texinfo and then `texi2pdf` (from `texinfo`) produces the PDF.

To install on Ubuntu/Debian:

`sudo apt-get install docbook2x texinfo`

Then convert the XML file:

`docbook2x-texi mydoc.xml`

and produce the PDF:

`texi2pdf mydoc.texi`

It works perfectly and it's fast.
