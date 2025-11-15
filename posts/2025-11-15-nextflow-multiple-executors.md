---
categories: [hpc, sdsc]
date: '2025-11-15'
layout: post
title: Mixing Nextflow Executors for Hybrid Workflows
---

This post demonstrates how to combine different Nextflow executors within a single workflow, a powerful pattern for optimizing resource usage in scientific computing. By running lightweight tasks locally and offloading computationally intensive processes to HPC clusters like Expanse (as discussed in my [previous tutorial on Nextflow on Expanse](2025-10-07-running-nextflow-on-expanse.html)), users can accelerate development and ensure scalability. This tutorial provides a minimal example of a Nextflow pipeline leveraging both local and Slurm executors.

## 1. Project Layout

```
expanse_nextflow/
├── greetings.csv
├── main_local_slurm.nf
├── nextflow.config
└── scripts/
```

`greetings.csv` is a CSV file whose first column holds greetings. `main_local_slurm.nf` defines three processes:

*   `sayHello` writes each greeting to its own file (local executor).
*   `convertToUpper` converts each file to uppercase (Slurm executor).
*   `collectGreetings` concatenates the uppercase files (local executor).

## 2. Key Nextflow Concepts

*   **Profiles** (in `nextflow.config`) are global bundles of settings activated via `-profile`. They affect the entire run.
*   **Executors** describe how a process gets executed (`local`, `slurm`, `awsbatch`, …). You can override the executor _per process_ with the `executor` directive inside the process block.
*   **Process directives** such as `queue`, `cpus`, `memory`, `clusterOptions`, and `beforeScript` can also be set per process.

This approach keeps everything inside the workflow file so individual processes specify exactly how they should run—no profile juggling required.

## 3. Walk Through `main_local_slurm.nf`

```nextflow
process sayHello {
    publishDir 'results', mode: 'copy'
    executor 'local'
    input:
        val greeting
    output:
        path "${greeting}-output.txt"
    script:
    """
    echo '$greeting' > '$greeting-output.txt'
    """
}
```
*Runs directly on the login node; no Slurm queue involved.*

```nextflow
process convertToUpper {
    publishDir 'results', mode: 'copy'
    container 'oras://ghcr.io/mkandes/ubuntu:22.04-amd64'
    executor 'slurm'
    queue 'debug'
    time '00:10:00'
    cpus 2
    memory '4 GB'
    clusterOptions '--account=sds166 --nodes=1 --ntasks=1 -o logs/%x-%j.out -e logs/%x-%j.err'
    scratch true
    beforeScript '''
      set -euo pipefail
      export SCRATCH_DIR="/scratch/$USER/job_${SLURM_JOB_ID}"
      mkdir -p "$SCRATCH_DIR/tmp"
      export TMPDIR="$SCRATCH_DIR/tmp"
      export NXF_OPTS="-Djava.io.tmpdir=$TMPDIR"
      echo "[NF] Using node-local scratch at: $SCRATCH_DIR"
    '''
    input:
        path input_file
    output:
        path "UPPER-${input_file}"
    script:
    """
    cat '$input_file' | tr '[a-z]' '[A-Z]' > 'UPPER-${input_file}'
    """
}
```
*Runs on Slurm with the same queue/limits/scratch prep the `slurm_debug` profile used, but scoped only to this process.*

```nextflow
process collectGreetings {
    publishDir 'results', mode: 'copy'
    executor 'local'
    input:
        path input_files
        val batch_name
    output:
        path "COLLECTED-${batch_name}-output.txt" , emit: outfile
        val count_greetings , emit: count
    script:
        count_greetings = input_files.size()
    """
    cat ${input_files} > 'COLLECTED-${batch_name}-output.txt'
    """
}
```
*Back to the local executor for the final aggregation and summary.*

## 4. Running the Workflow

1.  Place `greetings.csv` in the project root (first column only is fine).
2.  Launch the workflow without any profile overrides:
    ```bash
    nextflow run main_local_slurm.nf
    ```
3.  Observe the behavior:
    *   `sayHello` and `collectGreetings` appear in `.nextflow.log` as `executor > local` and execute immediately.
    *   `convertToUpper` submits to Slurm (`executor > slurm`) with the queue, resources, and `clusterOptions` defined in the process. You can check `logs/<process>-<jobid>.{out,err}` for scheduler output.

## 5. Tips for More Complex Pipelines

*   **Group processes by executor**: Keep the per-process directives close to the code that depends on them. Readers immediately understand where work runs.
*   **Extract shared directives**: If multiple processes share the same Slurm settings, wrap them in a `withName: { }` block inside `nextflow.config` _or_ create small helper functions in the script to set environment variables, keeping things DRY without new profiles.
*   **Respect login-node limits**: Only keep very quick, lightweight tasks on `executor 'local'`. Anything CPU-intensive should go to the scheduler.
*   **Container parity**: Use containers (Singularity/Apptainer or Docker) so local and Slurm executions rely on the same software stack.
*   **Logging**: Route `clusterOptions` output to a `logs/` folder for easier debugging, as done above.

## 6. Troubleshooting Checklist

*   **Processes stuck on Slurm** – verify queue/time limits match the partition. Increase `time` or `cpus` if the scheduler rejects jobs.
*   **Scratch errors locally** – ensure you only set `scratch true` when Slurm allocates node-local storage. Local processes should skip those directives.
*   **Environment differences** – leverage `beforeScript` to load modules or set `$PATH` consistently before each Slurm job starts.

With these practices you can confidently mix execution backends, keeping orchestration simple while still tapping into the scheduler for the heavy lifting.
