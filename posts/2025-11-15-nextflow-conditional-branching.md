---
categories: [hpc, sdsc, nextflow]
date: '2025-11-15'
layout: post
title: Implementing Conditional Logic in Nextflow Workflows
---

This post serves as a follow-up to my previous tutorial, "[Running Nextflow on Expanse](2025-10-07-running-nextflow-on-expanse.html)", where I covered the foundational aspects of deploying Nextflow workflows on an HPC environment. While the previous discussion focused on execution environments, this tutorial delves into a crucial aspect of building sophisticated and adaptive computational workflows: conditional logic.

Conditional execution is a powerful feature in workflow management systems, enabling pipelines to dynamically adjust their behavior based on runtime conditions. Nextflow provides robust mechanisms for implementing conditional branching, leveraging its dataflow paradigm to ensure reproducibility and efficient parallel execution. This tutorial will explore how to implement such logic using channels and operators, drawing examples from the [`main_conditional.nf` pipeline](https://github.com/zonca/expanse_nextflow/blob/main/main_conditional.nf) available in the expanse_nextflow repository. The principles discussed here are universally applicable to Nextflow workflows, extending beyond the Expanse HPC environment.

## Problem Statement

Consider a scenario requiring the following workflow steps:

1.  **Parse Input:** Process a CSV file containing a list of greetings.
2.  **Generate Files:** Create a distinct file for each parsed greeting.
3.  **Global Conditional Decision:** Introduce a single, random decision that applies uniformly to the entire batch of greetings.
4.  **Conditional Transformation:** Apply an uppercase transformation exclusively to the files selected by the global decision.
5.  **Consolidate Output:** Merge all processed files into a single output.

The key challenge lies in the dynamic nature of the conditional decision, which necessitates dynamic channel operations within Nextflow.

## Core Processes

The `main_conditional.nf` pipeline utilizes several processes to achieve the described functionality:

| Process            | Responsibility                                                              | Inputs                  | Outputs                                   |
| :----------------- | :-------------------------------------------------------------------------- | :---------------------- | :---------------------------------------- |
| `sayHello`         | Generates an output file (`<greeting>-output.txt`) containing the greeting. | `val greeting`          | `path "${greeting}-output.txt"`           |
| `convertToUpper`   | Transforms the content of an input file to uppercase, creating `UPPER-<file>`. | `path input_file`       | `path "UPPER-${input_file}"`              |
| `collectGreetings` | Concatenates a collection of files and reports the total count of greetings. | `path input_files`, `val batch_name` | `path "COLLECTED-${batch}-output.txt"`, `val count_greetings"` |
| `random_decision`  | Executes `scripts/random_decision.sh` to produce either `0` or `1` as a standard output. | (None)                  | `stdout decision`                         |

The `random_decision` process is particularly noteworthy as it emits an integer directly onto a channel, rather than a file path, which is then used to drive the conditional logic.

## Workflow Orchestration

The DSL2 `workflow { main: ... }` block in `main_conditional.nf` orchestrates the dataflow as follows:

1.  **Initialize Greeting Channel:**
    ```groovy
    greeting_ch = Channel.fromPath(params.greeting)
                        .splitCsv()
                        .map { line -> line[0] }
    ```
    This sequence reads the CSV file, splits it into rows, and extracts the first column, resulting in a channel emitting individual greeting strings.

2.  **Execute `sayHello` Process:**
    ```groovy
    sayHello(greeting_ch)
    ```
    Invoking `sayHello` instantiates the process, making its output available via `sayHello.out`.

3.  **Determine Conditional Branch:**
    ```groovy
    random_decision()
    def decision_ch = random_decision.out
                            .map { it.trim() }
                            .view { "Random branch decision: $it" }
    ```
    The `random_decision` process is executed once. Its output, a single integer, is then trimmed and broadcast to `decision_ch`. Due to the broadcast nature of channels, all downstream consumers receive the same decision, ensuring a consistent conditional path for the entire batch.

4.  **Combine Greetings with Decision:**
    ```groovy
    sayHello.out
        .combine(decision_ch)
        .view { "Greeting + decision pair: $it" }
        .set { decorated_ch }
    ```
    The `combine` operator pairs each greeting file path from `sayHello.out` with the single decision value from `decision_ch`. The `.set { decorated_ch }` construct is crucial here, allowing this combined channel to be reused for subsequent branching operations without being consumed.

5.  **Implement Conditional Branching:**
    ```groovy
    decorated_ch
        .filter { tuple -> tuple[1] == "0" }
        .map { tuple -> tuple[0] }
        .view { "Skipping uppercase for: $it" }
        .set { skip_uppercase_ch }

    decorated_ch
        .filter { tuple -> tuple[1] == "1" }
        .map { tuple -> tuple[0] }
        .view { "Running uppercase on: $it" }
        .set { convert_input_ch }
    ```
    Here, `decorated_ch` is filtered into two distinct channels based on the decision value (`tuple[1]`). The `map` operator then extracts only the file path (`tuple[0]`), preparing the data for the next stage. The use of `.set` on both `skip_uppercase_ch` and `convert_input_ch` ensures these channels can be independently consumed.

6.  **Execute Conditional Transformation:**
    ```groovy
    def converted_ch = convertToUpper(convert_input_ch)
        .view { "Converted file produced: $it" }
    ```
    The `convertToUpper` process is only triggered for files that pass through the `convert_input_ch` (i.e., where the decision was `1`). Files in `skip_uppercase_ch` bypass this process entirely.

7.  **Merge Branches:**
    ```groovy
    def uppercase_ch = skip_uppercase_ch.mix(converted_ch)
    ```
    The `mix` operator interleaves elements from `skip_uppercase_ch` and `converted_ch`, emitting them as they become available. This effectively merges the two conditional branches back into a single stream for subsequent processing.

8.  **Final Collection and Reporting:**
    ```groovy
    collectGreetings(uppercase_ch.collect(), params.batch)
    collectGreetings.out.count.view { "There were $it greetings in this batch" }
    ```
    The `collect()` operator gathers all files from `uppercase_ch` before passing them to `collectGreetings`. This process then emits both the concatenated output file and a count of the processed greetings.

## Executing the Workflow

To execute this conditional workflow on Expanse, navigate to the `expanse_nextflow` repository and run:

```bash
nextflow run main_conditional.nf -profile slurm_debug -ansi-log false
```

You should observe output similar to this:

```
N E X T F L O W  ~  version 25.10.0
Launching `main_conditional.nf` [determined_kowalevski] DSL2 - revision: 9384b7fc20
[05/0ee611] Submitted process > sayHello (2)
[8c/80b9f0] Submitted process > sayHello (1)
[42/5b9235] Submitted process > random_decision
Random branch decision: 1
Greeting + decision pair: [/expanse/lustre/scratch/zonca/temp_project/nxf_work/05/0ee6113628b8c84ab1056f79fa5310/Bonjour-output.txt, 1]
Greeting + decision pair: [/expanse/lustre/scratch/zonca/temp_project/nxf_work/8c/80b9f0ef609a10ed6d25d115a2d73c/Hello-output.txt, 1]
Running uppercase on: /expanse/lustre/scratch/zonca/temp_project/nxf_work/05/0ee6113628b8c84ab1056f79fa5310/Bonjour-output.txt
Running uppercase on: /expanse/lustre/scratch/zonca/temp_project/nxf_work/8c/80b9f0ef609a10ed6d25d115a2d73c/Hello-output.txt
[40/30a93c] Submitted process > sayHello (3)
Greeting + decision pair: [/expanse/lustre/scratch/zonca/temp_project/nxf_work/40/30a93c83ed1f8c3d51791c8133f5c9/Holà-output.txt, 1]
Running uppercase on: /expanse/lustre/scratch/zonca/temp_project/nxf_work/40/30a93c83ed1f8c3d51791c8133f5c9/Holà-output.txt
[74/75e5ac] Submitted process > convertToUpper (2)
Converted file produced: /expanse/lustre/scratch/zonca/temp_project/nxf_work/74/75e5ac7244efcb02bb2973cbfffa2e/UPPER-Hello-output.txt
[dd/56e8de] Submitted process > convertToUpper (3)
Converted file produced: /expanse/lustre/scratch/zonca/temp_project/nxf_work/dd/56e8def9f6b74b805ceb2a5cc579d4/UPPER-Holà-output.txt
[23/32811d] Submitted process > convertToUpper (1)
Converted file produced: /expanse/lustre/scratch/zonca/temp_project/nxf_work/23/32811db56641dc0c36aa0e4cd66253/UPPER-Bonjour-output.txt
[f4/2c6a9d] Submitted process > collectGreetings
There were 3 greetings in this batch
```

These log entries confirm the dynamic execution of the conditional branches.

## Extending the Pattern

The conditional branching pattern demonstrated here can be extended in various ways:

*   Replace the `random_decision` process with one that queries external metadata, checks resource availability, or integrates with an API to inform branching logic.
*   Introduce additional `filter` operations to refine input streams based on specific criteria before transformations.
*   Utilize `view` blocks strategically during development for debugging complex dataflow paths.

## Conclusion

Implementing conditional logic in Nextflow workflows is fundamental for creating adaptable and efficient pipelines. By understanding how to manipulate channels with operators like `combine`, `filter`, `map`, `mix`, and `set`, developers can design workflows that respond dynamically to runtime conditions while maintaining Nextflow's benefits of reproducibility and parallel execution. This approach ensures that complex scientific workflows can be both robust and flexible, regardless of the underlying computing environment.

