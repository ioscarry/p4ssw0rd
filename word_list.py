import os, re
import binary_search
import cProfile

regexNotLowercase = re.compile("[^a-z]")
regexNotLowercaseApostrophe = re.compile("[^a-z']")

type = ['letter','number','letterapostrophe','combined']
wordPath = "words"
wordFiles = [
    {"name":"rockyou_top1000.dic",  "handle":None, "lines":1000,    "type":3},
    {"name":"contemporaryfiction.dic","handle":None,"lines":0,      "type":0},
    {"name":"contemporaryfiction-special.dic","handle":None,"lines":0,"type":2},
    {"name":"english.dic",          "handle":None, "lines":639446,  "type":0},
    {"name":"english-special.dic",  "handle":None, "lines":639446,  "type":2},
    {"name":"tv-1-5000.dic",        "handle":None, "lines":4995,    "type":0},
    {"name":"tv-1-5000-special.dic","handle":None, "lines":4995,    "type":2},
    {"name":"names.dic",            "handle":None, "lines":4425,    "type":0},
    {"name":"places.dic",           "handle":None, "lines":15450,   "type":0},
    {"name":"cities.dic",           "handle":None, "lines":123011,  "type":0},
    {"name":"tv-5000-10000.dic",    "handle":None, "lines":4995,    "type":0},
    {"name":"tv-5000-10000-special.dic","handle":None,"lines":4995, "type":2},
    {"name":"bible_books.dic",      "handle":None, "lines":81,      "type":0},
    {"name":"sports.dic",           "handle":None, "lines":684,     "type":0},
    {"name":"sports_proteams.dic",  "handle":None, "lines":130,     "type":0}]

def openFiles():
    for fn in wordFiles:
        fn["handle"] = open(os.path.join("words", fn["name"]), "r")

def findWord(word):
    # Open files if necessary
    if wordFiles[0]["handle"] is None:
        openFiles()

    lineCount = 0
    for fn in wordFiles:
        if re.search(regexNotLowercase, word) and fn["type"] == 0:
            continue
        location = binary_search.searchFile(fn["handle"], word)
        if location:
            return lineCount + int(location * fn["lines"])
        else:
            lineCount += fn["lines"]
    return False

if __name__ == "__main__":
    cProfile.run("findWord('illinois')")