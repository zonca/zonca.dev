---
aliases:
- /2010/06/change-column-name-in-fits-with-pyfits.html
categories:
- python
date: 2010-06-30 22:06
layout: post
slug: change-column-name-in-fits-with-pyfits
title: change column name in a fits with pyfits

---

<p>
 no way to change it manipulating the dtype of the data array.
 <br/>
 <code>
  a=pyfits.open('filename.fits')
  <br/>
  a[1].header.update('TTYPE1','newname')
 </code>
 <br/>
 you need to change the header, using the update method of the right TTYPE and then write again the fits file using a.writeto.
</p>
