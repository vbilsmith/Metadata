#!/usr/bin/env python

"""GSE Accession Analysis for human: Wordcloud for GSM Characteristics
 by Xinran Bi

 Modified by Halie Rando as follows:
- Converted from GSE_scrape_human.ipynb on Jan 14 at 12:05pm using `jupyter nbconvert --to script`
- Debugged return statement being outside of an if loop
- Refactored to use the same code for both mouse and human
"""
import re
import json
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd

def import_GSE(species):
    """Filters a dataframe form GREIN by species
    Accepts: species name ("mouse" or "human")
    Returns: pandas dataframe
    """
    GREIN_data = pd.read_csv("data/GREIN_data.csv")
    if species == "mouse":
        return GREIN_data[GREIN_data.Species == 'Mus musculus']['GEO accession'].tolist()
    if species == "human":
        return GREIN_data[GREIN_data.Species == 'Homo sapiens']['GEO accession'].tolist()
    print("Error: Unknown species")
    sys.exit(1)


def scrape_geo_data(geo_id):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}".format(geo_id)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <a> tags with href attributes containing "GSM"
            gsm_links = soup.find_all('a',
                                      href=lambda href: href and href.startswith('/geo/query/acc.cgi?acc=GSM'))

            # Extract and store only the GSM values
            gsm_values = [link.text for link in gsm_links]

            return gsm_values

        return "Failed to retrieve the page. Status code: {0}".format(response.status_code)

    except requests.exceptions.RequestException as e:
        return "Error: {0}".format(e)


def scrape_characteristics(geo_id):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}".format(geo_id)

    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

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
    input_str = re.sub(r'<td[^>]*>', '', input_str)  # remove <td> tags
    pattern = r'(\w+): ([^<]+)'
    matches = re.findall(pattern, input_str)
    characteristics_dictionary = dict(matches)
    return characteristics_dictionary

def save_results_to_file(results, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for result in results:
            file.write(result + '\n')

# Define species from standard in
species = sys.argv[1]

# Identify all relevant GSEs for this species
GSEs = import_GSE(species)
GSM = []
for GSE in GSEs:
    GSMs = scrape_geo_data(GSE)
    GSM.append(GSMs)
    #data[GSE] = GSMs
GSM1 = len(GSM)

if GSMs:
    GSM = [item for sublist in GSM for item in sublist] #flatten the list
GSM2 = len(GSM)

if GSM1 != GSM2:
    print("There is a bug-- the first GSM list is {0} and the second is {1}".format(GSM1, GSM2))
    sys.exit(1)

results = {}
for GSM in GSM:
    characteristics_string = scrape_characteristics(GSM)
    characteristics_dictionary = extract_characteristics(characteristics_string)
    results[GSM] = characteristics_dictionary
    #print(f"Characteristics for {GSM}: {characteristics_dictionary}")

json_file = "data/test_characteristics_{0}.json".format(species)
with open(json_file, "w") as file:
    json.dump(results, file)

print("Characteristics saved to {0}".format(json_file))
