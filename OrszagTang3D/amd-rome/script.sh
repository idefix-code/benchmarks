#!/bin/bash
#MSUB -r @name@
#MSUB -n @nodes@  # this ais actually the number of MPI procs
#MSUB -c @core@   # number of threads
#MSUB -T 600
#MSUB -o bench_%I.o
#MSUB -e bench_%I.e
#MSUB -q rome
#MSUB -A gen2231
#MSUB -x # allocate the whole node, no matter what
##MSUB -@ geoffroy.lesur@univ-grenoble-alpes.fr:begin,end
# move to the working directory
set -x
cd ${BRIDGE_MSUB_PWD}        # The BRIDGE_MSUB_PWD environment variable contains the directory from which the script was submitted.

command="./idefix"

export OMP_NUM_THREADS=@core@
export OMP_PROC_BIND=spread
export OMP_PLACES=threads
# Execution
echo "executing $command"
ccc_mprun $command -nowrite
