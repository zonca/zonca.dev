---
aliases:
- /2020/03/pelican-to-fastpages
categories:
- python
date: '2020-03-09'
layout: post
slug: pelican-to-fastpages
title: Migrate from Pelican to Fastpages

---

I have been using the Pelican static website generator for a few years,
hosting the content on Github, automatically build on push via Travis-CI
and deploy on Github pages to `zonca.github.io`.

I am a heavy Jupyter Notebook user so once I saw the announcement of [Fastpages](https://fastpages.fast.ai/)
I decided it was time to switch.
I loved the idea of having Jupyter Notebooks built-in and not added via plugins,
also great idea to use Github actions.

Only issue I found was that you cannot setup Fastpages on `username.github.io`,
so went for using a custom domain name instead.

## Import content

I created a script, in Python of course, to modify the front matter of the markdown
posts from the Pelican formatting to Jekyll, see [`pelican_to_jekyll.py`](https://gist.github.com/zonca/b4a5a44513854e1c8918743d219f5f34).
It also renames the files, because Jekyll expects a date at the beginning of filenames.

## Setup paginate

Currently Fastpages doesn't support pagination for the homepage,
but [implemented a workaround](https://github.com/fastai/fastpages/issues/48#issuecomment-596608688).

**Update 12 March 2020**: Now `fastpages` supports pagination natively! see [the documentation](https://github.com/fastai/fastpages)


## Redirect from the old Github Pages blog

I modified the permalinks of Fastpages so that I have the same URLs in the old and new websites,
just the domain changes.
Github pages does not support custom rewriting rules, so I modified the Pelican template
to put a custom redirection tag in each HTML header.

In the Pelican template `article.html`, in the `<header>` section I added:

{% raw  %}

```
<meta http-equiv="refresh" content="0; URL=https://zonca.dev/{{ article.url }}">
<link rel="canonical" href="https://zonca.dev/{{ article.url }}">
```

{% endraw %}

So that Pelican regenerated all the articles with their original address
and automatically redirects upon access.
The canonical link hopefully helps with SEO.

Did the same with the `index.html` template to redirect the homepage,
this depends on your template:

```
<meta http-equiv="refresh" content="0; URL=https://zonca.dev">
<link rel="canonical" href="https://zonca.dev/">
```

## Screenshots of the old blog

Yeah, for posterity, growing older I get more nostalgic.

The homepage:

![Old blog homepage](old_blog_homepage.png)

A section of an article page:

![Old blog article page](old_blog_article_page.png)
