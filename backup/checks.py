import string, re, collections
import word_list

def removeMutations(pw):
    """Check for the most common letter / number / symbol replacements"""


def dictionaryCombinations(pw, minLength):
    """Check if the password is made up of a number of dictionary words."""
    pw = pw.lower()
    for i in range(minLength, len(pw)):
        if pw[:i] in word_list.words:
            for j in range(i, len(pw)):
                if pw[j:] in word_list.words:
                    return {
                        "vector":           "Combination dictionary",
                        "error":            "dictionary words"
                    }
            return {
                "vector":           "Dictionary",
                "pattern":          "Dictionary word",
                "points":           -5
            }
    return False

def repetition(pw, targetAdjacent, targetTotalRepeat):
    """Checks if two characters are consecutively repeated, or the
    same character is used targetRepeat times."""
    last = ""
    streak = 0
    for char in pw:
        if char == last:
            streak += 1
        else:
            streak = 0
            last = char
        if streak >= targetAdjacent:
            return {
                "vector":           1,
                "error":            "Password contains more than {} consecutive \
repeated characters.".format(targetAdjacent)
            }
    if sorted(collections.Counter(pw).values())[-1] >= targetTotalRepeat:
        return {
            "vector":           1,
            "error":            "Password contains a character which repeats \
more than {} times.".format(targetTotalRepeat)
        }

    return False

def consecutive(pw, targetKeyConsec, targetAlphaConsec):
    """Check if letters are adjacent in the alphabet or keyboard.
    Arguments:
    targetKeyConsec: Check for >= number of consecutive keys on QWERTY keyboard.
    targetKeyConsec: Check for >= number of consecutive letters in alphabet.
    Return failure object if found, False if not."""
    # TODO: Check length for each consecutive character


    # Check for more than two consecutive characters in alphabet ("abcdef")
    pw = pw.lower()
    for i in range(targetAlphaConsec, len(pw)):
        sub = pw[i-targetAlphaConsec:i]
        if sub in string.ascii_lowercase or sub in string.digits:
            return {
                "vector":           2,
                "error":            "Password contains {}+ consecutive \
alphabet characters.".format(targetAlphaConsec)}
    return False

def partialDictionary(pw, targetLength):
    """Check for the largest number of consecutive characters which can be found
    in the dictionary, and pass/fail based on password length."""
    pw = pw.lower()
    for i in range(targetLength, len(pw)):
        sub = pw[i-targetLength:i]
        if sub in word_list.words:
            return {
                "vector":           2,
                "error":            "Substring {} found in dictionary.".format(
                    sub)}
    return False

# Checks

def checkLengthMinimum(pw):
    """Check if the password is far too short."""
    if len(pw) <= 4:
        return {
            "vector":       2,
            "error":        "Password is extremely short."}
    return False

def checkDigits(pw):
    """Check if password contains only digits."""
    for char in pw:
        if char not in string.digits:
            return False
    return {
        "vector":           2,
        "error":            "Password contains only digits."
    }

def checkLowercase(pw):
    """Check if password contains only lowercase letters."""
    for char in pw:
        if char not in string.ascii_lowercase:
            return False

    return {
        "vector":           2,
        "error":            "Password contains only lowercase letters."
    }

def checkMajorRepetition(pw):
    """Checks for repetition in adjacent and total characters."""
    return repetition(pw, 3, 4)

def checkMajorConsecutive(pw):
    """Checks for 4+ repeating characters."""
    return consecutive(pw, 4, 4)

def checkDictionary(pw):
    """Check if the password is in the dictionary with no mutations."""
    pw = pw.lower()
    if pw not in word_list.words:
        return False

    return {
        "vector":           1,
        "error":            "Password is a dictionary word."
    }

def checkDictionaryCombinations(pw):
    """Check if the password is made up of multiple dictionary words."""
    return dictionaryCombinations(pw, 4)

def checkLetterNumberOrder(pw):
    """Check if numbers exist at beginning or end."""
    if re.search(r"^(\d+[a-zA-Z]+|[a-zA-Z]+\d+)$", pw.lower()):
        return {
            "vector":           1,
            "error":            "Found letters with numbers attached to beginning or end."
        }
    return False

def checkPartialDictionary(pw):
    """Check for partial dictionary matches."""
    return partialDictionary(pw, 4, 1, 1)

def checkMutationCapital(pw):
    """Check if the only capital letter exists at the beginning of the password"""
    if re.match(r"[A-Z][^A-Z]+$", pw):
        return {
            "vector":           2,
            "error":            "Only first character is capitalized."
        }
    return False

def checkMutationSymbolLocation(pw):
    """Check if symbols are tacked on to the end."""
    if re.match(r"(\w+\W$|\W\w+)", pw):
        return {
            "vector":           2,
            "error":            "Symbol exist before or after password."
        }
    return False

def checkMutationSymbolType(pw):
    """Check for the most common symbol types"""

def checkKeyboardShift(pw):
    """Check for poor passwords shifted up, left, down, or right on keyboard"""
    # TODO: Low priority, but can catch a less-used but known mutation.
    return False

def checkDelimiter(pw):
    """Check for delimiter patterns between letters"""
