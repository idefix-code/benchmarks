#!/bin/bash

# echo des commandes lancees
set -x
#export KOKKOS_PROFILE_LIBRARY=~/src/kokkos-tools/kp_nvprof_connector.so
#which nsys
#nsys -v
# execution du code
#export TMPDIR=$JOBSCRATCH
#ln -s $JOBSCRATCH /tmp/nvidia

# execution du code
OMP_NUM_THREADS=@core@ OMP_PROC_BIND=spread ./idefix 2>&1 | tee idefix.out 
