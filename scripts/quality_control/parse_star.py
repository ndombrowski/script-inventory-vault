import pandas as pd
import os
import glob
import argparse

def parse_log_file(filepath):
    data = {}
    with open(filepath, 'r') as file:
        for line in file:
            if '|' in line:
                key, value = line.split('|')
                key = key.strip().replace(',', ';')
                key = key.strip()
                value = value.strip()
                data[key] = value
    return data

def main(input_folder, output_file):
    # Get all log files matching the pattern *final* in the input folder
    log_files = glob.glob(os.path.join(input_folder, '*final*'))

    # Create an empty DataFrame
    df = pd.DataFrame()

    # Loop through each file and parse its contents
    for log_file in log_files:
        # Parse the log file
        data = parse_log_file(log_file)
        
        # Convert the data to a DataFrame
        log_df = pd.DataFrame(data, index=[0]).T
        
        # Extract the relevant part of the filename (e.g., IDHF_B1T0)
        file_id = os.path.basename(log_file).split('_Log')[0]
        
        # Use the extracted part of the filename as the column header
        log_df.columns = [file_id]
        
        # Merge with the main DataFrame
        df = pd.concat([df, log_df], axis=1)

    # Reset index for better readability
    df.reset_index(inplace=True)
    df.columns = ['Metric'] + [os.path.basename(f).split('_Log')[0] for f in log_files]

    # Save the DataFrame to a CSV file
    df.to_csv(output_file, index=False)
    print(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Parse log files and merge them into a DataFrame.')
    parser.add_argument('--input_folder', required=True, help='The folder in which to look for the log files.')
    parser.add_argument('-o', '--output_file', required=True, help='The output CSV file to save the merged data.')

    # Parse arguments
    args = parser.parse_args()

    # Call the main function with parsed arguments
    main(args.input_folder, args.output_file)

