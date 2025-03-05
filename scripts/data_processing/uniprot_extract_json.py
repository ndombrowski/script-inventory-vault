import json
import argparse
import pandas as pd

# Function to process the JSON and extract the necessary data into a DataFrame
def extract_ids_and_names(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)
    
    # Extract the 'from' IDs and 'name'
    records = []
    for result in data["results"]:
        from_id = result["from"]
        name = result["to"]["name"].replace("Cluster: ", "")
        # Replace commas with an alternative if needed
        #name = name.replace(",", "")
        records.append({"uniprot_ID": from_id, "uniprot_name": name})
    
    # Create a DataFrame
    df = pd.DataFrame(records)
    
    # Save DataFrame to a CSV file
    df.to_csv(output_file, index=False)

# Main function to handle argparse
def main():
    parser = argparse.ArgumentParser(description='Extract IDs and names from a JSON file into a DataFrame.')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input JSON file path')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output CSV file path')

    args = parser.parse_args()

    # Extract data from JSON and write to the output file
    extract_ids_and_names(args.input, args.output)

if __name__ == "__main__":
    main()

