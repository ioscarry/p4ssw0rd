#!/usr/local/bin/python2.7
import re
import cProfile
from password import Password

parenMatch = {
    "(": ")",
    "[": "]",
    "{": "}",
    "<": ">",
    ")": "(",
    "]": "[",
    "}": "{",
    ">": "<",
}

def findParts(pw):
    # TODO: Loop through tree instead of parts
    changed = 1
    # Attempt to find border characters before anything else
    pw.findBorder(0)

    # Brute-force all-digit passwords which don't match dates
    if not re.search(r"[^0-9]", pw.parts[0].word):
        pass

    while changed:
        changed = 0
        for part in range(0, len(pw.parts)):
            if pw.parts[part].type:
                continue
            if pw.findDate(part):
                changed = 1
                continue
            if pw.findWord(part):
                changed = 1
                continue
            if pw.findKeyRun(part):
                changed = 1
                continue
            if pw.findRepeated(part):
                changed = 1
                continue
    for part in range(0, len(pw.parts)):
        if not pw.parts[part].type:
            pw.findBruteForce(part)

def reverseParen(word):
    word = list(word)
    for i in range(0, len(word)):
        if word[i] in parenMatch:
            word[i] = parenMatch[word[i]]
    return ''.join(word)

def compareParts(pw):
    """Find patterns involving multiple parts:
    - Border
    - Prefix
    - Repeated Suffix
    - Combination Suffix
    - Brute Force Suffix
    - Dictionary Repeated
    - Combination Dictionary(2)
    - Combination Dictionary(2) (with Delimiter)
    - Combination Dictionary(3)
    - Brute Force"""
    parts = pw.parts

    typeMap = ''.join([part.type[0] for part in pw.parts])

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

    # pattern = prefix
    # pattern = prefix-combination
    # pattern = suffix
    # pattern = suffix-combination

def timeToString(seconds):
    if not seconds:
        return "milliseconds"
    if seconds >= 3155692600:
        return "centuries"
    if seconds >= 315569260:
        return "{} decades".format(seconds // 315569260)
    if seconds >= 31556926:
        return "{} years".format(seconds // 31556926)
    if seconds >= 2629743:
        return "{} months".format(seconds // 2629743)
    if seconds >= 604800:
        return "{} weeks".format(seconds // 604800)
    if seconds >= 86400:
        return "{} days".format(seconds // 86400)
    if seconds >= 3600:
        return "{} hours".format(seconds // 3600)
    if seconds >= 60:
        return "{} minutes".format(seconds // 60)
    return "{} seconds".format(seconds)

def main(pw):
    pw = Password(pw)
    findParts(pw)
    compareParts(pw)

    # Temporary output
    result = []
    totalCost = 1
    for part in pw.parts:
        print part.pattern, "-",
    print
    for part in pw.parts:
        if part.type:
            result.append("<p>Found</p>\n\t<ul><li>part '{}'</li>\n\t<li>type '{}'</li>\n\t<li>mutations '{}'</li>\n\t<li>pattern '{}'</li>\n\t<li>base cost '{}'</li>\n\t<li>total cost '{}'</li></ul>".format(
                part.word, part.type, part.mutations, part.pattern, part.cost, part.finalCost))
            totalCost *= part.finalCost
        else:
            result.append("Found part '{}'".format(part.word))

    result.insert(0, "<p>Offline crack time at 1 billion guesses per second: {}</p>".format(timeToString(totalCost // 1000000000)))

    print '<br>\n'.join(result)
    return '<br>\n'.join(result)

    # Causes problems for web interface - investigating
    #cleanup.cleanup()

if __name__ == "__main__":
    #pw = "checkcorrecthorse"
    #pw = "((!11!No!5))01/49"
    #pw = "08-31-2004"
    #pw = "((-s-u-b-s-t-r-i-n-g-s))$$$$are2008/10/22tricky!@%@"
    pw = "To be or not to be, that is the question"
    #pw = "<<<<notG00dP4$$word>>>>tim2008-08"
    #pw = "wpm,.op[456curwerrrytyk"
    #pw = "$$money$$"
    #pw = "!!andtammytammy!!"
    pw = "--word&second--"
    #cProfile.run('main(pw)')
    main(pw)
