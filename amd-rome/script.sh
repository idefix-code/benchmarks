#!/bin/bash
#MSUB -r @name@
#MSUB -n @core@
#MSUB -T 600
#MSUB -o bench_%I.o
#MSUB -e bench_%I.e
#MSUB -q rome
#MSUB -A gen2231
#MSUB -@ geoffroy.lesur@univ-grenoble-alpes.fr:begin,end
​
# move to the working directory
set -x
cd ${BRIDGE_MSUB_PWD}        # The BRIDGE_MSUB_PWD environment variable contains the directory from which the script was submitted.
​
command="./idefix"
​

# Execution
echo "executing $command"
ccc_mprun $command
​
