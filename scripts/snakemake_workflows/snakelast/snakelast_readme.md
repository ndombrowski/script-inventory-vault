# Example workflow

Download fasta manually and store in the data folder:

1. https://www.ncbi.nlm.nih.gov/nuccore/MT271684.1?report=fasta (Clen)
2. https://www.ncbi.nlm.nih.gov/nuccore/MG753774.1?report=fasta (Clen)
3. https://www.ncbi.nlm.nih.gov/nuccore/NC_032042.1?report=fasta (Crac)
4. https://www.ncbi.nlm.nih.gov/nuccore/MK792749.1?report=fasta (Cser)

This workflow is designed to run the LAST on multiple genomes. It will generate a dotplot for each possible genome pair that is found in the data/mapping.tsv file.

For the below to work:

- Install [conda/mamba](https://scienceparkstudygroup.github.io/ibed-bioinformatics-page/source/conda/conda.html) and snakemake (`mamba install -c bioconda snakemake`)
- Ensure that you list all genomes of interest in the `config.yaml` file.


```{bash}
# Make a two column, tab separated file with the genome name and the taxon
# Add header: genome_name\ttaxon
# Manually replaced the content of second column with Clen, Crac or Cser
echo -e "sample_id\ttaxon\tpath" > data/mapping.tsv

for i in data/*fasta; do
  BASENAME=$(basename "${i%.fasta}")
  FULL_PATH=$(realpath "${i}")
  echo -e "${BASENAME}\t${BASENAME}\t${FULL_PATH}" >> data/mapping.tsv
done


# Code was tested with snakemake 7.32.3
# To setup dependencies defined in env.yaml, preferably use mamba since it is faster
# Note, this workflow can be run wherever, just make sure to set the correct path to the data and config files in the Snakefile and config.yaml files.
conda activate snakemake 

# Options 
# --report report.html (might need online connection)
# --dag: Do not execute anything and print the directed acyclic graph of jobs
# --summary, --detailed-summary
# -p: print out the executed shell commands
snakemake --snakefile workflow/Snakefile \
  --configfile config/config.yaml \
  --cores 1 --use-conda --conda-frontend mamba \
  --conda-prefix workflow/.snakemake/conda/
```