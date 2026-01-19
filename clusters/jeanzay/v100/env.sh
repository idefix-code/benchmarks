module purge

module load cuda/12.1.0
#module load nvidia-compilers/20.11
module load gcc/12.2.0
module load openmpi/4.1.1-cuda
module load cmake/3.18.0
module load paraview/5.9.1
module load python

export IDEFIX_FLAGS="-DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH_VOLTA70=ON -DIdefix_MPI=ON"
