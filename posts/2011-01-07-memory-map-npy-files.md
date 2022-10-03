---
aliases:
- /2011/01/memory-map-npy-files.html
categories:
- python
date: 2011-01-07 21:04
layout: post
slug: memory-map-npy-files
title: memory map npy files

---

<p>
 Mem-map the stored array, and then access the second row directly from disk:
 <br/>
 <br/>
 <code>
  X = np.load('/tmp/123.npy', mmap_mode='r')
 </code>
</p>
