"""General-purpose binary search for in sorted files, with custom low and high
locations (for first-character indexed files)."""

import os
import cProfile

def searchFile(f, search, low=None, high=None, splitChar=None):
    """Does a binary search on a file object of unknown length. Returns a float
    of the position in the file if found, False if not."""
    f.seek(0, os.SEEK_END)
    size = f.tell()
    if not low:
        low = 0
    if not high:
        high = size - 1
    mid = (high + low) // 2
    # Workaround to stop the first word from being missed
    f.seek(low)
    found, line = f.readline().rstrip("\n\r").split(splitChar)
    i = 0
    while found != search:
        temp = found
        mid = (high + low) // 2
        f.seek(mid)
        f.readline()                    # Move to the next full line
        found = f.readline().rstrip("\n\r")
        if splitChar and "\t" in found:
            (found, line) = found.split(splitChar)
        if found == temp:
            break
        if found > search:
            high = mid
        else:
            low = mid
        i += 1
        if i > 250:
            raise Exception(
                "infinite loop during binary search for {}".format(search))

    if found == search:
        return int(line)
    return False

if __name__ == "__main__":
    f = open(os.path.join("words", "cities.dic"), "r")
    #result = searchFile(f, "illinols))ol-eo-lgoo")
    cProfile.run('searchFile(f, "aaron")')
    result = searchFile(f, "aaron")
    print result
    f.close()