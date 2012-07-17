#!/usr/local/bin/python2.7
import copy, re, string, sqlite3, os
import key_graph, costs
from collections import deque

class DBWords(object):
    """Database object for word lists"""
    def __init__(self):
        self.c = None

    def connect(self):
        conn = sqlite3.connect(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "wordlist.db"))
        self.c = conn.cursor()

    def query(self, value):
        if not self.c:
            self.connect()
        result = self.c.execute(
            'SELECT location FROM words WHERE word=? LIMIT 1', (value,))
        result = result.fetchone()
        if result:
            return result[0]

class Part(object):
    """Node for a password graph, used for storing individual parts and
    their linkages"""
    def __init__(self, word, type=None, mutations=None, cost=1, pattern=None,
                 prev=None, next=None):
        if mutations is None: mutations = []
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
        return "Part: {} ({})".format(self.word, self.type)

    def _getFinalCost(self):
        """Returns the cost, including mutations"""
        multi = 1
        for mutation in self.mutations:
            multi *= mutation.cost
        return self.cost * multi

    def _getMutationCost(self):
        """Returns just the multiplier for mutations"""
        multi = 1
        for mutation in self.mutations:
            multi *= mutation.cost
        return multi

    finalCost = property(_getFinalCost)
    mutationCost = property(_getMutationCost)

class Mutation(object):
    def __init__(self, type, index):
        self.type = type
        self.index = index

    def __repr__(self):
        return "{}: {}".format(self.type, self.index)

    def _getCost(self):
        if self.type in costs.mutations:
            return costs.mutations[self.type]

    cost = property(_getCost)

