---
aliases:
- /2010/03/aptitude-search
categories:
- linux
- ubuntu
date: 2010-03-16 22:50
layout: post
slug: aptitude-search
title: aptitude search 'and'

---

<p>
 this is really something
 <strong>
  really annoying
 </strong>
 about aptitude, if you run:
 <br/>
 <code>
  aptitude search linux headers
 </code>
 <br/>
 it will make an 'or' search...to perform a 'and' search, which I need 99.9% of the time, you need quotation marks:
 <br/>
 <code>
  aptitude search 'linux headers'
 </code>
</p>
