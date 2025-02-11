import re
import os
import glob
import pandas as pd
import argparse

def parse_log_file(file_path):
    """
    Parse a log file and extract total sequences, rRNA sequences, and calculate the percentage of rRNA sequences.
    """
    # Extract the sample name from the file path
    sample_name = os.path.basename(file_path).replace(".log", "")
    
    # Initialize variables to store the extracted values
    total_sequences = "NA"
    rRNA_sequences = "NA"
    
    # Define a function to clean ANSI escape codes
    def clean_ansi_escape_codes(text):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', text)
    
    # Open and read the log file
    with open(file_path, 'r') as file:
        for line in file:
            # Clean the line from ANSI escape codes
            line_cleaned = clean_ansi_escape_codes(line)
            
            # Extract total sequences
            if "Processed" in line_cleaned:
                match = re.search(r"Processed (\d+) sequences", line_cleaned)
                if match:
                    total_sequences = int(match.group(1))
            # Extract rRNA sequences
            if "rRNA sequences" in line_cleaned:
                match = re.search(r"Detected (\d+) rRNA sequences", line_cleaned)
                if match:
                    rRNA_sequences = int(match.group(1))
    
    # Calculate the percentage of rRNA sequences
    if total_sequences != "NA" and rRNA_sequences != "NA":
        rRNA_percentage = round((rRNA_sequences / total_sequences) * 100, 2)
    else:
        rRNA_percentage = "NA"
    
    return [sample_name, total_sequences, rRNA_sequences, rRNA_percentage]

def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Parse log files and generate a dataframe.")
    parser.add_argument("-i", "--input", help="Input directory containing log files", required=True)
    parser.add_argument("-o", "--output", help="Output file path for the dataframe", required=True)
    args = parser.parse_args()
    
    # Get all log files matching the pattern
    log_files = glob.glob(os.path.join(args.input, "*.log"))
    
    # Initialize a list to store the results
    results = []
    
    # Process each log file
    for file_path in log_files:
        results.append(parse_log_file(file_path))
    
    # Create a dataframe from the results
    df = pd.DataFrame(results, columns=["Sample", "Total", "rRNA", "rRNA_Percentage"])
    
    # Write dataframe to output file
    df.to_csv(args.output, index=False)

if __name__ == "__main__":
    main()
