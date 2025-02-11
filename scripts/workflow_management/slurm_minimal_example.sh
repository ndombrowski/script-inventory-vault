#!/bin/bash
#SBATCH --job-name=deeploc_ochromonas
#SBATCH --output=logs/deeploc_%j.out
#SBATCH --error=logs/deeploc_%j.err
#SBATCH --cpus-per-task=20
#SBATCH --mem=50G
#SBATCH --time=UNLIMITED

# Activate modules
source ~/.bashrc
mamba activate deeploc_2.0

#generate folder
mkdir -p 03_data/annotations/manual/deeploc

#run search
deeploc2 \
  -f 03_data/annotations/Ochro1393_1_4_GeneCatalog.faa \
  -o 03_data/annotations/manual/deeploc \
  -d cpu
