import re
import argparse

def clean_transcripts(input_file, output_file):
    # Regular expression patterns
    gene_id_pattern = r'gene_id \"([^\"]+?)\^.*?\"'
    transcript_id_pattern = r'transcript_id \"(.*?)\.p[0-9]+\"'

    # Open the input file and output file
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Replace the gene_id part using the regular expression
            modified_line = re.sub(gene_id_pattern, r'gene_id "\1"', line)
            
            # Replace the transcript_id part to remove .p[0-9]
            modified_line = re.sub(transcript_id_pattern, r'transcript_id "\1"', modified_line)

            # Write the modified line to the output file
            outfile.write(modified_line)

    print(f"File has been cleaned and saved as {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean gene_id entries in a GTF file.")
    parser.add_argument("--input", required=True, help="Path to the input GTF file.")
    parser.add_argument("--output", required=True, help="Path to the output GTF file.")

    args = parser.parse_args()

    clean_transcripts(args.input, args.output)

