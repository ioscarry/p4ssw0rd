"""
Small script to convert files for usage.
"""

import re

regexSpecial = re.compile("[^a-zA-Z\n]")

#fnIn = open("tv-1-5000.dic", "r")
#fnOut = open("tv-1-5000-lower.dic", "wb")
#fnSpec = open("tv-1-5000-special.dic", "wb")

#fnIn = open("tv-5000-10000-unsorted.dic", "r")
#fnOut = open("tv-5000-10000.dic", "w")
#fnSpec = open("tv-5000-10000-special.dic", "w")

#fnIn = open("contemporaryfiction.dic", "r")
#fnOut = open("contemporaryfiction-lower.dic", "w")
#fnSpec = open("contemporaryfiction-special.dic", "w")

#fnIn = open("english.dic", "r")
#fnOut = open("english-lower.dic", "wb")
#fnSpec = open("english-special.dic", "wb")
for line in fnIn:
    if re.search(regexSpecial, line):
        fnSpec.write(line.lower())
    else:
        fnOut.write(line.lower())

fnIn.close()
fnOut.close()
fnSpec.close()
