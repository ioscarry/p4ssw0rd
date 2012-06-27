import os, re
import binary_search
import cProfile

regex_no_lowercase = re.compile("[^a-z]")

type = ['letter','number','combined']
wordPath = "words"
wordFiles = [
    {"name":"rockyou_top1000.dic",  "handle":None, "lines":1000,    "type":2},
    #{"name":"tv-movies-1-5000", "handle":None, "lines":0},
    {"name":"names.dic",            "handle":None, "lines":4425,    "type":0},
    #{"name":"names_male.dic",       "handle":None, "lines":7084,    "type":0},
    #{"name":"names_female.dic",     "handle":None, "lines":7084,    "type":0},
    {"name":"places.dic",           "handle":None, "lines":15450,   "type":0},
    {"name":"cities.dic",           "handle":None, "lines":123011,  "type":0},
    #{"name":"tv-movies-5000-10000", "handle":None, "lines":0},
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
        if re.search(regex_no_lowercase, word) and fn["type"] != 0:
            continue
        location = binary_search.searchFile(fn["handle"], word)
        if location:
            return lineCount + int(location * fn["lines"])
        else:
            lineCount += fn["lines"]
    return False

if __name__ == "__main__":
    cProfile.run("findWord('illinois')")