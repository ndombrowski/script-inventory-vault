```python
#load libs
import pandas as pd
import os

#define files we want to work with 
Inputpath = 'Annotations/Annotations.txt'

#metabolism order for KOs
Metabolism_file_KOs = pd.read_csv(os.path.join(os.environ["metabolism_mapping"], 'Metabolism_Clusters_Apr2020_v5.txt'), sep='\t')

# Read in input data
##################################################################
#Input
Input = pd.read_csv(Inputpath, sep='\t')
Input.shape

#make a subset to only include relevant columns
Input_subset = Input[['BinID', 'accession', 'KO_hmm', 'FAMA_Description']]
Input_subset.head(n=5)

#melt df
Input_long = pd.melt(Input_subset, id_vars=['BinID','accession'], value_vars=['KO_hmm','FAMA_Description'])

#change colnames to something more informative
Input_long.columns = ['BinID', 'accession', 'DB', 'gene']
Input_long.head(n=5)

#make a list of bins we are interested in --> 24
bin_list = list(Input_long['BinID'].unique())
len(bin_list)

# Make a list of all gene IDs and their descriptions
##################################################################
KOs = Input[['KO_hmm','KO_Definition']].drop_duplicates()
KOs.columns = ['gene','Description']
KOs['Database'] ='KO'

Sulfur_FAMA=Input[['FAMA_Description','FAMA_Description']].drop_duplicates()
Sulfur_FAMA.columns = ['gene','Description']
Sulfur_FAMA['Database'] ='FAMA'

#merge db info
Gene_description = pd.concat([KOs, Sulfur_FAMA])

# For make a count table for genes/genome
##################################################################
Counts_bins = Input_long.groupby(['BinID','gene', 'DB']).count()
Counts_bins.head()

#remove rows with no hit
Counts_bins_2 = Counts_bins[Counts_bins.index.get_level_values(1) != '-']

#move the index into the df
Counts_bins_2.reset_index(inplace=True) 

#check if all is looking ok
Counts_bins_2.head()

#add cluster names (for printing)
#Counts_bins_long = pd.merge(Counts_bins_2,design[["BinID", "Bins_per_Cluster", "Cluster2Name"]], on='BinID', how = 'left')

#add gene description (for printing)
Counts_bins_long2 = pd.merge(Counts_bins_2,Gene_description, on='gene', how = 'left')
Counts_bins_long2.head()

#convert df from long to wide
Count_bins_wide = Counts_bins_2.pivot(index='gene', columns='BinID', values='accession').fillna(0)

#check
Count_bins_wide.head(n=5)

##add in a description column based on Gene_description
Count_bins_wide_2 = pd.merge(Count_bins_wide,Gene_description, on='gene')
Count_bins_wide_2.head(n=5)

#change column order
#cols = list(Count_bins_wide_2.columns)
#cols = [cols[0]] + [cols[-2]] + [cols[-1]] + cols[1:-2]
list1 = ['gene' , 'Description' , 'Database' ]
list2 = list1 + bin_list
Count_bins_wide_2 = Count_bins_wide_2[list2]

#check
Count_bins_wide_2.head(n=2)
Count_bins_wide_2.shape

#print
Count_bins_wide_2.to_csv('Annotations/python_parsing/Bins_counts_allDB_thiopac.txt', index = False, sep = '\t')

# Summarize metabolism data based on KOs
##################################################################
#merge tables
KO_metabolism = pd.merge(Metabolism_file_KOs ,Count_bins_wide_2, how='left', left_on='KO', right_on='gene').fillna(0)

#check
KO_metabolism.head(n=2)
KO_metabolism.shape

#print to file
KO_metabolism.to_csv('Annotations/python_parsing/Bins_Metabolism_by_KO.txt', index = False, sep = '\t')
```