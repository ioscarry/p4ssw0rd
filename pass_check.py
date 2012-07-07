#!/usr/local/bin/python2.7
import re, copy
import cProfile, pstats
from password import Password
from time_to_string import timeToString

parenMatch = {
    "(": ")",
    "[": "]",
    "{": "}",
    "<": ">",
    ")": "(",
    "]": "[",
    "}": "{",
    ">": "<"}

def findParts(pw):
    """Searches for all possible patterns in the given Password object. Returns
     True if any match is found, False if not."""
    for part in pw.getParts():
        #print "{} | {} | {}".format(part, part.prev, part.next)
        if part.type:
            continue
        if not pw.checkMemo(part):
            pw.findDate(part)
            pw.findWord(part)
            pw.findKeyRun(part)
            pw.findRepeated(part)
            pw.findBruteForce(part)
    if pw.queue:
        pw.addParts()
        return True
    return False

def reverseParen(word):
    word = list(word)
    for i in range(0, len(word)):
        if word[i] in parenMatch:
            word[i] = parenMatch[word[i]]
    return ''.join(word)

def compareParts(parts, sim = False):
    typeMap = ''.join([part.type[0] for part in parts])

    # Dictionary-repeated
    # pattern = word-repeat
    result = re.finditer("(?=(ww))", typeMap)
    for match in result:
        start = match.start()
        if parts[start].word == parts[start + 1].word:
            if not parts[start].pattern:
                parts[start].pattern = "word-repeat"
            if not parts[start + 1].pattern:
                parts[start + 1].pattern = "word-repeat"

    # Dictionary-combination(2)
    # pattern = word-combination
    result = re.finditer("(?=(ww))", typeMap)
    for match in result:
        start = match.start()
        if not parts[start].pattern:
            parts[start].pattern = "word-combination"
        if not parts[start + 1].pattern:
            parts[start + 1].pattern = "word-combination"

    # Dictionary-combination (delimiter)
    # pattern = word-combination-delimiter
    result = re.finditer("(?=(w[rdb]w))", typeMap)
    for match in result:
        start = match.start()
        if not parts[start].pattern:
            parts[start].pattern = "word-combination"
        if not parts[start + 1].pattern:
            parts[start + 1].pattern = "word-combination-delimiter"
        if not parts[start + 2].pattern:
            parts[start + 2].pattern = "word-combination"

    # Borders
    # pattern = border-repeat
    for part in parts:
        print part, part.pattern

    result = re.finditer(r"([brd]).+\1", typeMap)
    for match in result:
        start = match.start()
        for end in parts[start:]:
            if parts[start].word == end.word:
                if not parts[start].pattern:
                    parts[start].pattern = "border-repeat"
                if not end.pattern:
                    end.pattern = "border-repeat"
            elif parts[start].word == end.word[::-1] or \
                 parts[start].word == reverseParen(end.word):
                if not parts[start].pattern:
                    parts[start].pattern = "border-mirror"
                if not end.pattern:
                    end.pattern = "border-mirror"

    for part in parts:
        if part.pattern:
            break
        else:
            part.pattern = 'prefix'
    for part in parts[::-1]:
        if part.pattern:
            break
        else:
            part.pattern = 'suffix'

    cost = 1
    for part in parts:
        cost *= part.finalCost
    return cost

def main(pw):
    pw = Password(pw)
    while findParts(pw):
        pass
    lowestCost = float('inf')
    for parts in pw.getParts(combination = True):
#        for part in parts:
#            print part
#        print
        cost = compareParts(parts)
        if cost < lowestCost:
            lowestCost = cost
            finalParts = parts

    result = []
    totalCost = 1
    for part in finalParts:
        if part.type:
            result.append("<p>Found</p>\n\t<ul><li>part '{}'</li>\n\t<li>type '{}'</li>\n\t<li>mutations '{}'</li>\n\t<li>pattern '{}'</li>\n\t<li>base cost '{}'</li>\n\t<li>total cost '{}'</li></ul>".format(
                part.word, part.type, part.mutations, part.pattern, part.cost, part.finalCost))
            totalCost *= part.finalCost
        else:
            result.append("Found part '{}'".format(part.word))

    result.insert(0, "<p>Offline crack time at 1 billion guesses per second: {}</p>".format(timeToString(totalCost // 1000000000)))

    print '<br>\n'.join(result)
    return '<br>\n'.join(result)

if __name__ == "__main__":
    #pw = "correcthorsebatterystaple"
    pw = "((!11!No!5))01/49"
    #pw = "08-31-2004"
    #pw = "dog$hose"
    #pw = "To be or not to be, that is the question"
    #pw = "<<<<notG00dP4$$word>>>>tim2008-08"
    #pw = "wpm,.op[456curkky"
    #pw = "$$money$$"
    #pw = "!!andtammytammy!!"
    #pw = "--word&second--"
    #pw = "$$money"
    #pw = "B3taM4le"
    pw = "$$thing$$"
#    cProfile.run('main(pw)', 'p4ssw0rd_correcthorsebattery')
#    p = pstats.Stats('p4ssw0rd_correcthorsebattery')
#    p.sort_stats('cum')
#    p.print_stats()
    main(pw)