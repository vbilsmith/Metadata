import matplotlib.pyplot as plt
import string
import json
from itertools import combinations

def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator).split()  # Split the text into a list of words after removing punctuation

# Load data from JSON file
with open('/Users/hildanashiferaw/Documents/ResearchVBIL/Metadata-main/data/test_characteristics_human.json', 'r') as json_file:
    data = json.load(json_file)
    #print(data)

# Count word pairs within each row
word_pair_counts = {}
for value in data.values():  # Iterate over the values of the outer dictionary
    if isinstance(value, dict):  # Check if the value is a dictionary
        keys = list(value.keys())
        keys = remove_punctuation(" ".join(keys))  # Convert keys to a list of words
        for pair in combinations(keys, 2):  # Generate all possible combinations of word pairs
            word_pair_counts[pair] = word_pair_counts.get(pair, 0) + 1

# Visualize the result
if word_pair_counts:
    pairs, counts = zip(*word_pair_counts.items())
    x = range(len(pairs))
    plt.bar(x, counts)
    plt.xlabel('Word Pairs')
    plt.ylabel('Count')
    plt.title('Word Pair Counts within Each Row')
    plt.xticks(x, pairs, rotation=45, ha='right')
    plt.show()
    #print(word_pair_counts)
else:
    print("No word pairs found in the data.")