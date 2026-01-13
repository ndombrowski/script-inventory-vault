import requests
from bs4 import BeautifulSoup
import pandas as pd
import re 


# --------------------------------- Get HTML --------------------------------- #
url = "https://www.kegg.jp/kegg/pathway.html"
response = requests.get(url)
html_content = response.text
soup = BeautifulSoup(html_content, "html.parser")

# -------------------------------- Store data -------------------------------- #
data = []

# Find h4 tags with level 1 categories
h4_tags = soup.find_all('h4', id=True)

for h4 in h4_tags:
    level1_raw = h4.get_text(strip=True)
    level1 = re.sub(r'^\d+\.\s*', '', level1_raw)
    
    # Navigate to the next sibling after this h4
    current = h4.find_next_sibling()
    level2 = ''
    
    while current and current.name != 'h4':
        # Check if current element is a b tag (level2 header)
        if current.name == 'b':
            level2_raw = current.get_text(strip=True)
            level2 = re.sub(r'^\d+\.\d+\s*', '', level2_raw)
        
        # Check if current element is a div with class "list"
        elif current.name == 'div' and 'list' in current.get('class', []):
            # Find the dl element inside
            dl = current.find('dl')
            if dl:
                # Find all dt tags (they come before their corresponding dd tags)
                dt_tags = dl.find_all('dt')
                
                for dt in dt_tags:
                    # Extract only the numeric map ID (5 digits)
                    dt_text = dt.get_text(strip=True)
                    mapid = re.match(r'^\d+', dt_text).group() if re.match(r'^\d+', dt_text) else ''
                    mapid_clean = "map" + mapid
                    
                    # Find the corresponding dd tag (next sibling)
                    dd = dt.find_next_sibling('dd')
                    if dd:
                        link = dd.find('a')
                        if link:
                            # Extract pathway name (level3)
                            pathway_text = link.get_text(strip=True)
                            
                            data.append({
                                'level1': level1,
                                'level2': level2,
                                'level3': pathway_text,
                                'pathway_map': mapid_clean
                            })
        
        current = current.find_next_sibling()

# Create DataFrame
df = pd.DataFrame(data)


df.to_csv("kegg_pathway_hierarchy.csv", index = None)

