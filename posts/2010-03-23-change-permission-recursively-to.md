---
aliases:
- /2010/03/change-permission-recursively-to.html
categories:
- linux
date: 2010-03-23 17:58
layout: post
slug: change-permission-recursively-to
title: change permission recursively to folders only

---

<code>
 find . -type d -exec chmod 777 {} \;
</code>
