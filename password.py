#!/usr/local/bin/python2.7
import copy, re, string
import word_list, key_graph

class Part(object):
    def __init__(self, word, type=None, mutations=None, cost=1, pattern=None):
        if mutations is None: mutations = []
        if not isinstance(mutations, list):
            mutations = [mutations]
        self.word = word
        self.type = type
        self.mutations = mutations
        self.pattern = pattern
        self.cost = cost

    def __repr__(self):
        return "word: {}, type: {}, mutations: {}".format(
            self.word, self.type, self.mutations, self.pattern
        )

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
        "charDupe": 49,
        }

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
    regexContainsLetters = re.compile(r"[a-zA-Z]")
    regexMirror = re.compile(r"([(\[{{<])(\1{0,10}).+")
    regexBorder = re.compile(r"(^[^a-zA-Z0-9]{1,10}).+\1")
    regexDate = re.compile(r"(\d{1,4})([-/_. ])?(\d{1,4})?\2?(\d{1,4})?$")

    def __init__(self, password):
        # TODO: Save type of each character (lower, number, symbol) to avoid so many regex calls later
        self.password = password
        self.parts = [Part(password)]

    def subPermutations(self, word, maxLength=20, minLength=4):
        """Generates all possible substrings, from longest to shortest."""
        length = len(word)
        endRange = length - minLength + 2
        for i in range(0, endRange):
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

    def searchDictionary(self, word):
        """Ask word_list to find the word, and return the number of records
        searched, or False if not found."""
        return word_list.findWord(word)

    def findWord(self, part = 0):
        """Removes and saves mutations, then attempts to find the largest
        dictionary word (larger than two characters) within the given part
        index."""

        # TODO: Performance: find a way to reduce the number of searches
        word = self.parts[part].word
        for prefix, suffix, sub in self.subPermutations(word, minLength=3):
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
                cost = self.searchDictionary(subUnLeet)
                if cost:
                    if replaced:
                        mutations.append(Mutation('leet', replaced))
                        # Replace part, indicate that it is a word
                    return self.addParts(
                        part, Part(prefix), Part(suffix),
                        Part(subUnLeet, "word", mutations, cost))
                elif replaced:
                    # Need to also check un-leeted word against special-
                    # character wordlists
                    cost = self.searchDictionary(sub)
                    if cost:
                        return self.addParts(
                            part, Part(prefix), Part(suffix),
                            Part(sub, "word", mutations, cost))

        return False

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

    def addParts(self, part, prefix, suffix, sub):
        if sub and sub.word:
            self.parts[part] = sub
        else:
            del(self.parts[part])
        if suffix and suffix.word:
            self.parts.insert(part + 1, suffix)
        if prefix and prefix.word:
            self.parts.insert(part, prefix)
        return True

    def findDate(self, part = 0):
        """Search for a date in any possible format.
        Performs a general regex for date formats, then validates digits."""
        word = self.parts[part].word
        for prefix, suffix, sub in self.subPermutations(word, minLength=4):
            if re.search(Password.regexContainsLetters, sub):
                continue

            result = re.match(self.regexDate, sub)
            if result:
                # Not sure what's a month, day, or year - let isDate decide
                places = (
                    result.group(1),
                    result.group(3),
                    result.group(4))
                places = [int(x) if x is not None else None for x in places]
                (type, cost) = self.isDate(places[0], places[1], places[2])
                if not type:
                    return False
                return self.addParts(
                    part, Part(prefix), Part(suffix),
                    Part(sub, type, cost=cost))
        return False

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

    def findRepeated(self, part):
        """Finds repeated characters."""
        word = self.parts[part].word
        for prefix, suffix, sub in self.subPermutations(word, minLength=2):
            mutations = []
            if self.isRepeated(sub[0], sub):
                cost = self.charCost(sub)
                return self.addParts(
                    part, Part(prefix), Part(suffix), Part(sub, 'repetition', cost=cost))
            elif self.isRepeated(sub[0].lower(), sub.lower()):
                replaced, word = self.removeCase(word)
                cost = self.charCost(sub)
                if replaced and len(replaced) == len(sub):
                    mutations.append(Mutation('upper', replaced))
                elif replaced:
                    mutations.append(Mutation('case', replaced))
                return self.addParts(
                    part, Part(prefix), Part(suffix),
                    Part(sub, 'repetition', mutations, cost=cost))
        return False

    def findKeyRun(self, part):
        """Finds consecutive runs on the keyboard through graphs - minimum of
        three is typical."""
        word = self.parts[part].word
        for prefix, suffix, sub in self.subPermutations(word, minLength=3):
            if key_graph.isRun(sub):
                cost = len(part)
                return self.addParts(part, Part(prefix), Part(suffix),
                                     Part(sub, 'keyboard', cost))
        return False

    def findBorder(self, part):
        """Attempts to find common identical or mirrored borders, either with
        or without additional suffixes."""
        matches = {
            "(":")",
            "[":"]",
            "{":"}",
            "<":">"}
        word = self.parts[part].word
        # First look for borders with no suffix
        # ex. $$money$$
        result = re.search(self.regexBorder, word)
        if result:
            parts = re.split(r'({})'.format(re.escape(result.group(1))), word, 2)
        else:
            # Yow.
            result = re.search(self.regexMirror, word)
            if result:
                # Get the matching character, multiply by length of match
                right = matches[result.group(1)]
                left = result.group(1) + result.group(2)
                right *= len(left)
                parts = re.split(
                    r'({}|{})'.format(re.escape(left), re.escape(right)), word, 2)
            else:
                return False
        if result:
            return self.addParts(
                part, Part(parts[0] + parts[1]),
                Part(parts[3] + parts[4]), Part(parts[2]))
        return False

        # Next, look for a border with suffix
        # ex. $$money$$2008

    def findBruteForce(self, part):
        """Find brute force time after all other patterns are exhausted."""
        word = self.parts[part].word
        if re.search("[^0-9a-zA-Z._!-@*#/$&]", word):
            charset = 94
        elif re.search("[^0-9a-zA-Z]", word):
            charset = 72
        elif re.search("^[A-Z]+$", word):
            charset = 26
        elif re.search("^[a-z]+$", word):
            charset = 26
        elif re.search("^[0-9]+$", word):
            charset = 10
        else:
            charset = 52
        return self.addParts(
            part, None, None, Part(word, 'bruteforce', [], charset ** len(word)))