import os
import argparse

def read_html(file_path):
    """Read HTML file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_html(file_path, content):
    """Save modified HTML content to a new file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def add_barcode_id_to_html(html_file):
    """Add barcode ID to a single HTML file"""
    # Read the HTML content
    html_content = read_html(html_file)

    # Extract barcode number (folder name)
    barcode_folder = os.path.basename(os.path.dirname(html_file))
    barcode_name = barcode_folder.replace("barcode", "Barcode ")

    # Create the barcode header as raw HTML
    barcode_header = f'<div style="font-size: 24px; font-weight: bold; margin-top: 20px; text-align: center;">{barcode_name}</div>'

    # Prepend the barcode header to the HTML content
    modified_html_content = barcode_header + html_content

    return modified_html_content

def combine_html_files(base_path, output_html, start_barcode=None, end_barcode=None):
    """Combine all LengthvsQualityScatterPlot_dot.html files in the base_path directory into a single HTML file, sorted by barcode ID"""
    combined_html = ""

    # Loop through all barcode folders in the base_path
    barcode_folders = [f for f in os.listdir(base_path) if f.startswith("barcode")]
    
    # Sort the barcode folders by the numeric part of the barcode ID
    barcode_folders.sort(key=lambda folder: int(folder.replace("barcode", "")))

    # If a range is specified, filter the barcode folders
    if start_barcode is not None:
        barcode_folders = [f for f in barcode_folders if int(f.replace("barcode", "")) >= start_barcode]
    if end_barcode is not None:
        barcode_folders = [f for f in barcode_folders if int(f.replace("barcode", "")) <= end_barcode]

    if not barcode_folders:
        print("No barcode folders found in the specified range!")
        return

    # Process each barcode folder
    for barcode_folder in barcode_folders:
        barcode_folder_path = os.path.join(base_path, barcode_folder)
        
        # Check if LengthvsQualityScatterPlot_dot.html exists in the folder
        html_file = os.path.join(barcode_folder_path, "LengthvsQualityScatterPlot_dot.html")
        
        if os.path.exists(html_file):
            print(f"Processing {html_file}...")

            # Add barcode ID to the HTML content
            modified_html_content = add_barcode_id_to_html(html_file)

            # Append the modified HTML content to the combined HTML
            combined_html += modified_html_content

    # Save the combined HTML to the output file
    save_html(output_html, combined_html)
    print(f"Combined HTML saved as: {output_html}")

def main(base_path, output_html, start_barcode, end_barcode):
    # Combine all relevant HTML files into one, possibly filtered by barcode range
    combine_html_files(base_path, output_html, start_barcode, end_barcode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine LengthvsQualityScatterPlot_dot.html files from each barcode folder into one, adding barcode ID to each and sorting by barcode ID.")
    parser.add_argument("--base_path", required=True, help="Base directory containing barcode folders")
    parser.add_argument("--output_html", required=True, help="Output HTML file name")
    parser.add_argument("--start_barcode", type=int, default=None, help="Start barcode number to process (inclusive)")
    parser.add_argument("--end_barcode", type=int, default=None, help="End barcode number to process (inclusive)")
    args = parser.parse_args()
    main(args.base_path, args.output_html, args.start_barcode, args.end_barcode)

