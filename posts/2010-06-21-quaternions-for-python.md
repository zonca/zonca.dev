---
aliases:
- /2010/06/quaternions-for-python
categories:
- python
date: 2010-06-21 07:21
layout: post
slug: quaternions-for-python
title: quaternions for python

---

**Update**: SciPy now includes `scipy.spatial.transform.Rotation` which provides excellent quaternion support. See the [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html).

<p>
 the situation is pretty problematic, I hope someday
 <strong>
  scipy
 </strong>
 will add a python package for rotating and interpolating quaternions, up to now:
 <br/>
</p>
<ul>
 <br/>
 <li>
  <a href="http://cgkit.sourceforge.net/doc2/quat.html">
   http://cgkit.sourceforge.net/doc2/quat.html
  </a>
  : slow, bad interaction with numpy, I could not find a simple way to turn a list of N quaternions to a 4xN array without a loop
 </li>
 <br/>
 <li>
  Quaternion package from CXC Harvard (link no longer available)
  : more lightweight, does not implement quaternion interpolation
 </li>
 <br/>
</ul>