class Password(object):
    """Main object which stores all parts search methods."""
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
    MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
              "oct", "nov", "dec", "january", "february", "march", "april",
              "june", "july", "august", "september", "october", "november",
              "december"]

    def __init__(self, password):
        root = Part('', type="root", cost=1)
        password = Part(word=password, prev=deque((root,)))
        root.next = deque((password,))
        self.root = root
        self.queue = []
        self.queueMemo = {}
        self.db = DBWords()

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

    def findEmail(self, part):
        """Searches for email addresses (can be weak or strong, but typically
        very weak)."""
        word = part.word
        for prefix, suffix, sub in self.subPermutations(word):
            if re.match(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$", sub):
                self.addQueue(part, prefix, suffix, sub, "email", [])

    def removeDelimiter(self, word, minNum=4):
        """Search for a delimiter between each character.
        Returns a tuple: (word, mutation object)."""
        count = 1
        replaced = []
        symbols = "`~!@#$%^&*()-_=+[{]};:\\'\",<.>/? "
        if word[0] in symbols:
            start = 0
        elif word[1] in symbols:
            start = 1
        else:
            return word, replaced
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
            return ''.join(word), Mutation('delimiter', replaced)
        return word, None


    def removeLeet(self, word):
        """Removes common letter and number/symbol substitutions.
        Can function as a generator, in case there is more than one
        possible result (functionality is currently disabled for performance,
        but will be needed with the pervasive i,l=1,1 and i,l=!,! replacements).

        Returns a tuple: (word, mutation object)."""

        result = [[]]
        replaced = []
        for index, char in enumerate(list(word)):
            # Special exception for l and i substitutions
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

        if not replaced:
            mutation = None
        elif len(replaced) == 1:
            mutation = Mutation('leetOne', replaced)
        else:
            mutation = Mutation('leetMulti', replaced)
        for temp in result:
            yield ''.join(temp), mutation

    def removeCase(self, word):
        """Searches for uppercase letters.
        Returns a tuple: (word, mutation object)."""
        replaced = [index for index, char in enumerate(word) if char.isupper()]
        length = len(replaced)

        if not length:
            return word, False
        if length == len(word):
            mutation = Mutation('caseUpper', replaced)
        elif replaced == [0]:
            mutation = Mutation('caseFirst', replaced)
        elif length == 1:
            mutation = Mutation('caseOne', replaced)
        else:
            mutation = Mutation('caseMulti', replaced)
        return word.lower(), mutation

    def searchDictionary(self, word):
        # Open files if necessary
        location = self.db.query(word)
        if location:
            return location
        return False


    def findWord(self, part, minLength=4, start=0, returnFirst=False):
        """Removes and saves mutations, then attempts to find the largest
        dictionary word (larger than minLength characters) within the given part
        index."""
        word = part.word
        for prefix, suffix, sub in self.subPermutations(
            word, minLength=minLength,
            start=start):
            mutations = []
            sub, mutation = self.removeDelimiter(sub)
            if mutation:
                mutations.append(mutation)

            sub, mutation = self.removeCase(sub)
            if mutation:
                mutations.append(mutation)

            # TODO: Bug: Mutations may stack on top of each other once
            # multiple leet possibilities are in
            for subUnLeet, mutation in self.removeLeet(sub):
                cost = self.searchDictionary(subUnLeet)
                if cost:
                    if mutation:
                        mutations.append(mutation)
                        # Replace part, indicate that it is a word
                    self.addQueue(
                        part, prefix, suffix, subUnLeet, "word", mutations, cost)
                    if returnFirst:
                        return
                elif mutation:
                    # Need to also check un-leeted word against special-
                    # character wordlists
                    cost = self.searchDictionary(sub)
                    if cost:
                        self.addQueue(
                            part, prefix, suffix, sub, "word", mutations, cost)
                        if returnFirst:
                            return

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
        """Takes the current queue, and adds parts into the password graph."""
        for (part, prefix, suffix, sub) in self.queue:
            if prefix.word:
                prefix.prev = part.prev
                prefix.next.append(sub)
                sub.prev.append(prefix)
                for node in part.prev:
                    node.next.append(prefix)
            else:
                sub.prev = part.prev
                for node in part.prev:
                    node.next.append(sub)
            if suffix.word:
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
            for node in part.next:
                if part in node.prev:
                    node.prev.remove(part)
            for node in part.prev:
                if part in node.next:
                    node.next.remove(part)
        self.queue = []

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
            if ((1 <= place1 <= 12 or place1 in self.MONTHS) and 1 <= place2 <= 31) or (
                (1 <= place2 <= 12 or place2 in self.MONTHS) and 1 <= place1 <= 31):
                return 'date', 21456 # 372+75 * 48
            elif ((1 <= place1 <= 12 or place1 in self.MONTHS) and self.isYear(place2)) or (
                (1 <= place2 <= 12 or place2 in self.MONTHS) and self.isYear(place1)):
                return 'date', 64656 # 900+372+75
        else:
            # YMD
            if self.isYear(place1):
                if ((1 <= place2 <= 12 or place2 in self.MONTHS) and 1 <= place3 <= 31) or (
                    (1 <= place3 <= 12 or place3 in self.MONTHS) and 1 <= place2 <= 31):
                    return 'date', 7948656 # 164250+900+372+75 * 48
            if self.isYear(place3):
                if ((1 <= place1 <= 12 or place1 in self.MONTHS) and 1 <= place2 <= 31) or (
                    (1 <= place2 <= 12 or place2 in self.MONTHS) and 1 <= place1 <= 31):
                    return 'date', 7948656 # 164250+900+372+75 * 48
        return False, False

    def findDate(self, part, returnFirst=False):
        """Search for a date in any possible format.
        Performs a general regex for date formats, then validates digits."""

        word = part.word
        for prefix, suffix, sub in self.subPermutations(word, minLength=4):
            result = re.match(r"((19|20)\d{2}|\d{2}|[jfmasondJFMASOND][a-zA-Z]+)([-/_. ])?([0-3]?[0-9]|[jfmasondJFMASOND][a-zA-Z]+)?\3?((19|20)\d{2}|\d{2})?$", sub)
            if result:
                # Not sure what's a month, day, or year - let isDate decide
                places = (result.group(1), result.group(4), result.group(5))
                ymd = []
                for place in places:
                    if not place: ymd.append(None)
                    elif place.isdigit(): ymd.append(int(place))
                    else: ymd.append(place.lower())
                (type, cost) = self.isDate(ymd[0], ymd[1], ymd[2])
                if not type:
                    continue
                self.addQueue(
                    part        = part,
                    prefix      = prefix,
                    suffix      = suffix,
                    sub         = sub,
                    type        = type,
                    cost        = cost)
                if returnFirst:
                    return

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

    def findRepeated(self, part, minLength=3, upper=None):
        """Finds repeated characters."""
        word = part.word
        run = 1
        start = 0
        end = len(word) - 1
        for index, char in enumerate(word):
            if index == end or char != word[index + 1]:
                if run >= minLength:
                    self.addQueue(
                        part        = part,
                        prefix      = word[:start],
                        suffix      = word[index+1:],
                        sub         = word[start:index+1],
                        type        = 'repetition',
                        cost        = self.charCost(word))
                start = index + 1
                run = 1
                continue
            else:
                run += 1

    def findKeyRun(self, part, minLength=4):
        """Finds consecutive runs on the keyboard through graphs - minimum of
        three is typical."""
        word = part.word

        for prefix, suffix, sub in self.subPermutations(word, minLength=minLength):
            cost = key_graph.isRun(sub)
            if cost:
                self.addQueue(
                    part        = part,
                    prefix      = prefix,
                    suffix      = suffix,
                    sub         = sub,
                    type        = 'keyboard',
                    mutations   = [],
                    cost        = cost)
                # Bail out early if the entire word is a run
                if len(sub) == len(word):
                    return

    def findBruteForce(self, part):
        """Find brute force time after all other patterns are exhausted."""
        word = part.word
        if re.search(r"[^0-9a-zA-Z._!-@*#/$&]", word):
            charset = 94
            type = 'bruteforce'
        elif re.search(r"[^0-9a-zA-Z]", word):
            charset = 72
            type = 'bruteforce'
        elif re.search(r"^[A-Z]+$", word):
            charset = 26
            type = 'bruteforce'
        elif re.search(r"^[a-z]+$", word):
            charset = 26
            type = 'bruteforce-lowercase'
        elif re.search(r"^[0-9]+$", word):
            charset = 10
            type = 'bruteforce-digits'
        else:
            charset = 52
            type = 'bruteforce'
        self.addQueue(
            part        = part,
            prefix      = '',
            suffix      = '',
            sub         = word,
            type        = type,
            cost        = charset ** len(word))

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
    pw = Password("twolllllthree")
    pw.findRepeated(pw.root.next[0])