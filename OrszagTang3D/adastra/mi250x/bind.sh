#!/bin/bash

set -eu

################################################################################
# Machine configurations
#
# Outputs:
# AFFINITY_OMP_PLACES: List of cores that the process will be bound to. The cores are part of the AFFINITY_NUMA_NODE
# AFFINITY_NUMACTL   :
# AFFINITY_NUMA_NODE : Index on the NUMA domain
# AFFINITY_GPU       : =$LOCAL_RANK : Closest GPU to the AFFINITY_NUMA_NODE
################################################################################

function Adastra8Tasks8GPUs() {
    # Node local rank 0 gets the GCD 0, is bound the cores [48-55] of NUMA domain 3 and uses the NIC 3
    # Node local rank 1 gets the GCD 1, is bound the cores [56-63] of NUMA domain 3 and uses the NIC 3
    # Node local rank 2 gets the GCD 2, is bound the cores [16-23] of NUMA domain 1 and uses the NIC 1
    # Node local rank 3 gets the GCD 3, is bound the cores [24-31] of NUMA domain 1 and uses the NIC 1
    # Node local rank 4 gets the GCD 4, is bound the cores [ 0- 7] of NUMA domain 0 and uses the NIC 0
    # Node local rank 5 gets the GCD 5, is bound the cores [ 8-15] of NUMA domain 0 and uses the NIC 0
    # Node local rank 6 gets the GCD 6, is bound the cores [32-39] of NUMA domain 2 and uses the NIC 2
    # Node local rank 7 gets the GCD 7, is bound the cores [40-47] of NUMA domain 2 and uses the NIC 2
    AFFINITY_OMP_PLACES=('{48}:8' '{56}:8' '{16}:8' '{24}:8' '{0}:8' '{8}:8' '{32}:8' '{40}:8')
    AFFINITY_NUMACTL=('48-55' '56-63' '16-23' '24-31' '0-7' '8-15' '32-39' '40-47')
    AFFINITY_NUMA_NODE=('3' '3' '2' '2' '0' '0' '1' '1')
    AFFINITY_GPU=('0' '1' '2' '3' '4' '5' '6' '7')
}

################################################################################
# GPU binding
################################################################################

function AMDHIP() {
    export HIP_VISIBLE_DEVICES=${AFFINITY_GPU[$1]}
}

################################################################################
# CPU binding
#
# Outputs:
# START_COMMAND: To use like so: $START_COMMAND "$@"
################################################################################

function OpenMPAffinity() {
    export OMP_PLACES=${AFFINITY_OMP_PLACES[$1]}
    export OMP_PROC_BIND=TRUE
    START_COMMAND="exec"
}

function NUMACTLAffinity() {
    START_COMMAND="exec numactl --localalloc --physcpubind=${AFFINITY_NUMACTL[$1]} --"
}

function NUMACTLAffinityStrict() {
    START_COMMAND="exec numactl --physcpubind=${AFFINITY_NUMACTL[$1]} --membind=${AFFINITY_NUMA_NODE[$1]} --"
}

################################################################################

# LOCAL_RANK: Variable monotonously increasing by one. Starting at zero to the
#             number of process on the node this scrip is executing (included).
# If the user needs more than one rank per GPU, we could to a round robin GPU distribution with a wrap around
# LOCAL_RANK=$(($SLURM_LOCALID / 8))
LOCAL_RANK=$SLURM_LOCALID

# Define your machine configuration:
Adastra8Tasks8GPUs

# Define your GPU binding if any:
AMDHIP $LOCAL_RANK

# Define your CPU binding:
# OpenMPAffinity $$LOCAL_RANK
NUMACTLAffinity $LOCAL_RANK
# NUMACTLAffinityStrict $LOCAL_RANK

export MPICH_OFI_NIC_POLICY=USER
export MPICH_OFI_NIC_MAPPING="0:0,1; 1:2,3; 2:4,5; 3:6,7"

################################################################################

echo "Starting the process with: '$START_COMMAND'"

$START_COMMAND "$@"
