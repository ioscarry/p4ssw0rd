import cProfile

# New auto keygraph - thanks, Dan Wheeler (with modifications)
layoutQwerty = """\
`~ 1! 2@ 3# 4$ 5% 6^ 7& 8* 9( 0) -_ =+
xx qQ wW eE rR tT yY uU iI oO pP [{ ]} \|
xx aA sS dD fF gG hH jJ kK lL ;: '"
xx zZ xX cC vV bB nN mM ,< .> /?"""

class Keyboard(object):
    def __init__(self):
        self.keys = []

    def addKey(self, key):
        self.keys.append(key)

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
        if neighbor in (self.left, self.right, self.up, self.down):
            return True
        return False

def getOrNone(layout, y, x):
    if x < 0 or y < 0:
        return None
    try:
        return layout[y][x]
    except IndexError:
        return None

def main():
    layout = layoutQwerty.split("\n")
    layout = [['' if key == "xx" else key for key in row.split()] for row in layout]
    qwerty = Keyboard()
    for y in range(0, len(layout)):
        for x in range(0, len(layout[y])):
            qwerty.addKey(Key(
                (layout[y][x]),
                left=getOrNone(layout, y, x - 1),
                right=getOrNone(layout, y, x + 1),
                up=getOrNone(layout, y - 1, x),
                down=getOrNone(layout, y + 1, x)))

if __name__ == "__main__":
    cProfile.run('main()')