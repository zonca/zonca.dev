---
title: "A practical primer on software citation"
date: '2026-09-28'
categories: [openscience, documentation]
layout: post
---

Software forms the foundation of modern research, yet citing code effectively remains a challenge
across scientific disciplines. Following the 2026
[Software Citation Workshop](https://softwarecitationworkshop.ucsd.edu/) hosted at UCSD and
supported by NASA, our team published a practical guide titled "A Practical Primer on Software
Citation in Research." It outlines a 7-step workflow for researchers and a 5-step framework for
developers, taking pragmatic positions on several grey areas in research software citation.

## 1. How far down the dependency tree should you cite?

A common dilemma is deciding which underlying libraries warrant formal citation. Top-level libraries
that directly shape your pipeline should always be formally cited. Foundational infrastructure
(NumPy, SciPy, Astropy) should be cited when a specific routine plays a dominant role in your
result. Deep dependencies generally do not require individual citations. Instead, scientific
reproducibility is preserved by recording complete versions in environment configuration files
(e.g., `requirements.txt`).

## 2. Adapting maintainers' preferred citations

While traditional advice suggests following a maintainer's instructions strictly, we advocate for a
more proactive approach: follow the intent, but adapt the format to meet citation standards. Authors
are encouraged to supplement requests by adding Zenodo DOIs, explicit version numbers, or commit
hashes to ensure the citation functions as a traceable reference.

## 3. Solving the GitHub-Zenodo metadata lag

Automatic archiving integrations like the GitHub-Zenodo webhook mint a version-specific DOI after a
release is published. As a result, the `CITATION.cff` file cannot contain its own version DOI,
leaving metadata one release behind. To resolve this, developers can use tools like Codefair to
generate and write the version-specific DOI directly into `CITATION.cff` prior to publishing.

## 4. Software authorship vs. paper authorship

Software citations should credit individuals based on contributions to the software itself, rather
than mirroring associated paper author lists. Because open-source software teams change over time,
authors should update `CITATION.cff` and Zenodo metadata with every new release to reflect current
contributors.

## 5. AI and Model Influence Statements

As AI-assisted workflows become common in code development and drafting, disclosure standards are
essential. We advocate for explicit disclosures or voluntary Model Influence Statements, detailing
how models were used, such as for grammar editing and figure concept brainstorming.

## Read the full primer

For the complete 7-step citation checklist, 5-step developer guide, and worked examples, read the
[full paper on arXiv](https://arxiv.org/abs/2609.28622).
