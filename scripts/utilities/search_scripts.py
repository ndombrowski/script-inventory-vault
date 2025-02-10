import json
from fuzzywuzzy import fuzz

def load_scripts(json_file):
    """Load the script inventory from a JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

from fuzzywuzzy import fuzz

def search_scripts(scripts, search_term=None, threshold=80):
    """Search scripts by title, description, or tag using fuzzy matching."""
    results = []
    for script in scripts:
        match = False
        if search_term:
            # Check fuzzy match for title, description, and tags
            title_match = fuzz.partial_ratio(search_term.lower(), script['title'].lower()) >= threshold
            desc_match = fuzz.partial_ratio(search_term.lower(), script['description'].lower()) >= threshold
            tags_match = any(fuzz.partial_ratio(search_term.lower(), tag.lower()) >= threshold for tag in script['tags'])
            match = title_match or desc_match or tags_match
        else:
            match = True  # If no search term, include all scripts

        if match:
            results.append(script)
    return results

def print_script(script):
    """Print details of a single script."""
    print(f"Title: {script['title']}")
    print(f"File: {script['file']}")
    print(f"Description: {script['description']}")
    print(f"Tags: {', '.join(script['tags'])}")
    print(f"Usage: {script['usage']}")
    print(f"Language: {script.get('language', 'N/A')}")
    print(f"Author: {script.get('author', 'N/A')}")
    print(f"Date created: {script.get('lastdate_created_updated', 'N/A')}")
    print("-" * 40)

def main():
    json_file = "index.json"
    scripts = load_scripts(json_file)

    # Example search
    search_term = input("Enter a search term (or press Enter to skip): ").strip()
    #tag = input("Enter a tag to filter by (or press Enter to skip): ").strip()

    results = search_scripts(scripts, search_term=search_term)

    if results:
        print(f"Found {len(results)} matching scripts:")
        for script in results:
            print_script(script)
    else:
        print("No matching scripts found.")

if __name__ == "__main__":
    main()