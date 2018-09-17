#!/bin/bash
#SBATCH --partition=GPU-shared
#SBATCH --job-name=itic_ptby
#SBATCH --output=res_%j.txt
#
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres gpu:1

module load singularity
cd /home/mhenry/planckton
singularity exec --nv --bind $(pwd) ~/docker-cmelab.simg python -u sim.py 
