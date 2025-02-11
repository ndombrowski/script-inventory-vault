#!/bin/bash
#SBATCH --job-name=Rscript
#SBATCH --output=Rlog_%j.out
#SBATCH --error=Rlog_%j.err
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --time=1:00:00

#Activate env
source ~/.bashrc
conda activate quarto_1.4.4

#Run R
Rscript my_script.R
