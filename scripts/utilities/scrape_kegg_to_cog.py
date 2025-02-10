#For each KEGG ID finds associated COG IDs
#usage: python scrape_module_and_kegg.py KEGG-ID outputDir
#for example: /opt/anaconda3/bin/python scrape_module_and_kegg.py K00845 output/

#import libs for the webscraping and downloading the web page
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import sys

#define id to search for
kegg_id = sys.argv[1]

#get url with data relevant for the kegg of interest
url = "https://www.genome.jp/dbget-bin/www_bget?" + kegg_id

#use get to download the contents of the webpage in text format and store in a variable called data:
data = requests.get(url).text

#create a beautiful soup object
soup = BeautifulSoup(data,"html.parser")

#get data of interest
pattern = re.compile(r"https://www.ncbi.*?COG.*?")
COG_ID_results = soup.find_all("a", href=pattern)

#store each element in a list
cog_list = []

for i in COG_ID_results:
    cog_list.append(i.text)
#print(cog_list)

#make a df
COG_to_Kegg_df = pd.DataFrame({'COG_id': cog_list})

#add kog ID
COG_to_Kegg_df["KEGG_id"] = kegg_id

#print
COG_to_Kegg_df.to_csv(sys.argv[2]+kegg_id+'.txt', sep ='\t', index = False)

