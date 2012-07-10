#!/usr/local/bin/python2.7
import copy, re, string
import word_list, key_graph
from collections import deque

class Part(object):
    def __init__(self, word, type=None, mutations=None, cost=1, pattern=None,
                 prev=None, next=None):
        if mutations is None: mutations = []
        if not isinstance(mutations, list):
            mutations = [mutations]
        if prev is None:
            prev = deque()
        if next is None:
            next = deque()
        self.word = word
        self.type = type
        self.mutations = mutations
        self.pattern = pattern
        self.cost = cost
        # Part acts as graph / doubly-linked list
        self.prev = prev
        self.next = next

    def __repr__(self):
#        return "word: {}, type: {}, mutations: {}".format(
#            self.word, self.type, self.mutations)
        return "Part: {} ({})".format(self.word, self.type)

    def _getFinalCost(self):
        multi = 1
        for mutation in self.mutations:
            multi *= mutation.cost
        return self.cost * multi

    finalCost = property(_getFinalCost)

class Mutation(object):
    typeCost = {
        "delimiter": 20,
        "leet": 64,
        "charSwap": 49,
        "charRemove": 49,
        "charDupe": 49,}

    def __init__(self, type, index):
        self.type = type
        self.index = index

    def __repr__(self):
        return "{}: {}".format(self.type, self.index)

    def _getCost(self):
        if self.type == "case":
            if self.index == "[0]":
                return 2
            else:
                return len(self.index)
        if self.type == "upper":
            return 3
        if self.type == "leet":
            return 64
        if self.type == "delimiter":
            return 128
        if self.type in ("charSwap", "charDupe", "charRemove"):
            if len(self.index) == 1:
                return self.index[0]
            else:
                return len(self.index) * 8
        return 1

    cost = property(_getCost)

class Password(object):
    SYMBOLS = tuple('`~!@#$%^&*()-_=+[{]}\\|;:\'",<.>/?')
    BORDERS = ('xx','x','')
    LEET = {
        '4':['a'],
        '@':['a'],
        '8':['b'],
        '(':['c'],
        '3':['e'],
        '9':['g'],
        '#':['h'],
        '!':['i'],
        '1':['l'],
        '0':['o'],
        '2':['r'],
        '5':['s'],
        '$':['s'],
        '7':['t'],
        '%':['z']}

    def __init__(self, password):
        # TODO: Save type of each character (lower, number, symbol) to avoid so many regex calls later
        root = Part('', type="root", cost=1)
        password = Part(word=password, prev=deque((root,)))
        root.next = deque((password,))
        self.root = root
        self.queue = []
        self.queueMemo = {}

    def subPermutations(self, word, start=0, minLength=4):
        """Generates all possible substrings, from longest to shortest."""
        length = len(word)
        endRange = length - minLength + 2
        for i in range(start+1, endRange):
            start = -1
            end = length-i
            for j in range(0, i):
                start += 1
                end += 1
                yield (word[:start], word[end:], word[start:end])

    def removeDelimiter(self, word, minNum=4):
        """Search for a delimiter between each character.
        Returns an array of changes and the modified string."""
        # word: "p-a-s-s-w-o-r-d"
        # word: "-p-a-s-s-2008"
        # word: "---$-$---@%"
        # check first character for delimiter
        # check every other character from there on
        # minimum match length of 4 by default
        count = 1
        replaced = []
        symbols = "`~!@#$%^&*()-_=+[{]};:\\'\",<.>/? "
        if word[0] in symbols:
            start = 0
        elif word[1] in symbols:
            start = 1
        else:
            return replaced, word
        for i in range(start, len(word), 2):
            if word[i] == word[start]:
                count += 1
                replaced.append(i)
            else:
                break
        if count >= minNum:
            # do this separately since we can't modify while iterating
            word = list(word)
            for i in replaced[::-1]:
                del word[i]
            return replaced, ''.join(word)
        return [], word


    def removeLeet(self, word):
        """Removes common letter and number/symbol substitutions.
        Can function as a generator, in case there is more than one
        possible result (functionality is currently disabled for performance,
        but will be needed with the pervasive i,l=1,1 and i,l=!,! replacements).

        Returns a tuple: (number of replacements made, word)."""

        result = [[]]
        replaced = []
        for index, char in enumerate(list(word)):
            # Special exception for multiple un-leeting choices:
            if char in self.LEET and len(self.LEET[char]) > 1:
                result += copy.deepcopy(result)
                for resultSub in result[:len(result) / 2]:
                    resultSub.append(self.LEET[char][0])
                for resultSub in result[len(result) / 2:]:
                    resultSub.append(self.LEET[char][1])
                replaced.append(index)
                continue

            elif char in self.LEET:
                char = self.LEET[char][0]
                replaced.append(index)

            for resultSub in result:
                resultSub.append(char)

        for temp in result:
            yield replaced, ''.join(temp)

    def removeCase(self, word):
        """Returns an index of all uppercase letters, and the word in
        lowercase."""
        replaced = [index for index, char in enumerate(word) if char.isupper()]
        return replaced, word.lower()

