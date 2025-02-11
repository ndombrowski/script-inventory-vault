import sys
import pandas as pd

def calculate_stats(input_file, column_number):
    # Read the tab-separated file into a DataFrame
    try:
        df = pd.read_csv(input_file, sep='\t')
    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")
        return
    except pd.errors.ParserError:
        print("Invalid file format. Please provide a tab-separated file.")
        return

    # Check if the column number is valid
    if column_number < 1 or column_number > len(df.columns):
        print(f"Column number {column_number} is out of range.")
        return

    # Extract the specified column
    column_data = df.iloc[:, column_number - 1]
    print(column_data)

    # Calculate statistics
    median = column_data.median()
    mean = column_data.mean()
    sd = column_data.std()
    quartiles = column_data.quantile([0.25, 0.5, 0.75])

    # Output the statistics
    print(f"Median: {median}")
    print(f"Mean: {mean}")
    print(f"Standard Deviation: {sd}")
    print("Quartile Ranges:")
    print(f"  25th percentile: {quartiles[0.25]}")
    print(f"  50th percentile (Median): {quartiles[0.5]}")
    print(f"  75th percentile: {quartiles[0.75]}")

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <column_number>")
        sys.exit(1)

    # Extract command line arguments
    input_file = sys.argv[1]
    column_number = int(sys.argv[2])

    # Call the function to calculate statistics
    calculate_stats(input_file, column_number)
