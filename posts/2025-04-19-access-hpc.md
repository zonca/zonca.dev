---
categories:
- hpc
date: 2025-04-19
layout: post
title: How to request High Performance Computing (HPC) resources
---

I am often asked how a scientist located in the US can access supercomputing resources.
I decided to write a blog post with an overview of the options, consider that I'm writing this in April 2025, so please cross-check on the official websites.

## Expanse

At the San Diego Supercomputer Center, our national scale resource is the [Expanse Supercomputer](https://www.sdsc.edu/systems/expanse/index.html), a powerful system designed for diverse scientific workloads.

**Expanse Specifications:**

*   **Peak Performance:** 5 Pflop/s
*   **CPU Cores:** 93,184
*   **GPUs:** 208 NVIDIA V100s
*   **Total DRAM:** 220 TB
*   **Total NVMe:** 810 TB
*   **Standard Compute Nodes (728 total):** AMD EPYC 7742 (Rome) CPUs (128 cores/node @ 2.25 GHz), 256 GB DRAM/node, 1 TB NVMe/node.
*   **GPU Nodes (52 total):** 4x NVIDIA V100s GPUs/node (32 GB memory/GPU, NVLINK), 40 Intel Xeon 6248 CPU cores/node (@ 2.5 GHz), 384 GB CPU DRAM/node, 1.6 TB NVMe/node.
*   **Large-memory Nodes (4 total):** AMD Rome CPUs (128 cores/node @ 2.25 GHz), 2 TB DRAM/node, 3.2 TB SSD/node.
*   **Interconnect:** HDR InfiniBand (100 Gb/s), Hybrid Fat-Tree topology.
*   **Storage:** Access to Lustre (12 PB) and Ceph (7 PB) parallel file systems.
*   **Architecture:** Organized into 13 Scalable Compute Units (SSCUs), each with 56 standard nodes and 4 GPU nodes.

Expanse is an ACCESS resource. ACCESS (Advanced Cyberinfrastructure Coordination Ecosystem: Services & Support) is a consortium of large US supercomputers dedicated to Science. It reviews applications from US scientists and grants them supercomputing resources. It is funded by the National Science Foundation.

### How to request resources on Expanse

Ordered from the lowest to the largest amount of resources needed, which generally corresponds to the amount of effort required for the allocation request. Resource usage on Expanse is typically measured in Service Units (SUs). Please refer to the [Expanse User Guide](https://www.sdsc.edu/systems/expanse/user_guide.html) for detailed billing information.

#### Trial Account

Anybody can request a trial account on Expanse with a quick justification. This is useful to try Expanse out and run some test jobs. See the ["Trial account" section in the Expanse User Guide](https://www.sdsc.edu/systems/expanse/user_guide.html#narrow-wysiwyg-2).

#### Campus Champions

Most US universities have a reference person that facilitates access to ACCESS supercomputers, often someone in the Information Technology office, Office of Research, or a professor. This person manages an allocation of supercomputing hours on ACCESS resources, and local faculty, postdocs, and graduate students can request access through them.
Campus champions are currently available in 362 US institutions, [see the list on the Campus Champions website](https://campuschampions.cyberinfrastructure.org/champions/current-campus-champions).

#### HPC@UC

If you are at any of the University of California campuses, you have an expedited way of getting resources at SDSC.
You can submit a request for a substantial allocation on Expanse via the [HPC@UC page](https://www.sdsc.edu/hpc-at-uc.html). It requires a justification and is typically reviewed within 10 business days. You might not be eligible if your research group has an active ACCESS allocation.

#### ACCESS Allocation

ACCESS allocations are full proposals where you can request significant resources on Expanse. You must provide a detailed justification for the resources requested and often demonstrate that your software can efficiently utilize the system. These requests are reviewed periodically. See the [ACCESS Allocations page](https://allocations.access-ci.org/get-your-first-project) for details on the process.

## Triton Shared Computing Cluster (TSCC)

The Triton Shared Computing Cluster is another supercomputer at SDSC, not allocated through ACCESS; resources are typically paid for by the users or their institutions. ACCESS resources can be oversubscribed, so groups needing additional resources might consider TSCC.

The easiest way to get hours on TSCC is often a pay-as-you-go option. A more cost-effective method for sustained use is often purchasing nodes to be added to the cluster (condo model). This grants an allocation proportional to the contributed hardware, allowing flexible usage patterns. Check the [TSCC page](http://www.sdsc.edu/services/hpc/tscc.html) or contact SDSC for current pricing and options.

## Feedback

If you have questions please email me at zonca on the `ucsd.edu` domain.