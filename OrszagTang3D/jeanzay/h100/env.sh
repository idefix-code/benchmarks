#!/bin/bash

module purge

module load arch/h100
module load cmake/3.30.1
module load cuda/12.1.0
module load openmpi/4.1.5-cuda
module load python/3.11.5

export IDEFIX_FLAGS=-DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH_HOPPER90=ON -DIdefix_MPI=ON
