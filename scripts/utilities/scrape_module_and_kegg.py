#For each KEGG module finds associated KEGG IDs in order how the appear in the pathway
#usage: python scrape_module_and_kegg.py ModuleID outputDir
#for example: /opt/anaconda3/bin/python scrape_module_and_kegg.py M00307 output/

#import libs for the webscraping and downloading the web page
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
import sys

#set pathway to search
module_id = sys.argv[1]

#set url
url = "https://www.genome.jp/module/" + module_id

#use get to download the contents of the webpage in text format and store in a variable called data:
data = requests.get(url).text

#create a beautiful soup object
soup = BeautifulSoup(data,"html.parser")

#scrape KO IDs
Definitions = soup.findAll("div", class_ = 'definition')

for result in Definitions:
    categories = result.find_all("td")
    KOs = categories[5].text
    print()

#parse KO ids
KO_char = KOs[:]
KO_char = KO_char.strip('\n ')
KO_char = KO_char.partition('\n')[0]
KO_char = re.sub(r'(K[0-9]+(?=K))',r'\1 ', KO_char)
KO_char = re.sub("\s+", ";", KO_char.strip())
KO_char = re.sub(r"\([^\(\)]+\)", lambda x: x.group(0).replace(";", ","), KO_char)
KO_char = re.sub(r'\((.*?)\)',r'\1', KO_char)
KO_char = re.sub(r"\([^\(\)]+\)", lambda x: x.group(0).replace(";", ","), KO_char)
KO_char = re.sub(r'\((.*?)\)',r'\1', KO_char)
KO_char = re.sub("\(", "", KO_char.strip())
KO_char = re.sub("\)", "", KO_char.strip())
KO_char = re.sub("\+", ",", KO_char.strip())
KO_char = re.sub("\-", ",", KO_char.strip())
KO_char = re.sub("-", '', KO_char)
KO_char = KO_char.split(";")

#print to df
df = pd.DataFrame({'KO_ID': KO_char})

#add dummy columns for the order and add column for module ID
df["Order"] = np.arange(df.shape[0])+1
df["Module"] = module_id

#split
df['KO_ID'] = df['KO_ID'].str.split(',')
df = df.explode('KO_ID')

#drop empty columns
df= df[df.KO_ID != '']

#print to file
df.to_csv(sys.argv[2]+module_id+'.txt', sep ='\t', index = False)

