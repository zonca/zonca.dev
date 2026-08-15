---
title: "Running AlphaFold3 and OpenFold3 protein-ligand structure prediction on SDSC Expanse"
date: '2026-08-13'
categories: [hpc, ai, github, sdsc, singularity]
layout: post
---

I built two self-contained, reproducible projects that run realistic (non-toy) protein structure
prediction on a single SDSC Expanse GPU node: one with DeepMind AlphaFold3 (via
nf-core/proteinfold) and one with the fully open OpenFold3 (MCL1 protein-ligand ensemble).

## Purpose and Use Cases

These projects have several key purposes and use cases:

- Teaching and onboarding users to run modern AI structure-prediction on HPC resources.
- Giving a "scientifically meaningful but small" workload that fits one GPU node so it can be
  run/experimented on easily in cyberinfrastructure demos, tutorials, and allocation-chargeable PIs.
- Demonstrating the whole lifecycle: source config -> Slurm/Singularity/HPC-queue submission ->
  GPU inference -> download/cite/publish outputs (GitHub + Zenodo + Hugging Face) so results are
  reproducible and reusable.
- Enabling ensemble/uncertainty studies (multiple seeds and diffusion samples) to test whether a
  model's own confidence ranking correlates with structural/pose consistency.

For these examples, the AlphaFold3 example uses TetR homodimer + DNA, and the OpenFold3 example uses
the official MCL1 protein-ligand complex (PDB 5FDR context).

## Quick Highlight of the Two Cases

### 1. AlphaFold3 (nf-core/proteinfold)

This case uses a full Nextflow pipeline. I staged ~238 GB (compressed) / ~2 TB (unpacked) of AF3
databases once into persistent project storage, obtained the DeepMind-gated af3.bin weights, and
submitted the GPU inference job (RUN_ALPHAFOLD3) to gpu-shared.

Key engineering notes:

- Nextflow 26 strict parser workaround (`NXF_SYNTAX_PARSER=v1`)
- Expanse Slurm quirks (`--gpus=N` not `--gres=gpu:N`, `--nodes`/`--ntasks-per-node`,
  valid account/QoS)
- Pre-pull Singularity images via batch job so SIF conversion never happens on the login node.

Docs and README are available at:
[https://github.com/zonca/proteinfold-on-expanse](https://github.com/zonca/proteinfold-on-expanse)

### 2. OpenFold3

This is an open model (Apache-2.0, no gated weights). Using the official MCL1 protein-ligand
example, I ran a 20-prediction ensemble (4 seeds x 5 diffusion samples) on ONE V100 32GB in ~24
minutes with real MSAs from the ColabFold server. V100 (sm_70) requires native PyTorch kernels (skip
cuEquivariance/deepspeed extras). Then analyzed confidence-vs-ligand-pose consistency:
corr(sample_ranking_score, ligand RMSD) = -0.58 across the 20 predictions (higher confidence -> more
consistent ligand poses, moderate effect).

Docs and README are available at:
[https://github.com/zonca/openfold3-mcl1-expanse](https://github.com/zonca/openfold3-mcl1-expanse)

Data is published and can be found at the
[Hugging Face dataset](https://huggingface.co/datasets/zonca/openfold3-mcl1-expanse)
and [Zenodo DOI 10.5281/zenodo.21926059](https://doi.org/10.5281/zenodo.21926059), both referenced
from the GitHub README.

Analysis results and a reproducible script are in the repo (`analysis/RESULTS.md`,
`mcl1_ensemble_metrics.csv`, `analyze_ensemble.py`).

## Included Results and Key Numbers

- **OpenFold3 MCL1**: 20 structures, avg_plddt ~75-77 (with MSAs), ptm 0.29-0.35, iptm 0.12-0.19,
  wall time 24m13s on 1 V100.
- **Confidence-vs-consistency**: correlation = -0.58 (higher-confidence predictions place the ligand
  more consistently). Caveat: official example uses 4 identical MCL1 copies (chains A-D) that
  permute across samples -> large global protein RMSD; recommend single-chain query for cleaner 5FDR
  ligand-placement benchmarks.
