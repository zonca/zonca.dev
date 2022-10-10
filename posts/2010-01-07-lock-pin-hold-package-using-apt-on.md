---
aliases:
- /2010/01/lock-pin-hold-package-using-apt-on
categories:
- linux
date: 2010-01-07 13:49
layout: post
slug: lock-pin-hold-package-using-apt-on
title: lock pin hold a package using apt on ubuntu

---

<p>
 set hold:
 <br/>
 <code>
  echo packagename hold | dpkg --set-selections
 </code>
 <br/>
 <br/>
 check, should be
 <strong>
  hi
 </strong>
 :
 <br/>
 <code>
  dpkg -l packagename
 </code>
 <br/>
 <br/>
 unset hold:
 <br/>
 <code>
  echo packagename install | dpkg --set-selections
 </code>
</p>
