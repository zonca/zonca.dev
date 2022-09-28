---
aliases:
- /2010/01/load-arrays-from-text-file-with-numpy
categories:
- python
date: 2010-01-05 16:32
layout: post
slug: load-arrays-from-text-file-with-numpy
title: load arrays from a text file with numpy

---

<p>
 space separated text file with 5 arrays in columns:
 <br/>
 <br/>
 [sourcecode language="python"]
 <br/>
 ods,rings,gains,offsets,rparams = np.loadtxt(filename,unpack=True)
 <br/>
 [/sourcecode]
 <br/>
 <br/>
 quite impressive...
</p>
