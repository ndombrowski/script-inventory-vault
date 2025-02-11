import os
import argparse
from collections import defaultdict

# Define the main function
def main(input_folder, search_prefix, output_file, protein_id_column):
    # Dictionary to store counts of genome-marker pairs
    genome_marker_dict = defaultdict(list)

    # Traverse through each file in the directory
    for filename in os.listdir(input_folder):
        if filename.startswith(search_prefix):
            filepath = os.path.join(input_folder, filename)
            
            with open(filepath, 'r') as file:
                for line in file:
                    columns = line.strip().split()
                    genome_id = columns[0]
                    marker_id = columns[1]
                    protein_id = columns[protein_id_column - 1]  # Adjust index for 1-based columns
                    
                    genome_marker_dict[(genome_id, marker_id)].append(protein_id)

    # Identify duplicates
    duplicates = {key: value for key, value in genome_marker_dict.items() if len(value) > 1}

    # Write the results to the output file
    with open(output_file, 'w') as out_file:
        out_file.write("GenomeID\tMarkerID\tCount\tEntries\n")
        for (genome_id, marker_id), entries in duplicates.items():
            entry_str = ';'.join(entries)
            out_file.write(f"{genome_id}\t{marker_id}\t{len(entries)}\t{entry_str}\n")

# Define command-line arguments using argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process COG marker files and find duplicates.')
    parser.add_argument('--inputfolder', type=str, required=True, help='Path to the input folder containing the files')
    parser.add_argument('--search-prefix', type=str, required=True, help='Prefix to search for in file names')
    parser.add_argument('--output', type=str, required=True, help='Path to the output file where results will be saved')
    parser.add_argument('--protein-column', type=int, default=5, help='Column index (1-based) containing the protein ID (default: 5)')

    args = parser.parse_args()

    main(args.inputfolder, args.search_prefix, args.output, args.protein_column)
