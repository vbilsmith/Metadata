#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re
import json
from tqdm import trange
import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import string

"""GSE Accession Analysis for human: Wordcloud for GSM Characteristics
 by Xinran Bi
 
 Modified by Halie Rando as follows:
- Converted from GSE_scrape_human.ipynb on Jan 14 at 12:05pm using `jupyter nbconvert --to script`
- Debugged return statement being outside of an if loop
- Refactored to use the same code for both mouse and human
"""

species = mouse

def import_GSE(species):
    """Filters a dataframe form GREIN by species
    Accepts: species name ("mouse" or "human")
    Returns: pandas dataframe
    """
    GREIN_data = pd.read_csv("data/GREIN_data.csv")
    if species == "mouse":
        GREIN = GREIN_data[GREIN_data.Species == 'Mus musculus']
    elif species == "human":
        GREIN = GREIN_data[GREIN_data.Species == 'Homo sapiens']
    GSE = GREIN['GEO accession'].tolist()
    return GSE

def scrape_geo_data(geo_id):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}".format(geo_id)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <a> tags with href attributes containing "GSM"
            gsm_links = soup.find_all('a', href=lambda href: href and href.startswith('/geo/query/acc.cgi?acc=GSM'))

            # Extract and store only the GSM values
            gsm_values = [link.text for link in gsm_links]

            return gsm_values

        else:
            return "Failed to retrieve the page. Status code: {0}".format(response.status_code)

    except requests.exceptions.RequestException as e:
        return "Error: {0}".format(e)


GSEs = import_GSE(species)
GSM = []
for GSE in GSEs:
    GSMs = scrape_geo_data(GSE)
    GSM.append(GSMs)
    #data[GSE] = GSMs

if GSMs:
    GSM = [item for sublist in GSM for item in sublist] #flatten the list

def save_results_to_file(results, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for result in results:
            file.write(result + '\n')

csv_file_path = "data/GSM_human.csv"
# with open(csv_file_path, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(GSM_human)

def scrape_characteristics(geo_id):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}".format(geo_id)

    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            characteristics_dict = {}
            
            # Find the "Characteristics" label
            characteristics_label = soup.find('td', text='Characteristics')
            
            if characteristics_label:
                # Get the next sibling (which contains the characteristics content)
                characteristics_content = characteristics_label.find_next_sibling('td')
                characteristics_string = str(characteristics_content)

                return characteristics_string

    
        return "Failed to retrieve the page. Status code: {0}".format(response.status_code)

    except requests.exceptions.RequestException as e:
        return "Error: {0}".format(e)

def extract_characteristics(input_str):
    input_str = re.sub(r'<td[^>]*>', '', input_str) # remove <td> tags
    pattern = r'(\w+): ([^<]+)'
    matches = re.findall(pattern, input_str)
    characteristics_dictionary = dict(matches)
    return characteristics_dictionary

geo_id = "GSM2683998"
characteristics_string = scrape_characteristics(geo_id)
characteristics_dictionary = extract_characteristics(characteristics_string )
print("characteristics_dictionary:", characteristics_dictionary)


results = {}
for GSM in GSM:
    characteristics_string = scrape_characteristics(GSM)
    characteristics_dictionary = extract_characteristics(characteristics_string)
    results[GSM] = characteristics_dictionary
    #print(f"Characteristics for {GSM}: {characteristics_dictionary}")

json_file = "data/test_characteristics_human.json"
with open(json_file, "w") as file:
    json.dump(results, file)

print("Characteristics saved to {0}".format(json_file))


def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

with open('data/test_characteristics_human.json', 'r') as json_file:
    data = json.load(json_file)

attribute_texts = []

for key, value in data.items():
    # Include the attribute key and its value
    attribute_text = "{0}: {str(1)}".format(key, value)
    attribute_texts.append(attribute_text)

text_data = " ".join(attribute_texts)

text_data = text_data.lower()

text_data = remove_punctuation(text_data)

wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()


def scrape_characteristics(geo_id):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}".format(geo_id)

    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            characteristics_dict = {}
            
            # Find the "Characteristics" label
            characteristics_label = soup.find('td', text='Characteristics')
            
            if characteristics_label:
                # Get the next sibling (which contains the characteristics content)
                characteristics_content = characteristics_label.find_next_sibling('td')
                characteristics_string = str(characteristics_content)

            return characteristics_string

        else:
            return "Failed to retrieve the page. Status code: {0}".format(response.status_code)

    except requests.exceptions.RequestException as e:
        return "Error: {0}".format(e)


def extract_characteristics(input_str):
    
    input_str = re.sub(r'<td[^>]*>', '', input_str) # remove <td> tags
    
    pattern = r'(\w+): ([^<]+)'
    matches = re.findall(pattern, input_str)
    
    characteristics_dictionary = {}
    
    for attribute, value in matches:
        characteristics_dictionary[attribute] = characteristics_dictionary.get(attribute, 0) + 1


   # characteristics_dictionary = dict(matches)
    
    return characteristics_dictionary



attribute_counts = {}

for geo_id in GSM:
    characteristics_string = scrape_characteristics(geo_id)
    characteristics_dictionary = extract_characteristics(characteristics_string)

    for attribute in characteristics_dictionary:
 
        if attribute in attribute_counts:
           
            attribute_counts[attribute] += 1
        else:

            attribute_counts[attribute] = 1

    #print(f"Characteristics for {geo_id}: {characteristics_dictionary}")

print("Attribute Counts:")
for attribute, count in attribute_counts.items():
    print("{0}: {1}".format(attribute, count))

