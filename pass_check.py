#!/usr/local/bin/python2.7
import re, itertools, time
import cProfile, pstats
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
        """Searches for possible patterns in the given Password object, and
        tells the object to add the new parts."""
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
        """Returns the matching character for any of '([{<'."""
        word = list(word)
        for i in range(0, len(word)):
            if word[i] in self.parenMatch:
                word[i] = self.parenMatch[word[i]]
        return ''.join(word)

    def findLowestCost(self):
        """Compares the cost of each possible combination, and saves the lowest-
        cost one."""
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
        self.finalCost = lowestCost

    def compareParts(self, parts, lowestCost):
        """Searches for known patterns in the given combination of parts, and
        calculates a cost based on the approximate cost of cracking each one."""
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
                if not patterns[start + 1]:
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
            for end in range(start + 1, len(parts)):
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

        # If there are no patterns, attempt to find the "base" - word or date
        if not any(patterns):
            for index in range(0, len(typeMap)):
                if typeMap[index] in "wd":
                    patterns[index] = "base"
                    break
            else:
                patterns[0] = "base"

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
        borderCount =  0
        repeatCount =  0
        combinations = []
        attachments =  []
        for pattern, part in itertools.izip(patterns, parts):
            # TODO: Replace with generalized cases, pull from costs
            if pattern == "prefix":
                attachments.append(part.cost * 2)
            elif pattern == "suffix":
                attachments.append(part.cost)
            elif pattern == ("border-repeat"):
                if borderCount:
                    continue
                cost *= part.finalCost
            elif pattern == ("border-mirror"):
                if borderCount:
                    continue
                cost *= part.finalCost * 2
            elif pattern == "word-repeat":
                if repeatCount:
                    cost *= 2
                cost *= part.finalCost
            elif pattern == "word-combination":
                combinations.append(part.cost)
                cost *= part.mutationCost
            else:
                cost *= part.finalCost
        if combinations:
            if max(combinations) < 20000:
                cost *= 20000 ** len(combinations)
            else:
                cost *= max(combinations) ** len(combinations)
        if attachments:
            cost *= max(attachments) ** len(attachments)
        return patterns, cost

class Analysis(object):
    """Object which contains the result sent to web template"""
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
        passwordFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "rockyou.txt")
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

    for part in parts:
        result.addPart(part)
    result.cost = timeToString(pc.finalCost // 1000000000)

    return result

if __name__ == "__main__":
    profile = 0
    randomPassword = 0
    pw = "eunuchportraitracisttangent333"           # Long analyze time - 2.4s
    #pw = "342008"                                   # Not picked up as date
    #pw = "D0g.................................$.."

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
