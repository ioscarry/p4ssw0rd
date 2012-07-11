import cProfile

layouts = []

# New auto keygraph - thanks, Dan Wheeler (with modifications)
layoutQwerty = """\
`~ 1! 2@ 3# 4$ 5% 6^ 7& 8* 9( 0) -_ =+
xx qQ wW eE rR tT yY uU iI oO pP [{ ]} \|
xx aA sS dD fF gG hH jJ kK lL ;: '"
xx zZ xX cC vV bB nN mM ,< .> /?"""

class Keyboard(object):
    def __init__(self):
        self.keys = {}

    def addKey(self, key):
        self.keys[key.key[0]] = key
        self.keys[key.key[1]] = key

class Key(object):
    def __init__(self, key, left, right, up, down):
        self.key = key
        self.left = left
        self.right = right
        self.up = up
        self.down = down

    def __repr__(self):
        return "Key: {}, left:{} right:{} up:{} down:{}".format(
            self.key, self.left, self.right, self.up, self.down)

    def hasNeighbor(self, neighbor):
        if neighbor in self.left or neighbor in self.right\
            or neighbor in self.up or neighbor in self.down:
            return True
        return False

def getOrEmpty(layout, y, x):
    if x < 0 or y < 0:
        return []
    try:
        return list(layout[y][x])
    except IndexError:
        return []

def isRun(word, minLength=3):
    breaks = 0
    run = 0
    cost = 0
    # TODO: number of turns
    turns = 0
    if not layouts:
        createLayouts()
    for layout in layouts:
        for char, next in zip(word, word[1:]):
            run += 1
            if char == " " or not layout.keys[char].hasNeighbor(next):
                if run < minLength:
                    return False
                breaks += 1
                run = 0
    if run < minLength:
        return False
    # Cost of all horizontal runs >2 with no turns: 264
    # Cost of all vertical runs >2 with no turns: 30
    # Cost of all runs with one break: 264^2 = 69696
    # Cost of all runs with two breaks: 264^3 = 18399744
    if breaks > 3:
        return False
    cost += 264**(breaks + 1)
    return cost


def createLayouts():
    layout = layoutQwerty.split("\n")
    layout = [['' if key == "xx" else key for key in row.split()] for row in layout]
    qwerty = Keyboard()
    for y in range(0, len(layout)):
        for x in range(0, len(layout[y])):
            if not layout[y][x]:
                continue
            qwerty.addKey(Key(
                (list(layout[y][x])),
                left=getOrEmpty(layout, y, x - 1),
                right=getOrEmpty(layout, y, x + 1),
                up=getOrEmpty(layout, y - 1, x),
                down=getOrEmpty(layout, y + 1, x)))
    layouts.append(qwerty)

if __name__ == "__main__":
    print isRun("qwerty")
    #cProfile.run('isRun("qwert")')