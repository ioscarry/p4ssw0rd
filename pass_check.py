#!/usr/local/bin/python2.7
import re, itertools, time
import cProfile, pstats
import cleanup
from password import Password
from time_to_string import timeToString

class PassCheck(object):
    parenMatch = {
        "(": ")",
        "[": "]",
        "{": "}",
        "<": ">",
        ")": "(",
        "]": "[",
        "}": "{",
        ">": "<"}

    def __init__(self, password):
        self.password = Password(password)

    def findParts(self):
        """Searches for possible patterns in the given Password object.
        Returns True if any match is found, False if not."""
        while True:
            for part in self.password.getParts():
                if part.type:
                    continue
                #if not self.password.checkMemo(part):
                if len(part.word) >= 9:
                    self.password.findWord(part, minLength = len(part.word) // 2)
                    if not self.password.queue:
                        for min_ in range(len(part.word) // 2 - 1, 1, -1):
                            self.password.findWord(
                                part, minLength=min_, start=len(part.word) - min_,
                                returnFirst=True)
                            if self.password.queue:
                                break
                # Disabled for performance
#                elif 2 <= len(part.word) <= 4:
#                    self.password.findWord(part, minLength=2, returnFirst=True)
                else:
                    self.password.findWord(part, minLength=3)
                self.password.findEmail(part)
                self.password.findDate(part, returnFirst=True)
                self.password.findKeyRun(part)
                if len(part.word) > 2:
                    self.password.findRepeated(part, minLength=3)
                else:
                    self.password.findRepeated(part, minLength=2)
                self.password.findBruteForce(part)
            if self.password.queue:
                self.password.addParts()
            else:
                break

    def reverseParen(self, word):
        word = list(word)
        for i in range(0, len(word)):
            if word[i] in self.parenMatch:
                word[i] = self.parenMatch[word[i]]
        return ''.join(word)

    def findLowestCost(self):
        lowestCost = float('inf')
        finalParts = []
        finalPatterns = []
        for parts in self.password.getParts(combination = True):
            (patterns, cost) = self.compareParts(parts, lowestCost)
            if cost < lowestCost:
                lowestCost = cost
                finalParts = parts
                finalPatterns = patterns
        for index, part in enumerate(finalParts):
            part.pattern = finalPatterns[index]
        self.finalParts = finalParts

    def compareParts(self, parts, lowestCost):
        typeMap = ''.join([part.type[0] for part in parts])

        # Parts are shared between combinations - can't modify them!
        patterns = [None] * len(parts)

        # Dictionary-repeated
        # pattern = word-repeat
        result = re.finditer(r"(?=(ww))", typeMap)
        for match in result:
            start = match.start()
            if parts[start].word == parts[start + 1].word:
                if not patterns[start]:
                    patterns[start] = "word-repeat"
                if patterns[start + 1]:
                    patterns[start + 1] = "word-repeat"

        # Dictionary-combination(2)
        # pattern = word-combination
        result = re.finditer(r"(?=(ww))", typeMap)
        for match in result:
            start = match.start()
            if not patterns[start]:
                patterns[start] = "word-combination"
            if not patterns[start + 1]:
                patterns[start + 1] = "word-combination"

        # Dictionary-combination (delimiter)
        # pattern = word-combination-delimiter

        result = re.finditer(r"(?=(w[rdb]w))", typeMap)
        for match in result:
            start = match.start()
            if not patterns[start]:
                patterns[start] = "word-combination"
            if not patterns[start + 1]:
                patterns[start + 1] = "word-combination-delimiter"
            if not patterns[start + 2]:
                patterns[start + 2] = "word-combination"

        # Borders
        # pattern = border-repeat
        result = re.finditer(r"([brd]).+\1", typeMap)
        for match in result:
            start = match.start()
            for end in range(start, len(parts)):
                if parts[start].word == parts[end].word:
                    if not patterns[start]:
                        patterns[start] = "border-repeat"
                    if not patterns[end]:
                        patterns[end] = "border-repeat"
                elif parts[start].word == parts[end].word[::-1] or \
                     parts[start].word == self.reverseParen(parts[end].word):
                    if not patterns[start]:
                        patterns[start] = "border-mirror"
                    if not patterns[end]:
                        patterns[end] = "border-mirror"

        for index in range(0, len(parts)):
            if patterns[index]:
                break
            else:
                patterns[index] = 'prefix'
        for index in range(len(parts) - 1, -1, -1):
            if patterns[index]:
                break
            else:
                patterns[index] = 'suffix'

        cost = 1
        for pattern, part in itertools.izip(patterns, parts):
            cost *= part.finalCost
        return patterns, cost

class Analysis(object):
    def __init__(self, word, cost=0, time=0):
        self.word = word
        self.cost = cost
        self.time = time
        self.parts = []

    def addPart(self, part):
        self.parts.append(part)

def main(pw=None, randomPassword=False):
    if randomPassword:
        import os, random
        passwordFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "words", "work", "rockyou.txt")
        f = open(passwordFile, "r")
        size = os.stat(passwordFile).st_size
        f.seek(random.randint(0, size))
        f.readline()
        pw = str(f.readline().rstrip("\r\n"))
        f.close()
    elif not pw:
        return None

    pw = str(pw)
    timeStart = time.time()
    pc = PassCheck(pw)
    pc.findParts()
    pc.findLowestCost()
    timeRun = time.time() - timeStart
    parts = pc.finalParts
    result = Analysis(pw, time=timeRun)

    totalCost = 1
    for part in parts:
        totalCost *= part.finalCost
        result.addPart(part)
    result.cost = timeToString(totalCost // 1000000000)

    cleanup.cleanup()

    return result

if __name__ == "__main__":
    profile = 0
    randomPassword = 1
    pw = "qwerbunchasdfsmall"
    pw = "correcthorsebattery"
    pw = "((!11!No!5))01/49"
    pw = "This is a long, but terrible passphrase."
    pw = "22200" # 2/22/00?
    #pw = "10/23/99"
    #pw = "123qweasdzxc"
    #pw = "08-31-2004"
    #pw = "dog$hose"
    #pw = "To be or not to be, that is the question"
    #pw = "<<notG00dP4$$word>>tim2008-09-04"
    #pw = "asdfawrbteabfdagawe"
    #pw = "wpm,.op[456curkky"
    #pw = "$$money$$"
    #pw = "!!andtammytammy!!"
    #pw = "--word&second--"
    #pw = "$$money"
    #pw = "B3taM4le"
    #pw = "$$thing$$"
    #pw = "2009/04/21"
    pw = "everything and nothing are together at last"
    # Possible bugs from rockyou.txt
    #pw = "kirsygirl23"
    #pw = "ali19-45"
    #pw = "rubenaNDJUanito"
    #pw = "imranskuri"
    #pw = "rheybeth"
    #pw = "brewstabb"
    #pw = "5mona$$$"
    #pw = "tuktik2517"
    pw = "ffffffffffffffff"

    if randomPassword:
        result = main(randomPassword=True)
    else:
        result = main(pw)
    if profile:
        command = 'main(pw)'
        cProfile.runctx(
            command, globals(), locals(), filename="random-chars.profile")
        p = pstats.Stats('random-chars.profile')
        p.sort_stats('cum')
        p.print_stats(1)
    else:
        print "Word: {}".format(result.word)
        print "Time: {}".format(result.time)
        print "Cost: {}".format(result.cost)
        for part in result.parts:
            print "Part: '{}'".format(part.word)
            print "\tType: {}".format(part.type)
            print "\tMutations: {}".format(part.mutations)
            print "\tPattern: {}".format(part.pattern)
            print "\tCost: {}".format(part.cost)
            print "\tTotal Cost: {}".format(part.finalCost)
