---
title: "SDSC Cyberinfrastructure for AI-Enabled Science: A Beginner's Guide"
author: "Andrea Zonca"
date: "2026-05-29"
categories: [hpc, ai, sdsc]
description: "A beginner-friendly overview of SDSC's computing platforms for AI research — Expanse, Voyager, Cosmos, NRP, and the National Data Platform — with step-by-step access instructions and links to get started."
---

If you're a researcher looking to run AI workloads but don't know where to start, the San Diego Supercomputer Center (SDSC) at UC San Diego offers a remarkable set of cyberinfrastructure resources purpose-built for data-intensive, AI-enabled science. This guide walks you through each platform, what it's best for, and exactly how to get access — whether you need GPUs for deep learning, a Kubernetes cluster for flexible computing, or a data platform to discover and collaborate on datasets.

This post is based on a talk by [Mai H. Nguyen](https://www.sdsc.edu/research/experts/nguyen_mai.html) at the SMASH Lunch Seminar on May 26, 2026, with supplemental information and links for beginners.

## What Is Cyberinfrastructure?

Cyberinfrastructure (CI) is the integrated set of computing resources, data storage, networking, software tools, and human expertise that supports research and innovation. Think of it as the technological backbone that enables complex, data-intensive work — from training large language models to analyzing genomic data.

SDSC, part of UC San Diego's Halicioglu School of Data Science and Computing (HSDSC), develops and operates several CI platforms. Here are the five key resources covered in this guide:

| Platform | Best For | Accelerator Type | Access Method |
|----------|----------|-----------------|---------------|
| **Expanse** | General HPC, heterogeneous computing | NVIDIA V100/A100/H100 | ACCESS allocation |
| **Voyager** | Deep learning at scale | Intel Gaudi2 | ACCESS or NAIRR Pilot |
| **Cosmos** | GPU-accelerated science, easier GPU porting | AMD MI300A APU | Request via consult@sdsc.edu |
| **NRP (Nautilus)** | Flexible K8s computing, Jupyter notebooks | Various (A100, H100, V100, H200) | CILogon signup |
| **National Data Platform** | Data discovery, collaboration, AI-ready datasets | — | CI Logon signup |

---

## 1. Expanse — The Workhorse HPC Cluster

Expanse is SDSC's flagship HPC system for heterogeneous computing. It supports a wide range of science and engineering workloads, from molecular dynamics to AI/ML training, and is the most versatile entry point for researchers who need traditional HPC with GPU capabilities.

### Key Specs

- **CPU nodes:** 728 AMD EPYC 7742 (Rome) nodes, 128 cores each, 256 GB DRAM
- **GPU nodes:** 52 NVIDIA V100 GPU nodes (4 GPUs per node, NVLINK) — available via NAIRR
- **PATh expansion:** 112 AMD Milan CPU nodes + 8 A100 GPU nodes
- **Expanse AI Resource (new!):** 34 nodes with Intel Sapphire Rapids CPUs, 1 TB memory, **4 NVIDIA H100 GPUs per node**, 6.4 TB NVMe
- **Storage:** 12 PB Lustre + 7 PB Ceph
- **Interconnect:** HDR InfiniBand, 100 Gb/s

### Getting Started

1. **Get an ACCESS account:** Visit `https://identity.access-ci.org/new-user` and create an account using your institutional credentials.

2. **Request an allocation:** Go to `https://allocations.access-ci.org/` and choose a project type:
   - **Explore** (400K credits, 1-page proposal, approved in ~1 business day) — great for getting started, benchmarking, small classes
   - **Discover** (1.5M credits, 3-page proposal, any time) — for modest research needs
   - **Accelerate** (3M credits, 10-page proposal, any time) — mid-scale research
   - **Maximize** (largest, peer-reviewed, twice yearly) — large-scale campaigns

3. **Log in:** `ssh your_username@expanse.sdsc.edu` (requires 2FA with authenticator app)

4. **Try the Expanse User Portal:** `https://portal.expanse.sdsc.edu` — a web interface for file management, job submission, and launching Jupyter notebooks, RStudio, or MATLAB.

5. **Trial accounts:** If you just want to test things out, email `consult@sdsc.edu` for a trial account with 1,000 core-hours (approved within 1 business day).

### Software and Containers

Expanse uses a **Spack-based** software stack with environment modules (`module load ...`). Popular AI/ML packages (PyTorch, TensorFlow) are available. SDSC also provides **Singularity/Apptainer containers** for tools like AlphaFold2, PyTorch, TensorFlow, and more.

### Useful Links

- Expanse overview: `https://www.sdsc.edu/systems/expanse/index.html`
- Expanse user guide: `https://www.sdsc.edu/systems/expanse/user_guide.html`
- Expanse 101 tutorial: `https://hpc-training.sdsc.edu/expanse-101/`
- Expanse training repo: `https://github.com/sdsc-hpc-training-org/expanse-101`
- ACCESS allocations: `https://allocations.access-ci.org/`

---

## 2. Voyager — Purpose-Built for Deep Learning

Voyager is an NSF-funded HPC system specifically designed for AI applications. Its unique feature is the **Intel Gaudi2 accelerator** — a chip purpose-built for deep learning training and inference, different from traditional NVIDIA GPUs but with easy PyTorch migration.

### Key Specs

- **42 training nodes**, each with **8 Intel Gaudi2** accelerators (336 total)
- **36 Intel x86 compute nodes** for data processing
- **400 GbE RoCE interconnect** with all-to-all networking within nodes
- **Storage:** 3 PB Ceph + 324 TB home
- **Memory:** 512 GB per training node, 96 GB HBM2 per Gaudi2 accelerator

### Why Intel Gaudi?

If you've been using NVIDIA GPUs, migrating to Intel Gaudi is straightforward:

- **PyTorch is natively integrated** with the SynapseAI software stack — minimal code changes needed
- **Easy GPU migration:** Import `habana_frameworks` in your PyTorch code and you're largely set
- **HuggingFace support:** Use the [Optimum Habana](https://github.com/huggingface/optimum-habana) library to run Transformers and Diffusers models with minimal modification
- **Advanced users** can write custom kernels if needed
- **Jupyter notebooks** are also available on Voyager

### Getting Started

1. **Request access** via:
   - **NAIRR Pilot:** `https://nairrpilot.org/opportunities/allocations` — submit a 3-page proposal, reviewed monthly. Open to US-based researchers at academic institutions, nonprofits, and startups with federal grants.
   - **ACCESS:** `https://allocations.access-ci.org/` — Voyager is also available through ACCESS allocations.

2. **Log in:** `ssh login.voyager.sdsc.edu` (SSH key required — send your public key to `consult@sdsc.edu`)

3. **Run jobs:** Voyager uses **Kubernetes**, not Slurm. You submit workloads as Kubernetes pods using YAML files. Example:

   ```yaml
   apiVersion: v1
   kind: Pod
   spec:
     containers:
     - image: vault.habana.ai/gaudi-docker/1.10.0/ubuntu22:1.8.0-2
       command: ["hl-smi"]
       resources:
         limits:
           habana.ai/gaudi: 1
           hugepages-2Mi: 3800Mi
           memory: 32G
   ```

### Sample Applications

Researchers have already run diverse AI workloads on Voyager: diffusion models for cosmology super-resolution, BioBERT for biomedical text, U-Net for cardiac imaging, graph neural networks for high-energy physics, LLM fine-tuning for epilepsy, and more.

### Useful Links

- Voyager overview: `https://www.sdsc.edu/systems/voyager/index.html`
- Voyager user guide: `https://www.sdsc.edu/systems/voyager/user_guide.html`
- Reference models and tutorials: `https://github.com/javierhndev/Voyager-Reference-Models`
- Intel Gaudi documentation: `https://docs.habana.ai/`
- PyTorch on Intel Gaudi: `https://docs.habana.ai/en/latest/PyTorch/index.html`
- Optimum Habana (HuggingFace on Gaudi): `https://github.com/huggingface/optimum-habana`
- Voyager 101 webinar (Apr 2025): `https://github.com/sdsc-hpc-training-org/advanced-computing-webinars/tree/main/Apr-08-2025-Porting-PyTorch-to-Voyager`
- NAIRR Pilot allocations: `https://nairrpilot.org/opportunities/allocations`

---

## 3. Cosmos — Democratizing GPU Acceleration

Cosmos is SDSC's newest testbed system, built around the **AMD Instinct MI300A APU** — a chip that integrates both CPU and GPU on a single package with **unified memory**. This design eliminates the traditional hurdle of copying data between CPU and GPU memory, making GPU acceleration dramatically easier to adopt.

### Key Specs

- **42 nodes**, each with **4 AMD MI300A APUs** (168 APUs total)
- **Unified memory:** 128 GB HBM3 per APU, shared coherently between CPU and GPU (5.3 TB/s peak throughput)
- **24 EPYC Zen4 CPU cores** + 228 GPU compute cores per APU
- **HPE Slingshot interconnect** with AMD Infinity xGMI between sockets
- **VAST flash storage:** ~500 TB, high IOPS
- **Ceph capacity storage:** 4.9 PB
- **100% liquid cooled** HPE Cray EX system

### Why the APU Matters for Beginners

Traditional GPU programming requires managing two separate memory spaces (CPU host memory and GPU device memory) and explicitly copying data between them. The MI300A APU's **unified memory** means:

- **No host/device data copies** — CPU and GPU share the same memory
- **Incremental porting approach** — start with CPU code, gradually offload compute-intensive parts to GPU
- **"No code left behind"** — many applications that were never ported to GPUs can now be accelerated with minimal effort

### Getting Started

1. **Cosmos is currently in testbed phase.** Access is by project approval, not open allocation yet.
2. **Email `consult@sdsc.edu`** with a summary of your project. The Cosmos team evaluates suitability and sets up a follow-up call.
3. **Log in:** `ssh your_username@login01.cosmos.sdsc.edu` (SSH key required)
4. **Jobs use Slurm** — the familiar batch scheduling system: `sbatch`, `srun`, etc.

Cosmos uses **ROCm** (AMD's GPU computing platform) and provides containerized environments with AI/ML frameworks pre-installed.

### Useful Links

- Cosmos overview: `https://www.sdsc.edu/systems/cosmos/index.html`
- Cosmos user guide: `https://www.sdsc.edu/systems/cosmos/user_guide.html`
- AMD CDNA 3 architecture white paper: `https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf`
- NSF award announcement: `https://www.sdsc.edu/news/2024/PR20240712_Cosmos_award.html`

---

## 4. National Research Platform (NRP) — Federated, Flexible, and Free

The National Research Platform is a partnership of more than **80 institutions** across the US and globally, led by UC San Diego, University of Nebraska-Lincoln, and the Massachusetts Green High Performance Computing Center. Its primary computing resource is the **Nautilus cluster** — a massive Kubernetes-based distributed system spanning 4 continents.

### What Makes NRP Different

- **No allocation proposals needed** — sign up with your institutional credentials and start using it
- **Kubernetes-native** — flexible, container-based computing
- **Diverse hardware** — A100, H100, H200, V100 GPUs and more, contributed by partner institutions
- **Persistent storage** — CephFS, CvmFS, S3, or bring your own
- **Built-in services** — JupyterHub, GitLab with CI/CD runners, Nextcloud, Overleaf, and more

### Three Ways to Use NRP

1. **JupyterHub** — The easiest way. Log in through your browser, choose your hardware, and start running notebooks. No Kubernetes knowledge required. Visit the NRP JupyterHub and authenticate with your institutional credentials.

2. **Coder** — A JupyterHub-like experience with a full VS Code environment in the browser. Also requires no Kubernetes knowledge.

3. **kubectl** — For maximum control. Define pods, jobs, and deployments with YAML files, specifying CPU, GPU, memory, and storage requirements. Requires basic Kubernetes knowledge.

### LLM Inference Service

NRP provides **free, authenticated access to large language models** — a fantastic resource for researchers who need LLM capabilities without paying API costs:

- **Web chat interface:** `https://librechat.nrp-nautilus.io` or `https://nrp-llm-chat.nrp-nautilus.io`
- **API access** (OpenAI-compatible): Get a token at `https://nrp.ai/llmtoken/`, then use the OpenAI Python client:

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-nrp-token",
    base_url="https://ellm.nrp-nautilus.io/v1"
)

completion = client.chat.completions.create(
    model="gpt-oss",
    messages=[
        {"role": "user", "content": "Explain quantum computing in one paragraph."}
    ]
)
print(completion.choices[0].message.content)
```

### Coding Assistants on NRP

You can use the NRP LLM service to power local coding assistants like [OpenCode](https://github.com/opencode-ai/opencode) or Claude Code, giving you free, institutional-access AI coding help. See my step-by-step guides:

- [Configure NRP LLM with OpenCode and Crush](/posts/2026-01-29-configure-nrp-llm-opencode-crush)
- [Configure Claude Code with Minimax](/posts/2026-04-21-configure-claude-code-minimax)
- [Fixing clipboard issues with Opencode in Byobu/Tmux over SSH](/posts/2026-04-13-opencode-byobu-clipboard)

### Getting Started

1. **Sign up:** Go to `https://nrp.ai/get-access` and log in with your institutional credentials via CILogon
2. **Get added to a namespace** — contact your research supervisor or request to be promoted to admin to create your own namespace
3. **Install kubectl** and download your kubeconfig from the portal
4. **Or just use JupyterHub** for the simplest experience

### Useful Links

- NRP main site: `https://nrp.ai/`
- Getting started: `https://nrp.ai/documentation/userdocs/start/getting-started`
- Get access: `https://nrp.ai/get-access`
- Full documentation: `https://docs.nationalresearchplatform.org/`
- Using Nautilus (3 methods): `https://nrp.ai/documentation/userdocs/start/using-nautilus/`
- LLM managed service: `https://nrp.ai/documentation/userdocs/ai/llm-managed/`
- LLM API access: `https://nrp.ai/documentation/userdocs/ai/llm-managed/api-access/`
- Dashboard: `https://dash.nrp-nautilus.io/`

---

## 5. National Data Platform (NDP) — Data Discovery and Collaboration

The National Data Platform is a federated ecosystem for discovering, sharing, and computing on data. It's not a compute cluster — it's a platform that connects data, services, AI tools, and computing resources in one place.

### Key Features

- **Data Catalog** — Search across registered datasets from multiple institutions using substring search, conceptual search (powered by Open Knowledge Networks), spatial-temporal search, and filtered search by organization
- **Collaborative Workspace** — Web-based interface where multiple users can share resources, tools, and data in real time
- **AI-Ready Data** — Structured, curated datasets optimized for AI projects
- **Compute Integration** — Connect to HPC or cloud resources for data processing and ML training
- **Education Hub** — Hands-on modules and classroom resources for courses that need computational tools and AI-ready data

### The NDP Workflow

1. **Discover** — Find data and digital assets in the catalog
2. **Collect** — Add additional assets and workflow inputs
3. **Collaborate** — Create a shared workspace with collaborators
4. **Compute** — Execute workflows on HPC or cloud
5. **Store/Export** — Save final data products
6. **Extend** — Add endpoint services as needed

### Getting Started

1. **Go to** `https://nationaldataplatform.org/`
2. **Click "Log in/Register"** → Select "Sign in with CI Logon" → Choose "University of California, San Diego" as your Identity Provider → Log in with your UCSD Active Directory credentials
3. **Browse the catalog** or set up a workspace

### Useful Links

- NDP main site: `https://nationaldataplatform.org/`
- NDP documentation: `https://nationaldataplatform.org/documentation/`
- Data catalog: `https://nationaldataplatform.org/documentation/ndp-catalog/`
- Set up workspace tutorial: `https://nationaldataplatform.org/documentation/quick-start/set-up-workspace/`

---

## Which Platform Should You Choose?

Here's a simple decision guide:

- **Need traditional HPC with GPU support?** → Start with **Expanse** (ACCESS Explore allocation, approved in ~1 day)
- **Training large deep learning models?** → **Voyager** (Intel Gaudi2, purpose-built for AI)
- **Have CPU-only code you want to accelerate with GPUs?** → **Cosmos** (unified memory APUs make porting easy)
- **Want free, flexible computing without writing proposals?** → **NRP Nautilus** (sign up and go)
- **Need to find and collaborate on datasets?** → **National Data Platform**
- **Just want to try things out?** → **NRP JupyterHub** (fastest path from zero to running code) or **Expanse trial account** (email `consult@sdsc.edu`)

---

## SDSC Training Resources

SDSC offers extensive training programs to help you get up to speed:

- **SDSC HPC/CI Training:** `https://hpc-training.sdsc.edu/` — tutorials for Expanse, Voyager, and more
- **HPC Basic Skills:** `https://hpc-training.sdsc.edu/basic_skills/` — Linux, bash, batch computing fundamentals
- **COMPLECS:** Non-programming skills for using supercomputers (parallel computing concepts, security, data management)
- **CIML Summer Institute:** Best practices for machine learning on HPC systems
- **HPC & Data Science Summer Institute:** Week-long introductory workshop
- **Advanced HPC/CI Webinars:** `https://www.sdsc.edu/education/training-programs/index.html` — ongoing webinar series on AI/ML, performance analysis, and visualization
- **Expanse 101 Tutorial:** `https://hpc-training.sdsc.edu/expanse-101/`

## Getting Help

For any SDSC resource, email **`consult@sdsc.edu`** — the HPC consulting team can help you choose the right platform, get access, and optimize your workflows.

---

*This post is based on the SMASH Lunch Talk "Cyberinfrastructure for AI-Enabled Research at SDSC" by Mai H. Nguyen (SDSC), presented May 26, 2026. The original slides are available on the [Trello card for this project](https://trello.com/c/CA7e2WdI/271). Thanks to Mai for permission to create this blog post.*
