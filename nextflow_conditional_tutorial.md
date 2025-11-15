---
categories:
  - nextflow
---

# Implementing Conditional Branching in Nextflow

Conditional execution is one of the reasons workflow engines are more expressive than a pile of shell scripts. Nextflow gives you the same building blocks you already use in Python or Bash—`if`/`else`, random decisions, multi-step branching—but exposes them through channels and operators so that the dataflow graph stays reproducible and parallel. This tutorial walks through the `main_conditional.nf` pipeline in this repository and explains, line by line, how it works and why each operator was chosen.

## Problem Statement

We want to:

1. Parse a CSV of greetings.
2. Emit a file per greeting.
3. Make a single random decision that applies to the entire batch (all greetings share the same choice in this example).
4. Uppercase only the files that were selected.
5. Merge all produced files back together.

Because the random decision happens at runtime, we cannot determine the branch statically—we need dynamic channel operations.

## Processes

Three processes perform the core work (see `main_conditional.nf:1-72`):

| Process | Responsibility | Inputs | Outputs |
|---------|----------------|--------|---------|
| `sayHello` | Create `<greeting>-output.txt` with the greeting text. | `val greeting` | `path "${greeting}-output.txt"` |
| `convertToUpper` | Uppercase a file, writing `UPPER-<file>`. | `path input_file` | `path "UPPER-${input_file}"` |
| `collectGreetings` | Concatenate a batch of files and emit the number of greetings. | `path "COLLECTED-${batch}-output.txt"`, `val count_greetings` |

The `random_decision` process (lines 52-71) simply runs `scripts/random_decision.sh`, which prints `0` or `1`. Declaring `stdout decision` means the pipeline receives that integer on a channel instead of a file path.

## Workflow Breakdown

The DSL2 `workflow { main: ... }` block (lines 78-122) orchestrates the dataflow:

1. **Create the greeting channel**
   ```groovy
   greeting_ch = Channel.fromPath(params.greeting)
                       .splitCsv()
                       .map { line -> line[0] }
   ```
   `Channel.fromPath` emits the CSV file path, `splitCsv` streams each row, and `map` selects the first column. The channel now emits plain greeting strings.

2. **Launch the first process**
   ```groovy
   sayHello(greeting_ch)
   ```
   In DSL2, calling the process instantiates it and exposes two attributes:
   - `sayHello.out` for the stdout channel and any emitted files.
   - `sayHello.out.<name>` if you use the `emit:` keyword.

3. **Launch the conditional driver**
   ```groovy
    random_decision()
    def decision_ch = random_decision.out
                            .map { it.trim() }
                            .view { "Random branch decision: $it" }
   ```
   - `def` is regular Groovy syntax for defining a variable. The variable (`decision_ch`) simply holds a reference to the channel returned by `random_decision.out`. You are not copying any data; you are attaching a name to the stream so you can reuse it later.
   - We run the process once, but because channels are *broadcasts*, every downstream consumer gets the same decision value. Thus, the whole batch either skips or uppercases. If you wanted a per-greeting decision you would pass the greeting channel into a conditional process (e.g., `random_decision(greeting_ch)`), or derive the decision directly in Groovy with `.map`.

> **Channels vs. `def` variables**  
> A channel is a reactive stream provided by Nextflow (e.g., the result of `Channel.fromPath`, `sayHello.out`, or any operator chain). A `def` variable is just a Groovy reference that points to such a channel. When you write `def decorated_ch = ...` you are not materializing the stream; you are giving it a name so it can be consumed multiple times via `.set { decorated_ch }`. This keeps the syntax familiar for anyone with Groovy or Java experience while still operating entirely in Nextflow’s dataflow world.
   - `map { it.trim() }` removes stray newlines.
   - `view` is a debugging helper that prints every emitted element to the log.

4. **Combine greetings with decisions**
   ```groovy
   sayHello.out
       .combine(decision_ch)
       .view { "Greeting + decision pair: $it" }
       .set { decorated_ch }
   ```
   - `combine` pairs one greeting file path with one decision value.
   - `.set { decorated_ch }` stores the resulting channel into a named variable for reuse twice later. Without `.set`, the channel would be consumed once and disappear.

5. **Split into “skip” or “convert” branches**
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
   Each `filter` tests the decision value (`tuple[1]`). `map` strips the decision, leaving the file path. Because channels are immutable streams, you can reuse `decorated_ch` by placing `.set` earlier.

6. **Execute the conditional process**
   ```groovy
   def converted_ch = convertToUpper(convert_input_ch)
       .view { "Converted file produced: $it" }
   ```
   Only the `1` branch triggers `convertToUpper`. The skipped files never enter this process.

7. **Merge the branches**
   ```groovy
   def uppercase_ch = skip_uppercase_ch.mix(converted_ch)
   ```
   `mix` interleaves multiple channels and emits their values as soon as they are ready. It is preferable to `Channel.merge` in DSL2 because it works seamlessly with broadcast channels.

8. **Collect and report**
   ```groovy
   collectGreetings(uppercase_ch.collect(), params.batch)
   collectGreetings.out.count.view { "There were $it greetings in this batch" }
   ```
   - `collect()` is used only once at the point where we genuinely need all files before continuing.
   - The process emits both the concatenated file and the count, thanks to `emit: outfile` and `emit: count` in the process definition.

## Running the Workflow

```bash
nextflow run main_conditional.nf
```

Key log lines to watch (from `.nextflow.log`):

- `Random branch decision: 1` – emitted by the `view` on `decision_ch`.
- `Greeting + decision pair: [/path/to/Alice-output.txt, 1]` – confirms the `combine`.
- `Skipping uppercase for: /path/to/Bob-output.txt` – shows filtering works.
- `Converted file produced: UPPER-/path/to/Alice-output.txt` – indicates the conditional process ran.
- `There were 4 greetings in this batch` – final count from `collectGreetings.out.count`.

If you see errors such as `Missing process or function map(...)` or `No such property: out`, it usually means you attempted to call `map` on a plain list instead of a channel, or you tried to reuse a process handle instead of its `.out` channel. Ensuring every process is invoked (`sayHello(...)`, `random_decision()`) before using `.out` resolved those errors here.

## Extending the Pattern

- Replace `random_decision` with a process that inspects metadata, checks disk space, or queries an API to decide the branch.
- Chain additional filters before `set { convert_input_ch }` to guard against malformed inputs.
- Add `view` blocks early when troubleshooting—Nextflow removes them from execution semantics but keeps them invaluable for debugging.

## Summary

Conditional execution in Nextflow hinges on thinking in channels:

1. Generate the data you may need (`sayHello.out` and `random_decision.out`).
2. Combine, filter, and map streams to express logic.
3. Only collect or merge when necessary.
4. Use `.set` to reuse an intermediate channel, especially when creating multiple branches.

Following this pattern keeps your workflow fully parallel and deterministic while still reacting to runtime decisions.
