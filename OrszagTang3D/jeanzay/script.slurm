#!/bin/bash
#SBATCH -A een@gpu
#SBATCH --job-name=idefixIdeal     # nom du job
#SBATCH --nodes=@nodes@                   # nombre de noeuds
#SBATCH --ntasks-per-node=@core@         # nombre de tache MPI par noeud  (=nb de GPU)
#SBATCH --gres=gpu:@core@                # nombre de GPU par noeud
#SBATCH --cpus-per-task=10          # nombre de coeurs CPU par tache (un quart du noeud ici)
# /!\ Attention, "multithread" fait reference à l'hyperthreading dans la terminologie Slurm
#SBATCH --hint=nomultithread        # hyperthreading desactive
#SBATCH --time=00:10:00             # temps maximum d'execution demande (HH:MM:SS)
#SBATCH --output=idefix%j.out     # nom du fichier de sortie
#SBATCH --error=idefix-error%j.out      # nom du fichier d'erreur (ici commun avec la sortie)

# nettoyage des modules charges en interactif et herites par defaut
module purge

# chargement des modules
module load cuda/11.2
module load gcc/8.3.1
module load openmpi/4.1.1-cuda
module load python/3.8.2
#module load nvidia-nsight-systems/2021.1.1

# echo des commandes lancees
set -x
#export KOKKOS_PROFILE_LIBRARY=~/src/kokkos-tools/kp_nvprof_connector.so
#which nsys
#nsys -v
# execution du code
#export TMPDIR=$JOBSCRATCH
#ln -s $JOBSCRATCH /tmp/nvidia


# execution du code
srun /gpfslocalsup/pub/idrtools/bind_hfi.sh ./idefix -autotune --kokkos-num-devices=@core@
