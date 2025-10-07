---
title: "Python for HPC"

date: "2025-09-15"
categories: [Python, HPC, sdsc]
---

Python is often the first choice for prototyping research ideas, but scaling that prototype to thousands of cores and multi‑node workflows needs a different toolkit. This post shares a webinar I authored for the [Advanced HPC-CI Webinar series](https://www.sdsc.edu/education/training-programs/Advanced-HPC-CI-Webinars.html) that walks through a practical path: start with idiomatic Python, isolate hotspots, accelerate them, then scale out while keeping the development loop fast.

I'm Andrea Zonca, Lead of the Scientific Computing Applications Group at the San Diego Supercomputer Center. In the session I focus on pragmatic techniques that have repeatedly worked for moving Python workloads onto supercomputers. About me: [researcher profile](https://www.sdsc.edu/research/researcher_spotlight/zonca_andrea.html).

[Video on Youtube](https://www.youtube.com/watch?v=Zv4DcRy1yeg)

<iframe width="560" height="315" src="https://www.youtube.com/embed/Zv4DcRy1yeg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Key chapters:

* [Environment management](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=240s) (4:00) – Jupyter workflow; two deployment patterns: (1) pre-packaged Conda env tarballs staged to fast storage; (2) Singularity / Docker containers for portability and reproducibility.
* [AI code assistants](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=557s) (9:17) – Using tools like GitHub Copilot plus terminal assistants to speed iteration; keep a tight human review loop.
* [Threads vs processes](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=1032s) (17:12) – GIL implications; when threads are fine (I/O, native extensions) and when to switch to multiprocessing or compiled sections; memory trade‑offs.
* [Numba optimization](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=1974s) (32:54) – JIT hotspots, type specialization, parallel=True, cache usage, and when to stop micro‑optimizing.
* [Dask for scaling out](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=3324s) (55:24) – Task graphs, scheduler behavior, choosing between Array / Delayed / DataFrame, minimizing data movement, dashboard-driven tuning.

My group, the Scientific Computing Applications Group, helps scientists in the US optimize their code on supercomputers. Feel free to contact me via my [contact info](https://www.sdsc.edu/cgi-bin/staff_dir.cgi?query_type=s&name=Andrea+Zonca).

If you have any problems or feedback, please open an issue in the [repository](https://github.com/zonca/python_hpc_2025/issues/new).
