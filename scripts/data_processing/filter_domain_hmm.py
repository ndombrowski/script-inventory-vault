import pandas as pd
import argparse

def is_overlap(hit1, hit2):
    return not (hit1['protein_end'] < hit2['protein_start'] or hit1['protein_start'] > hit2['protein_end'])

def filter_hits(input_file, output_file):
    # Load the data into a pandas DataFrame
    columns = ["protein_id", "protein_length", "KO", "KO_length", "cEvalue", "protein_start", "protein_end", "hmm_from", "hmm_to", "protein_coverage", "hmm_coverage"]
    data = pd.read_csv(input_file, sep="\t", header=None, names=columns)

    # Sort data by protein_id, protein_start, cEvalue, and protein_coverage
    data = data.sort_values(by=["protein_id", "protein_start", "cEvalue", "protein_coverage"], ascending=[True, True, True, False])

    # Initialize an empty list to store the filtered results
    filtered_hits = []

    # Process each protein_id separately
    for protein_id, group in data.groupby('protein_id'):
        non_overlapping_hits = []

        for _, hit in group.iterrows():
            overlap = False
            for existing_hit in non_overlapping_hits:
                if is_overlap(hit, existing_hit):
                    overlap = True
                    break
            
            if not overlap:
                non_overlapping_hits.append(hit)
        
        filtered_hits.extend(non_overlapping_hits)

    # Convert the filtered hits back to a DataFrame
    filtered_df = pd.DataFrame(filtered_hits, columns=columns)

    # Save the results to the output file with a header
    filtered_df.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter hits to find the most reasonable hit for each protein stretch.')
    parser.add_argument('-i', '--input', required=True, help='Input file path')
    parser.add_argument('-o', '--output', required=True, help='Output file path')

    args = parser.parse_args()

    filter_hits(args.input, args.output)

