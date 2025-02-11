import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Analyze protein lengths from a FASTA file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input FASTA file.")
    parser.add_argument("--threshold", type=int, default=None, help="Custom threshold for extreme protein lengths.")
    args = parser.parse_args()

    # File path from arguments
    file_path = args.input
    threshold = args.threshold

    # Initialize variables
    seq_lengths = []
    protein_names = []
    current_length = 0
    current_name = ""

    try:
        # Parse the file
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith(">"):  # Header line
                    if current_length > 0:  # Save the previous sequence length and name
                        seq_lengths.append(current_length)
                        protein_names.append(current_name)
                    current_name = line.strip()  # Save the current header
                    current_length = 0  # Reset for the new sequence
                else:  # Sequence line
                    current_length += len(line.strip())

            # Append the last sequence length and name
            if current_length > 0:
                seq_lengths.append(current_length)
                protein_names.append(current_name)

        # Calculate basic stats
        num_proteins = len(seq_lengths)
        min_length = min(seq_lengths)
        max_length = max(seq_lengths)
        mean_length = sum(seq_lengths) / len(seq_lengths)
        median_length = np.median(seq_lengths)

        # Find the name of the protein with the max length
        max_index = seq_lengths.index(max_length)
        max_name = protein_names[max_index]

        # Analyze extreme lengths
        percentile_95 = np.percentile(seq_lengths, 95)  # 95th percentile
        extreme_length_threshold = threshold if threshold else percentile_95  # Use custom threshold if provided
        num_extreme_proteins = sum(1 for length in seq_lengths if length > extreme_length_threshold)
        extreme_proteins = [
            (name, length) for name, length in zip(protein_names, seq_lengths) if length > extreme_length_threshold
        ]

        # Print results
        print(f"Number of proteins: {num_proteins}")
        print(f"Min length: {min_length}")
        print(f"Max length: {max_length} (Protein: {max_name})")
        print(f"Mean length: {mean_length:.2f}")
        print(f"Median length: {median_length}")
        print(f"95th percentile length: {percentile_95}")
        print(f"Number of proteins with length > {extreme_length_threshold}: {num_extreme_proteins}")

        # Optional: Print extreme proteins
        #if extreme_proteins:
        #    print("\nProteins with extreme lengths:")
        #    for name, length in extreme_proteins[:10]:  # Limit to first 10 for readability
        #        print(f"{name} (Length: {length})")

        # Optional: Plot histogram
        plt.hist(seq_lengths, bins=50, edgecolor='black', alpha=0.75)
        plt.axvline(x=extreme_length_threshold, color='red', linestyle='--', label=f"Threshold = {extreme_length_threshold}")
        plt.axvline(x=percentile_95, color='green', linestyle='--', label="95th Percentile")
        plt.title("Distribution of Protein Lengths")
        plt.xlabel("Protein Length")
        plt.ylabel("Frequency")
        plt.legend()
        plt.show()

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

