module purge

module load cuda/12.9.41.patched
module load openmpi/5.0.8/cuda-12.9-gcc-14.2.0
module load ucx/1.19.0-cuda

export IDEFIX_FLAGS="-DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH_HOPPER90=ON -DIdefix_MPI=ON"
