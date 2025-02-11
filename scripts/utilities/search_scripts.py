import json
import argparse
from fuzzywuzzy import fuzz

def load_scripts(json_file):
    """Load the script inventory from a JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def search_scripts(scripts, search_term=None, language=None, threshold=80, exact=False):
    """Search scripts by title, description, or tag using fuzzy or exact matching, with an optional language filter."""
    results = []
    search_term = search_term.lower() if search_term else None
    language = language.lower() if language else None  # Normalize language for comparison

    for script in scripts:
        match = True  # Assume match by default

        # Apply search term filter if provided
        if search_term:
            if exact:
                # Exact match
                title_match = search_term == script['title'].lower()
                desc_match = search_term in script['description'].lower()
                tags_match = any(search_term == tag.lower() for tag in script['tags'])
            else:
                # Fuzzy match
                title_match = fuzz.partial_ratio(search_term, script['title'].lower()) >= threshold
                desc_match = fuzz.partial_ratio(search_term, script['description'].lower()) >= threshold
                tags_match = any(fuzz.partial_ratio(search_term, tag.lower()) >= threshold for tag in script['tags'])
            match = title_match or desc_match or tags_match

        # Apply language filter if provided
        script_language = script.get('language', '').lower()  # Default to empty string if missing
        if language and script_language != language:
            match = False

        if match:
            results.append(script)

    return results

def print_script(script):
    """Print details of a single script."""
    print("-" * 40)
    print(f"Title: {script['title']}")
    print(f"File: {script['file']}")
    print(f"Description: {script['description']}")
    print(f"Tags: {', '.join(script['tags'])}")
    print(f"Usage: {script.get('usage', 'N/A')}")
    print(f"Language: {script.get('language', 'N/A')}")
    print(f"Author: {script.get('author', 'N/A')}")
    print(f"Date created: {script.get('date_created', 'N/A')}")
    print("-" * 40)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Search scripts in a JSON inventory.")
    parser.add_argument("--exact", action="store_true", help="Perform an exact search instead of fuzzy search.")
    args = parser.parse_args()

    json_file = "index.json"
    scripts = load_scripts(json_file)

    # Get user input
    search_term = input("Enter a search term (or press Enter to skip): ").strip()
    language = input("Filter by language (Python, R, Bash, etc.) or press Enter to skip: ").strip()

    # Prompt for exact search if not specified
    if not args.exact and search_term:
        exact_search = input("Do you want to perform an exact search? (yes/no): ").strip().lower()
        if exact_search in ['yes', 'y']:
            args.exact = True

    results = search_scripts(scripts, search_term=search_term, language=language, exact=args.exact)

    if results:
        print(f"Found {len(results)} matching scripts:")
        for script in results:
            print_script(script)
    else:
        print("No matching scripts found.")

if __name__ == "__main__":
    main()