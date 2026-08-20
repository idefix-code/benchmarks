# benchmarks
Utility code used to orchestrate Idefix's performance tests.

## Contents

### OrszagTang3D

This directory contains scripts used to create the weak scaling plot (ig 8) from the Idefix method paper.
These tests were written for Idefix v1.1


### particles

This directory contains scripts used to evaluate the single-process perfomance (frag_tests) as well as weak scaling tests for the lagrangian particles module.
These tests were written for Idefix v2.0 with Clément Robert's particle module (unreleased at the time of writing).

### scripts/bench.py

A complete python script to :

1. Build Idefix for the cluster (Sub-command **build**).
2. Generate the job files for the given cluster (Sub-command **gen**).
3. Launching the jobs (Sub-command **run**).
4. Extracting the scalability results and plotting (Sub-command **extract**).

In order to proceed, you need to first **download** and **compile** *Idefix*. You can either do it by hand or use the **build** sub-command of the script :

    ./scripts/bench.py --cluster <CLUSTER> --commit <GIT-COMMIT> build

Then you need to **generate** the job directory and files :

    ./scripts/bench.py --cluster <CLUSTER> --commit <GIT-COMMIT> \
        --account <ACCOUNT> --max-cores <MAX-CORES> --cores-per-node <CORES-PER-NODE>\
        --problem-size <PROBLEM-SIZE> \
        gen

Note that when running on **GPUs**, the `core` options correspond to the number of GPUs and not cores.

Check that the jobs are created the right way, then launch them by calling :

    ./scripts/bench.py --cluster <CLUSTER> --commit <GIT-COMMIT> \
        --account <ACCOUNT> --max-cores <MAX-CORES> --cores-per-node <CORES-PER-NODE> \
        --problem-size <PROBLEM-SIZE> \
        run

You can then finally parse the logs to extract the perf and get some report files as output :

    ./scripts/bench.py --cluster <CLUSTER> --commit <GIT-COMMIT> \
        --account <ACCOUNT> --max-cores <MAX-CORES> --cores-per-node <CORES-PER-NODE> \
        --problem-size <PROBLEM-SIZE> \
        extract

It will produce :

 - `runs/<COMMIT>/<CLUSTER>/<DATE>/<PROBLEM-SIZE>/summary.json`
 - `runs/<COMMIT>/<CLUSTER>/<DATE>/<PROBLEM-SIZE>/summary.dat`
 - `runs/<COMMIT>/<CLUSTER>/<DATE>/<PROBLEM-SIZE>/summary.gnuplot`
 - `runs/<COMMIT>/<CLUSTER>/<DATE>/<PROBLEM-SIZE>/summary.pdf`

For a more concrete example, to use the **H100** of **Kraken**, you can use :

    # compile
    ./scripts/bench.py --cluster kraken-gpu/h100 --commit master build

    # generate the jobs
    ./scripts/bench.py --cluster kraken-gpu/h100 --commit master --account <ACCOUNT> \
        --max-cores 8 --cores-per-node 2 --problem-size 256 \
        gen

    # submit the jobs to the cluster
    ./scripts/bench.py --cluster kraken-gpu/h100 --commit master --account <ACCOUNT> \
        --max-cores 8 --cores-per-node 2 --problem-size 256 \
        run

    # extract the performance from the logs
    ./scripts/bench.py --cluster kraken-gpu/h100 --commit master --account <ACCOUNT> \
        --max-cores 8 --cores-per-node 2 --problem-size 256 \
        extract

In case you want to build Idefix yourself, use the case in **./OrszagTang3D/setup/** to prepare your build dir and then use the
`--build-directory` to configure in which directory your **idefix** binary and case files lands.

    ./scripts/bench.py --build-directory ./my_idefix/build/ --cluster kraken-gpu/h100 \
        --commit master --account <ACCOUNT> --max-cores 8 --cores-per-node 2 \
        --problem-size 256 \
        gen

To extract the data from a past date, you can precise the date (following the format `year-month-day`) and force the plotting with gnuplot via `--plot`:

    ./scripts/bench.py --cluster kraken-gpu/h100 --commit master --account <ACCOUNT> \
        --max-cores 8 --cores-per-node 2 --problem-size 256 \
        gen --date 2026-06-15 --plot

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
