---
layout: post
title: set python logging level
date: 2011-04-13 01:02
categories: [python]
slug: set-python-logging-level
---

<p>
 often using logging.basicConfig is useless because if the logging module is already configured upfront by one of the imported libraries this is ignored.
 <br/>
 <br/>
 The solution is to set the level directly in the root logger:
 <br/>
 <code>
  ﻿﻿logging.root.level = logging.DEBUG
 </code>
</p>
