import os
import cProfile

def searchFile(f, term):
    """Does a binary search on a file object of unknown length. Returns a float
    of the position in the file if found, False if not."""
    # TODO: Find a way to cache locations of first 1-2 characters at the least
    # TODO: Fix bug - first entry in file returns False
    f.seek(0, os.SEEK_END)
    size = f.tell()
    low, high = 0, size - 1
    mid = (high + low) // 2
    found = None
    i = 0
    while found != term:
        temp = found
        mid = (high + low) // 2
        f.seek(mid)
        f.readline()                    # Move to the next full line
        found = f.readline().rstrip("\n").rstrip("\r")
        if found == temp:
            break
        if found > term:
            #print "found: {} high: {} low: {}".format(found, high, low)
            high = mid
        else:
            #print "found: {} high: {} low: {}".format(found, high, low)
            low = mid
        i += 1
        if i > 250:
            raise Exception("infinite loop during binary search for {}".format(term))

    if found == term:
        return (mid * 1.0) / size
    else:
        return False

if __name__ == "__main__":
    f = open(os.path.join("words", "cities.dic"), "r")
    #result = searchFile(f, "illinols))ol-eo-lgoo")
    cProfile.run('searchFile(f, "aaron")')
    result = searchFile(f, "aaron")
    print result
    f.close()