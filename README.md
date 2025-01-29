# benchmarks
Utility code used to orchestrate Idefix's performance tests.

## Contents

### OrszagTang3D

This directory contains scripts used to create the weak scaling plot (ig 8) from the Idefix method paper.
These tests were written for Idefix v1.1


### particles

This directory contains scripts used to evaluate the single-process perfomance (frag_tests) as well as weak scaling tests for the lagrangian particles module.
These tests were written for Idefix v2.0 with Clément Robert's particle module (unreleased at the time of writing).

### scripts/run-bench

A basic script to facilitate running the benchmark on a specific
version of Idefix.

To run a set of benchmarks, simply run the following command :

    scripts/run-bench --account <ACCOUNT> --gpu <GPU> --idefix-tag <IDEFIX_TAG> --max-cores <MAX-CORE> --problem-size <PROBLEM_SIZE>

(for example, to benchmark Idefix v2.2.00, on 1,2,4,8,16 and 32 GPU cores on NVidia A100, you can run) :

    scripts/run-bench --account <ACCOUNT> --gpu a100 --idefix-tag v2.2.00 --max-cores 32

This will fetch, compile and run the specified Idefix tag, then spawn
a few SLURM jobs, that you can monitor with `squeue --me`.

When all the jobs have been run (or even before then), you can run
`scripts/run-bench collect`, which will output a JSON file containing
all the relevant information about the runs, in the following schema :

    [
        {
          date: "YYYY-MM-DD_HH:mm:ss",      # the time at which the benchmark was started
          gpumodel: "model",                # the GPU model, as specified on the command-line
          idefix_commit: "COMMIT_ID",       # the Idefix commit ID that was tested
          bench_commit: "COMMIT_ID",        # the benchmark commit ID (in this repository)
          results: [
              {
                nbgpu: NGPU,                # the number of GPUs
                cell_updates: CELL_UPDATES, # in cells/second/GPU
              },
              ...
          ]
        },
        ...
    ]
