---
title: "Python for HPC"

date: "2025-09-15"
categories: [Python, HPC, Numba, Dask]
---

Python has long been the language researchers reach for when prototyping ideas, but getting that same code ready for thousands of cores and petabytes of data takes a different playbook. On my blog I'm sharing the webinar I authored for the [Advanced HPC-CI Webinar series](https://www.sdsc.edu/education/training-programs/Advanced-HPC-CI-Webinars.html), which walks through that transition step by step and shows how to keep Python flexible while making it perform like a native HPC tool.

I'm Andrea Zonca, Lead of the Scientific Computing Applications Group at the San Diego Supercomputer Center, and in this session I guide you through the practices I rely on when bringing Python onto supercomputers. Learn more about my work here: [https://www.sdsc.edu/research/researcher_spotlight/zonca_andrea.html](https://www.sdsc.edu/research/researcher_spotlight/zonca_andrea.html).

Key topics include:

*   [Python Environment Management](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=240s) (4:00): Discusses using Jupyter Notebooks for development and two main techniques for handling Python environments on supercomputers: staging Conda environments as single packaged files for faster access on scratch space, and using Singularity/Docker containers for efficient execution.
*   [AI Code Assistants](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=557s) (9:17): Recommends using tools like GitHub Copilot and terminal-based assistants (e.g., Gemini) for code development, emphasizing an iterative process of AI coding and human review.
*   [Threads vs. Processes](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=1032s) (17:12): Explains the crucial difference between threads and processes in Python for distributed computing, highlighting Python's Global Interpreter Lock (GIL) and how it affects multi-threading performance. It suggests using multi-processing as a workaround for GIL limitations, while noting the memory overhead.
*   [Numba for Optimization](https://www.youtube.com/watch=Zv4DcRy1yeg&t=1974s) (32:54): Introduces Numba as a just-in-time (JIT) compiler to speed up Python functions, making them comparable to C/Fortran code. It shows how Numba optimizes computationally heavy parts of the code and can handle multi-threading automatically.
*   [Dask for Distributed Computing](https://www.youtube.com/watch?v=Zv4DcRy1yeg&t=3324s) (55:24): Explains Dask as a framework for running computations across multiple nodes, ideal for larger-scale problems and data that doesn't fit into memory. It details how Dask manages task dependencies and data transfer using a direct acyclic graph (DAG) and offers tools like Dask Array and Dask Delayed for parallel execution. The video also showcases Dask's real-time dashboard for monitoring distributed computations.

All materials for this video can be found here: [https://github.com/zonca/python_hpc_2025](https://github.com/zonca/python_hpc_2025)
