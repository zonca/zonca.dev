---
aliases:
- /2006/10/using-gnu-find
categories:
- linux
date: 2006-10-03 14:00
layout: post
slug: using-gnu-find
title: using gnu find

---

<p>
 list all the directories excluding ".":
 <br/>
</p>
<blockquote>
 find . -maxdepth 1 -type d -not -name ".*"
</blockquote>
<br/>
find some string in all files matching a pattern in the subfolders (with grep -r you cannot specify the type of file)
<br/>
<blockquote>
 find . -name '*.py' -exec grep -i pdb '{}' \;
</blockquote>
