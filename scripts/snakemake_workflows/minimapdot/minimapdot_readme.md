---
format: html
---

# Generating dotplots

## Get data

Download fasta manually and store in the data folder:

1. https://www.ncbi.nlm.nih.gov/nuccore/MT271684.1?report=fasta (Clen)
2. https://www.ncbi.nlm.nih.gov/nuccore/MG753774.1?report=fasta (Clen)
3. https://www.ncbi.nlm.nih.gov/nuccore/NC_032042.1?report=fasta (Crac)
4. https://www.ncbi.nlm.nih.gov/nuccore/MK792749.1?report=fasta (Cser)

```{bash}
# Simplify header by finding lines starting with > and removing everything after the first space
for i in data/*fasta; do
  sed -i 's/ .*//' $i
done

# Make a two column, tab separated file with the genome name and the taxon
# Add header: genome_name\ttaxon
# Manually replaced the second column with Clen, Crac or Cser
echo -e "sample_id\ttaxon\tpath" > data/mapping.tsv

for i in data/*fasta; do
  BASENAME=$(basename "${i%.fasta}")
  FULL_PATH=$(realpath "${i}")
  echo -e "${BASENAME}\t${BASENAME}\t${FULL_PATH}" >> data/mapping.tsv
done
```

## Snakemake workflow for minimap2/dotplotly

This workflow is designed to run the dotplotly script on multiple genomes. It will generate a dotplot for each genome pair listed in the `config.yaml` file.

For the below to work:

- Install [conda/mamba](https://scienceparkstudygroup.github.io/ibed-bioinformatics-page/source/conda/conda.html) and snakemake (`mamba install -c bioconda snakemake`)
- Ensure that you list all genomes of interest in the `config.yaml` file.

```{bash}
# Code was tested with snakemake 7.32.3
# To setup dependencies defined in env.yaml, preferably use mamba since it is faster
conda activate snakemake 

snakemake --snakefile workflow/Snakefile \
  --configfile config/config.yaml \
  --cores 2 --use-conda --conda-frontend mamba \
  --conda-prefix workflow/.snakemake/conda/
```




## Test another tool: Pafr in R

Vignette for the package can be found [here](https://cran.r-project.org/web/packages/pafr/vignettes/Introduction_to_pafr.html).

```{r}
#install.packages("pafr")

library(pafr)

ali <-  read_paf("results/v2/minimap2/MG753774.1_vs_NC_032042.1.paf")
dotplot(ali, label_seqs = TRUE)
plot_synteny(ali, q_chrom="NC_032042.1", t_chrom="MG753774.1")
```