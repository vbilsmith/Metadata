import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import string


def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

with open('data/test_characteristics_human.json', 'r') as json_file:
    data = json.load(json_file)

attribute_texts = []

for key, value in data.items():
    # Include the attribute key and its value
    attribute_text = f"{key}: {str(value)}"
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
    url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={geo_id}"

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
            return f"Failed to retrieve the page. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def extract_characteristics(input_str):
    input_str = re.sub(r'<td[^>]*>', '', input_str)  # remove <td> tags

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

    # print(f"Characteristics for {geo_id}: {characteristics_dictionary}")

print("Attribute Counts:")
for attribute, count in attribute_counts.items():
    print(f"{attribute}: {count}")