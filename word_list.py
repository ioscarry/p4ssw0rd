"""
Sources:
ftp://ftp.openwall.com/pub/wordlists/
http://www.skullsecurity.org/wiki/index.php/Passwords
http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists
http://contest-2010.korelogic.com/wordlists.html
"""

import os, re, mmap, string
import binary_search
import cProfile
from word_list_index import wordFiles

searchMemo = {}

type = ['letter','digit','letterapostrophe','combined']
rootPath = os.path.dirname(os.path.realpath(__file__))
wordPath = os.path.join(rootPath, "words")
workPath = os.path.join(rootPath, "words", "work")
wordListIndex = os.path.join(rootPath, "word_list_index.py")

# Defines the order in which wordlists are searched - used for convertFiles only
wordsOrder = [
    "openwall-password.dic",
    "rockyou_top1000.dic",
    "numbers_as_words.dic",
    "names.dic",
    "tv-1-5000-special.dic",
    "tv-1-5000.dic",
    "tv-5000-10000-special.dic",
    "tv-5000-10000.dic",
    "english-tiny-cap.dic",
    "english-tiny-lower.dic",
    "contemporaryfiction-special.dic",
    "contemporaryfiction.dic",
    "bible_books.dic",
    "cities.dic",
    "places.dic",
    "english-small-alnum.dic",
    "english-small-cap.dic",
    "english-small-lower.dic",
    "english-small-mixed.dic",
    "sports.dic",
    "sports_proteams.dic",
#    "english-large-acronym.dic",
#    "english-large-alnum.dic",
#    "english-large-cap.dic",
#    "english-large-lower.dic",
#    "english-large-mixed.dic",
#    "english-extra-acronym.dic",
#    "english-extra-alnum.dic",
#    "english-extra-cap.dic",
#    "english-extra-lower.dic",
#    "english-extra-mixed.dic",
]

def convertFiles():
    """Takes wordlists, copies, calculates and appends frequency, concatenates
    and splits based on length, then sorts by first character."""
    lines = 0
    maxLength = 0
    tempFiles = []
    for fn in wordsOrder:
        fIn = open(os.path.join(workPath, fn), "r")

        # Save for deletion later
        fnOut = os.path.join(wordPath, fn)
        tempFiles.append(fnOut)
        fOut = open(fnOut, "w")
        for line in fIn:
            lines += 1
            length = len(line.rstrip("\n\r"))
            if length > maxLength:
                maxLength = length
            fOut.write("{}\t{}\n".format(line.rstrip("\n\r"), lines))
        fIn.close()
        fOut.close()

    # Create new files: "len1, len2", etc (no zero padding)
    lenFiles = {}
    for i in range(1, maxLength + 1):
        lenFiles[i] = open(
            os.path.join(wordPath, str(i) + ".dic"), "w")

    for fn in wordsOrder:
        fIn = open(os.path.join(wordPath, fn), "r")
        for line in fIn:
            length = len(line.split("\t")[0])
            lenFiles[length].write(line)
        fIn.close()

    for fn in lenFiles.values():
        fn.close()

    # Sort and remove duplicates. Slow, but only runs once on wordlist changes
    for fn in lenFiles:
        f = open(os.path.join(wordPath, str(fn) + ".dic"), "r")

        # Remove duplicates and keep the lower line numbers
        lines = {}
        for line in f:
            base, count = line.rstrip("\n\r").split("\t")
            count = int(count)
            if base in lines and lines[base] < count:
                continue
            else:
                lines[base] = count
        f.close()
        lines = sorted(["{}\t{}\n".format(k, v) for k, v in lines.iteritems()])
        f = open(os.path.join(wordPath, str(fn) + ".dic"), "w")
        for line in lines:
            f.write(line)
        f.close()

    for fn in tempFiles:
        os.remove(fn)

def indexFiles():
    fIndex = open(wordListIndex, "w")
    fIndex.write("wordFiles = {\n")
    for fn in os.listdir(wordPath):
        maxLength = 0
        if not fn.endswith(".dic"):
            continue
        size = int(os.stat(os.path.join(wordPath, fn)).st_size)
        f = open(os.path.join(wordPath, fn), "r")
        if not size:
            continue
        contents = mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ)
        f.close()

        # Letter indexing
        stack = []

        letterIndex = {}
        for letter in sorted(string.printable):
            result = re.search(r"^{}".format(re.escape(letter)), contents, re.M)
            if result:
                start = result.start()
                while len(stack) > 0:
                    stack.pop().append(start)
                letterIndex[letter] = [start,]
                stack.append(letterIndex[letter])
                lastPos = start
        while len(stack) > 0:
            element = stack.pop()
            if element[0]:
                element.append(size)
            else:
                element.append(0)

        letterIndex = {k: tuple(v) for k, v in letterIndex.items()}
        fIndex.write('\t{}:{{"name":"{}", "handle":None, "letterIndex":{}}},\n'.format(
            fn.split(".")[0], fn, letterIndex))
    fIndex.write("}")
    fIndex.close()

def openFiles():
    for fn in wordFiles.values():
        fn["handle"] = open(os.path.join(wordPath, fn["name"]), "r")

def closeFiles():
    for fn in wordFiles:
        fn["handle"].close()

def searchDictionary(word):
    global searchMemo
    # Open files if necessary
    if word in searchMemo:
        return searchMemo[word]
    if len(word) not in wordFiles:
        return False
    if wordFiles[1]["handle"] is None:
        openFiles()
    fn = wordFiles[len(word)]

    first = word[0]
    if first not in fn["letterIndex"]:
        return False
    length = len(word)

    location = binary_search.searchFile(
        fn["handle"],
        word,
        fn["letterIndex"][first][0],
        fn["letterIndex"][first][1],
        splitChar="\t")
    searchMemo[word] = location
    if location:
        return location
    return False

if __name__ == "__main__":
    #cProfile.run("findWord('illinois')")
    convertFiles()
    indexFiles()