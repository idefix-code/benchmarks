#!/bin/bash

# explicitely bind HFI to each MPI process
# https://www.open-mpi.org/faq/?category=opa

if [ -z "${LOCAL_RANK}" ]; then LOCAL_RANK=${SLURM_LOCALID}; fi  # srun

export HFI_UNIT=$((${SLURM_LOCALID}/2))

"$@"