#    def checkMemo(self, part):
#        if part.word in self.queueMemo:
#            if self.queueMemo:
#                for item in self.queueMemo[part.word]:
#                    self.addQueue(part, item[0], item[1], item[2], item[3],
#                                  item[4], item[5], memo=True)
#            return True
#        else:
#            self.queueMemo[part.word] = []
#        return False

    def findWord(self, part, minLength=4, start=0, returnFirst=False):
        """Removes and saves mutations, then attempts to find the largest
        dictionary word (larger than minLength characters) within the given part
        index."""
        word = part.word
        for prefix, suffix, sub in self.subPermutations(
            word, minLength=minLength, start=start):
            mutations = []
            replaced, sub = self.removeDelimiter(sub)
            if replaced:
                mutations.append(Mutation('delimiter', replaced))

            replaced, sub = self.removeCase(sub)
            if replaced and len(replaced) == len(sub):
                mutations.append((Mutation('upper', replaced)))
            elif replaced:
                mutations.append((Mutation('case', replaced)))

            for replaced, subUnLeet in self.removeLeet(sub):
                cost = word_list.searchDictionary(subUnLeet)
                if cost:
                    if replaced:
                        mutations.append(Mutation('leet', replaced))
                        # Replace part, indicate that it is a word
                    self.addQueue(
                        part, prefix, suffix, subUnLeet, "word", mutations, cost)
                    if returnFirst:
                        return
                elif replaced:
                    # Need to also check un-leeted word against special-
                    # character wordlists
                    cost = word_list.searchDictionary(sub)
                    if cost:
                        self.addQueue(
                            part, prefix, suffix, sub, "word", mutations, cost)
                        if returnFirst:
                            return

    def isYear(self, num):
        if (1940 <= num <= 2020) or (40 <= num <= 99) or (0 <= num <= 20):
            return True
        return False

    def isDate(self, place1, place2, place3):
        """Return a date type if a date is valid, False if not. Day, Month, and
        Year can be in any order. Does not currently check for valid days
        depending on length of month."""
        if not place2 and not place3:
            # Y only
            if self.isYear(place1):
                return 'date', 75
        elif not place3:
            # MD or YM
            if (1 <= place1 <= 12 and 1 <= place2 <= 31) or (
                1 <= place2 <= 12 and 1 <= place1 <= 31):
                return 'date', 372+75
            elif (1 <= place1 <= 12 and self.isYear(place2)) or (
                1 <= place2 <= 12 and self.isYear(place1)):
                return 'date', 900+372+75
        else:
            # YMD
            if self.isYear(place1):
                if (1 <= place2 <= 12 and 1 <= place3 <= 31) or (
                    1 <= place3 <= 12 and 1 <= place2 <= 31):
                    return 'date', 164250+900+372+75
                # Have to check both for dates such as 01/04/01
            if self.isYear(place1):
                if (1 <= place1 <= 12 and 1 <= place2 <= 31) or (
                    1 <= place2 <= 12 and 1 <= place1 <= 31):
                    return 'date', 164250+900+372+75
        return False, False

    def addQueue(self, part, prefix, suffix, sub, type=None, mutations=None,
                 cost=None, memo=False):
#        if not memo:
#            # TODO: Required for unit testing - may be worth refactoring
#            if not part.word in self.queueMemo:
#                self.queueMemo[part.word] = []
#            self.queueMemo[part.word].append(
#                [prefix, suffix, sub, type, mutations, cost])
        self.queue.append([part, Part(prefix), Part(suffix),
                           Part(sub, type, mutations, cost)])

    def getParts(self, combination=False):
        """Iteratively return either all parts, or all possible combination of parts."""
        stack = [(self.root, 0)]
        node = self.root.next[0]
        part = 0
        while True:
            if node.next and part < len(node.next):
                if part == 0 and not combination:
                    yield node
                stack.append((node, part))
                node = node.next[part]
                part = 0
            elif node.next:
                if stack:
                    node, part = stack.pop()
                else:
                    break
                part += 1
            else:
                #for part in node.next:
                if node.word and combination:
                    yield [i[0] for i in stack if i[0].word] + [node]
                elif node.word and not combination:
                    yield node
                node, part = stack.pop()
                part += 1

    def addParts(self):
        for (part, prefix, suffix, sub) in self.queue:
            if prefix.word:
