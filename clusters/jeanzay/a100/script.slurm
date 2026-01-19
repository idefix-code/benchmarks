#!/bin/bash
#SBATCH -A @account@@a100
#SBATCH -C a100
#SBATCH --job-name=idefixIdeal     # nom du job
#SBATCH --nodes=@nodes@                   # nombre de noeuds
#SBATCH --ntasks-per-node=@core@         # nombre de tache MPI par noeud  (=nb de GPU)
#SBATCH --gres=gpu:@core@                # nombre de GPU par noeud
#SBATCH --cpus-per-task=6          # nombre de coeurs CPU par tache (un quart du noeud ici)
# /!\ Attention, "multithread" fait reference à l'hyperthreading dans la terminologie Slurm
#SBATCH --hint=nomultithread        # hyperthreading desactive
#SBATCH --time=00:10:00             # temps maximum d'execution demande (HH:MM:SS)
#SBATCH --output=idefix%j.out     # nom du fichier de sortie
#SBATCH --error=idefix-error%j.out      # nom du fichier d'erreur (ici commun avec la sortie)

# nettoyage des modules charges en interactif et herites par defaut
module purge

# chargement des modules
module load arch/a100
module load cuda/12.1.0
module load gcc/12.2.0
module load openmpi/4.1.1-cuda
module load cmake/3.25.2


# echo des commandes lancees
set -x
#export KOKKOS_PROFILE_LIBRARY=~/src/kokkos-tools/kp_nvprof_connector.so
#which nsys
#nsys -v
# execution du code
#export TMPDIR=$JOBSCRATCH
#ln -s $JOBSCRATCH /tmp/nvidia


# execution du code
srun ./bind.sh ./idefix
