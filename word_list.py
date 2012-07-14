"""
Sources:
ftp://ftp.openwall.com/pub/wordlists/
http://www.skullsecurity.org/wiki/index.php/Passwords
http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists
http://contest-2010.korelogic.com/wordlists.html
"""

import os
import sqlite3

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
]

def addWordsToDB():
    conn = sqlite3.connect('wordlist.db')
    c = conn.cursor()
    lineMemo = {}

    c.execute("CREATE TABLE IF NOT EXISTS words(word VARCHAR(60), location INTEGER)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS word_index ON words (word)")

    lines = 0
    for fn in wordsOrder:
        fIn = open(os.path.join(workPath, fn), "r")
        for line in fIn:
            line = line.rstrip("\n\r")
            if line in lineMemo:
                continue
            elif line:
                lines += 1
                c.execute("INSERT INTO words VALUES (?, ?)", (line.decode('utf-8'), lines))
                lineMemo[line] = True
        conn.commit()
    conn.close()