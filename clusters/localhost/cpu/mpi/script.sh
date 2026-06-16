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
mpirun -np @core@ ./idefix 2>&1 | tee idefix.out 
