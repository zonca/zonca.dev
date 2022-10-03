---
aliases:
- /2012/07/compile-python-module-with-mpi-support.html
date: 2012-07-06 16:08
layout: post
slug: compile-python-module-with-mpi-support
title: compile python module with mpi support

---

<p>
 CC=mpicc LDSHARED="mpicc -shared" python setup.py build_ext -i
</p>
