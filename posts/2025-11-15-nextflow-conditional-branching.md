---
categories: [hpc, sdsc]
date: '2025-11-15'
layout: post
title: Implementing Conditional Logic in Nextflow Workflows
---

This post serves as a follow-up to our previous tutorial, "[Running Nextflow on Expanse](2025-10-07-running-nextflow-on-expanse.html)", where we covered the foundational aspects of deploying Nextflow workflows on an HPC environment. While the previous discussion focused on execution environments, this tutorial delves into a crucial aspect of building sophisticated and adaptive bioinformatics workflows: conditional logic.

Conditional execution is a powerful feature in workflow management systems, enabling pipelines to dynamically adjust their behavior based on runtime conditions. Nextflow provides robust mechanisms for implementing conditional branching, leveraging its dataflow paradigm to ensure reproducibility and efficient parallel execution. This tutorial will explore how to implement such logic using channels and operators, drawing examples from the `main_conditional.nf` pipeline available in the [expanse_nextflow repository](https://github.com/zonca/expanse_nextflow). The principles discussed here are universally applicable to Nextflow workflows, extending beyond the Expanse HPC environment.

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

To execute this conditional workflow, navigate to the `expanse_nextflow` repository and run:

```bash
nextflow run main_conditional.nf
```

Observe the Nextflow logs for messages indicating the random decision and the subsequent branching behavior. For instance, you might see:

*   `Random branch decision: 1` (or `0`)
*   `Greeting + decision pair: [/path/to/Alice-output.txt, 1]`
*   `Skipping uppercase for: /path/to/Bob-output.txt` (if decision was `0` for Bob)
*   `Running uppercase on: /path/to/Alice-output.txt` (if decision was `1` for Alice)
*   `Converted file produced: UPPER-/path/to/Alice-output.txt`
*   `There were X greetings in this batch`

These log entries confirm the dynamic execution of the conditional branches.

## Extending the Pattern

The conditional branching pattern demonstrated here can be extended in various ways:

*   Replace the `random_decision` process with one that queries external metadata, checks resource availability, or integrates with an API to inform branching logic.
*   Introduce additional `filter` operations to refine input streams based on specific criteria before transformations.
*   Utilize `view` blocks strategically during development for debugging complex dataflow paths.

## Conclusion

Implementing conditional logic in Nextflow workflows is fundamental for creating adaptable and efficient pipelines. By understanding how to manipulate channels with operators like `combine`, `filter`, `map`, `mix`, and `set`, developers can design workflows that respond dynamically to runtime conditions while maintaining Nextflow's benefits of reproducibility and parallel execution. This approach ensures that complex scientific workflows can be both robust and flexible, regardless of the underlying computing environment.

### Next Steps

Explore other advanced Nextflow features, such as subworkflows, modules, and advanced error handling, to further enhance the sophistication and resilience of your computational pipelines.
