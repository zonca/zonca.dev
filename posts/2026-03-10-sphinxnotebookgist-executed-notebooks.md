---
title: "Keep Jupyter notebooks clean in git, but rendered with outputs in Sphinx"
description: "A small Sphinx extension that fetches an executed notebook from a Gist or raw URL, verifies the sources still match, and replaces the local notebook during the docs build."
date: "2026-03-10"
categories: [python, jupyter]
---

When I build documentation with notebooks, I often want two things that pull in opposite directions:

* keep the notebook in git **without outputs**
* publish documentation that shows the **executed outputs**

[`sphinxnotebookgist`](https://github.com/zonca/sphinxnotebookgist) is a small Sphinx extension I wrote for that workflow.

## What the extension does

For any notebook that contains:

```json
{
  "metadata": {
    "sphinxnotebookgist": {
      "url": "https://gist.github.com/<user>/<gist_id>"
    }
  }
}
```

the extension:

1. resolves the URL to a raw notebook
2. fetches the executed notebook
3. compares only the notebook sources, ignoring outputs and execution counts
4. fails the build if the sources differ
5. replaces the local notebook in place if they match

That means the executed notebook becomes an artifact used only for the documentation build, while the repository can keep the cleaner source-only version.

## Why this is useful compared to `nbsphinx`

`nbsphinx` is excellent at rendering notebooks in Sphinx, but it solves a different problem.

With `nbsphinx`, the usual options are:

* commit notebooks with outputs already present
* execute notebooks during the docs build
* disable execution and render whatever is already in the file

All of those are reasonable, but they can be awkward when execution is slow, depends on credentials or external services, or when you want a canonical executed notebook produced elsewhere.

`sphinxnotebookgist` adds a different model:

* the repository notebook is the **editable source**
* the remote executed notebook is the **rendered artifact**
* the build checks that the source cells are still identical before using that artifact

So this is not a replacement for `nbsphinx`; it is a helper that can sit in front of `nbsphinx` or `myst-nb` when you want to separate authoring from execution.

## Practical benefits

This approach is useful when:

* executed outputs are large or noisy and you do not want them in git
* notebooks are executed in CI, on another machine, or in a trusted environment
* you want a hard failure when someone edits the source notebook locally but forgets to regenerate the executed copy
* you already publish executed notebooks through GitHub Gists or another raw URL

The extension currently supports GitHub Gist page URLs, direct raw `http(s)` notebook URLs, and local `file://` URLs for testing.

If this matches your workflow, the code is here: <https://github.com/zonca/sphinxnotebookgist> and the package is published on PyPI at <https://pypi.org/project/sphinxnotebookgist/>.
