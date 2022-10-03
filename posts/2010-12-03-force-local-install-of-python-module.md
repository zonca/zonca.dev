---
aliases:
- /2010/12/force-local-install-of-python-module.html
categories:
- python
date: 2010-12-03 22:18
layout: post
slug: force-local-install-of-python-module
title: force local install of python module

---

<code>
 python setup.py install --prefix FOLDER
 <br/>
</code>
<br/>
<br/>
creates lib/python2.6/site-packages, to force a local install you should use:
<br/>
<br/>
<code>
 python setup.py install --install-lib FOLDER
</code>
