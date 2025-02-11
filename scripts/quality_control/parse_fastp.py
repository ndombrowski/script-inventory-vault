import re
import glob
import csv
import argparse

def parse_fastp_log(log_file_path):
    with open(log_file_path, 'r') as file:
        log_content = file.read()
    
    # Extracting sample ID
    sample_id_match = re.search(r'HTML report: .*/(.*)\.fastp-trim\.report\.html', log_content)
    sample_id = sample_id_match.group(1) if sample_id_match else "Unknown"

    # Extracting the numerical values with error handling
    def extract_value(pattern, content):
        match = re.search(pattern, content)
        return int(match.group(1)) if match else None

    reads_passed_filter = extract_value(r'reads passed filter: (\d+)', log_content)
    reads_failed_low_quality = extract_value(r'reads failed due to low quality: (\d+)', log_content)
    reads_failed_too_many_N = extract_value(r'reads failed due to too many N: (\d+)', log_content)
    reads_failed_too_short = extract_value(r'reads failed due to too short: (\d+)', log_content)
    reads_with_adapter_trimmed = extract_value(r'reads with adapter trimmed: (\d+)', log_content)
    bases_trimmed_due_to_adapters = extract_value(r'bases trimmed due to adapters: (\d+)', log_content)

    return {
        'sample_id': sample_id,
        'reads_passed_filter': reads_passed_filter,
        'reads_failed_low_quality': reads_failed_low_quality,
        'reads_failed_too_many_N': reads_failed_too_many_N,
        'reads_failed_too_short': reads_failed_too_short,
        'reads_with_adapter_trimmed': reads_with_adapter_trimmed,
        'bases_trimmed_due_to_adapters': bases_trimmed_due_to_adapters
    }

def create_summary_table(log_files_pattern, output_csv_path):
    log_files = glob.glob(log_files_pattern)
    summary_data = []

    for log_file in log_files:
        log_data = parse_fastp_log(log_file)
        summary_data.append(log_data)

    # Writing the summary data to a CSV file
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['sample_id', 'reads_passed_filter', 'reads_failed_low_quality', 'reads_failed_too_many_N',
                      'reads_failed_too_short', 'reads_with_adapter_trimmed', 'bases_trimmed_due_to_adapters']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in summary_data:
            writer.writerow({
                'sample_id': data['sample_id'],
                'reads_passed_filter': data['reads_passed_filter'],
                'reads_failed_low_quality': data['reads_failed_low_quality'],
                'reads_failed_too_many_N': data['reads_failed_too_many_N'],
                'reads_failed_too_short': data['reads_failed_too_short'],
                'reads_with_adapter_trimmed': data['reads_with_adapter_trimmed'],
                'bases_trimmed_due_to_adapters': data['bases_trimmed_due_to_adapters']
            })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse fastp log files and create a summary CSV file.')
    parser.add_argument('-i', '--input', required=True, help='Input file pattern (e.g., logs/fastp_52399_*.err)')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file path')

    args = parser.parse_args()
    create_summary_table(args.input, args.output)

