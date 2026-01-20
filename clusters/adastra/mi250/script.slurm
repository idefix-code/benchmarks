#!/bin/bash
#SBATCH -A @account@
#SBATCH --constraint=MI250
#SBATCH --job-name=idefixIdeal     # nom du job
#SBATCH --nodes=@nodes@                   # nombre de noeuds
#SBATCH --ntasks-per-node=@core@         # nombre de tache MPI par noeud  (=nb de GPU)
#SBATCH --gres=gpu:@core@                # nombre de GPU par noeud
#SBATCH --cpus-per-task=8          # nombre de coeurs CPU par tache (un quart du noeud ici)
# /!\ Attention, "multithread" fait reference à l'hyperthreading dans la terminologie Slurm
#SBATCH --hint=nomultithread        # hyperthreading desactive
#SBATCH --time=00:10:00             # temps maximum d'execution demande (HH:MM:SS)
#SBATCH --output=idefix%j.out     # nom du fichier de sortie
#SBATCH --error=idefix-error%j.out      # nom du fichier d'erreur (ici commun avec la sortie)

# nettoyage des modules charges en interactif et herites par defaut
module purge

# chargement des modules
module load cpe/24.07
module load craype-accel-amd-gfx90a craype-x86-trento
module load PrgEnv-cray
module load amd-mixed

export MPICH_GPU_SUPPORT_ENABLED=1

set -x

# execution du code

srun --ntasks-per-node=@core@ --cpus-per-task=8 --threads-per-core=1 --gpu-bind=closest -- ./idefix
