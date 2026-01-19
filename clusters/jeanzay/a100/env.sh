module purge

module load arch/a100

module load cuda/12.1.0
#module load nvidia-compilers/20.11
module load gcc/12.2.0
module load openmpi/4.1.1-cuda
module load cmake/3.25.2
module load python

export IDEFIX_FLAGS="-DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH_AMPERE80=ON -DIdefix_MPI=ON"
#module load paraview/5.9.1