#                self.parts.append(prefix)
                prefix.prev = part.prev
                prefix.next.append(sub)
                sub.prev.append(prefix)
                for node in part.prev:
                    node.next.append(prefix)
            else:
                sub.prev = part.prev
                for node in part.prev:
                    node.next.append(sub)
#            self.parts.append(sub)
            if suffix.word:
#                self.parts.append(suffix)
                sub.next.append(suffix)
                suffix.prev.append(sub)
                suffix.next = part.next
                for node in part.next:
                    node.prev.append(suffix)
            else:
                sub.next = part.next
                for node in part.next:
                    node.prev.append(sub)
        for (part, prefix, suffix, sub) in self.queue:
#            if part in self.parts:
#                self.parts.remove(part)
            for node in part.next:
                if part in node.prev:
                    node.prev.remove(part)
            for node in part.prev:
                if part in node.next:
                    node.next.remove(part)
        self.queue = []


    def findDate(self, part):
        """Search for a date in any possible format.
        Performs a general regex for date formats, then validates digits."""
        word = part.word
        for prefix, suffix, sub in self.subPermutations(word, minLength=4):
            if re.search(r"[a-zA-Z]", sub):
                continue
            result = re.match(r"((19|20)\d{2}|\d{2})([-/_. ])?([0-3]?[0-9])?\3?((19|20)\d{2}|\d{2})?$", sub)
            if result:
                # Not sure what's a month, day, or year - let isDate decide
                places = (
                    result.group(1),
                    result.group(4),
                    result.group(5))
                places = [int(x) if x is not None else None for x in places]
                (type, cost) = self.isDate(places[0], places[1], places[2])
                if not type:
                    continue
                print sub
                print places
                print type
#                print sub
#                print places
#                print "Found: {}, cost: {}".format(type, cost)
                self.addQueue(part, prefix, suffix, sub, type, cost=cost)

    def isRepeated(self, first, word):
        """Improve efficiency over collections.Counter()"""
        for char in word:
            if char != first:
                return False
        return True

    def charCost(self, word):
        """Return cost for repeated character"""
        if word[0] in string.digits:
            return 10 * len(word)
        elif word[0] in string.ascii_lowercase:
            return 26 * len(word)
        elif word[0] in string.ascii_uppercase:
            return 52 * len(word)
        return 94 * len(word)

    def findRepeated(self, part, minLength=3):
        """Finds repeated characters."""
        word = part.word
        for prefix, suffix, sub in self.subPermutations(word, minLength=minLength):
            mutations = []
            if self.isRepeated(sub[0], sub):
                cost = self.charCost(sub)
                self.addQueue(part, prefix, suffix, sub, 'repetition', cost=cost)
            elif self.isRepeated(sub[0].lower(), sub.lower()):
                replaced, word = self.removeCase(word)
                cost = self.charCost(sub)
                if replaced and len(replaced) == len(sub):
                    mutations.append(Mutation('upper', replaced))
                elif replaced:
                    mutations.append(Mutation('case', replaced))
                self.addQueue(part, prefix, suffix, sub, 'repetition',
                              mutations, cost=cost)

    def findKeyRun(self, part):
        """Finds consecutive runs on the keyboard through graphs - minimum of
        three is typical."""
        word = part.word
        for prefix, suffix, sub in self.subPermutations(word, minLength=3):
            if key_graph.isRun(sub):
                cost = len(sub)
                self.addQueue(part, prefix, suffix, sub, 'keyboard', [], cost)

    def findBruteForce(self, part):
        """Find brute force time after all other patterns are exhausted."""
        word = part.word
        if re.search(r"[^0-9a-zA-Z._!-@*#/$&]", word):
            charset = 94
        elif re.search(r"[^0-9a-zA-Z]", word):
            charset = 72
        elif re.search(r"^[A-Z]+$", word):
            charset = 26
        elif re.search(r"^[a-z]+$", word):
            charset = 26
        elif re.search(r"^[0-9]+$", word):
            charset = 10
        else:
            charset = 52
        self.addQueue(part, '', '', word, 'bruteforce', [], charset ** len(word))

if __name__ == "__main__":
#    pw = Password("hi2")
#    pw.findWord(pw.parts[1])
#    pw.findBruteForce(pw.parts[1])
#    pw.addParts()
#    for combination in pw.getCombinations():
#        print combination
    pw = Password("rootword")
#    for prefix, suffix, sub in pw.subPermutations(pw.root.next[0].word):
#        print sub