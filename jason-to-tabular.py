import json

def importData(infile):
    readfile = open(infile, "r")
    data = json.load(readfile)
    return data


humanData = importData("data/test_characteristics_human.json")
for GSE_data in humanData.values():
    print(GSE_data.keys())
    break
