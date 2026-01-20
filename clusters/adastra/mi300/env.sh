module purge

module load cpe/24.07
module load craype-accel-amd-gfx942 craype-x86-trento
module load PrgEnv-cray
module load amd-mixed
module load cray-python/3.11.7
module load cmake

export IDEFIX_FLAGS="-DKokkos_ENABLE_HIP=ON -DKokkos_ENABLE_HIP_MULTIPLE_KERNEL_INSTANTIATIONS=ON -DKokkos_ARCH_AMD_GFX942=ON -DIdefix_MPI=ON"
