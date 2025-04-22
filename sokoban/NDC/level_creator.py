import pyxel
from copy import deepcopy

CURSOR = -4
TELEPORT_BOX = -3
FIRST_BOX = -2
PLAYER = -1
VOID = 0
WALL = 1
BOX = 2
TARGET = 3
STONE = 4
BUTTON = 10
GATE = 11

BLOCKS_TRANSLATOR = {
    VOID: 0,
    BOX: 1,
    TELEPORT_BOX: 2,
    FIRST_BOX: 3,
    STONE: 4,
    WALL: 5
}
FLOOR_TRANSLATOR = {
    VOID: 0,
    TARGET: 2,
    BUTTON: 1,
    GATE: 3
}
SPRITE_TRANSLATOR = {
    VOID: (0, 0),
    BOX: (1, 0),
    TELEPORT_BOX: (2, 0),
    FIRST_BOX: (3, 0),
    STONE: (4, 0),
    WALL: (5, 0),
    TARGET: (0, 2),
    BUTTON: (0, 1),
    GATE: (0, 3)
}


class LevelCreator:
    def __init__(self) -> None:
        pyxel.init(256, 256, title="Sokoban")
        pyxel.load("hallo.pyxres")

        self.cursor_x = 0
        self.cursor_y = 0
        self.width = 16
        self.height = 14
        self.tp_count = 0

        self.layouts = [[[VOID for _ in range(self.width)] for _ in range(self.height)],
                        [[VOID for _ in range(self.width)] for _ in range(self.height)]]
        self.sprite_range = ((VOID, BOX, TELEPORT_BOX, FIRST_BOX, STONE, WALL, PLAYER),
                             (VOID, BUTTON, TARGET, GATE))
        self.range_index = 0
        self.index = 0
        
        self.actions = []
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.cursor_x = 0
        self.cursor_y = 0
        self.width = 16
        self.height = 14
        self.tp_count = 0

        self.layouts = [[[VOID for _ in range(self.width)] for _ in range(self.height)],
                        [[VOID for _ in range(self.width)] for _ in range(self.height)]]
        self.sprite_range = ((VOID, BOX, TELEPORT_BOX, FIRST_BOX, STONE, WALL, PLAYER),
                             (VOID, BUTTON, TARGET, GATE))
        self.range_index = 0
        self.index = 0
        
        self.actions = []
    
    def place_sprite(self):
        sprite = self.sprite_range[self.range_index][self.index]
        original_sprite = self.layouts[self.range_index][self.cursor_y][self.cursor_x]
        self.layouts[self.range_index][self.cursor_y][self.cursor_x] = sprite
        self.actions.append((self.cursor_x, self.cursor_y, self.range_index, original_sprite))

    def undo(self):
        action = self.actions.pop()
        x, y, range_index, sprite = action
        self.layouts[range_index][y][x] = sprite
    
    def save_level(self):
        result = f"{self.tp_count}\n\n"
        block_layout = self.layouts[0]
        floor_layout = self.layouts[1]
        height0, height1 = self.height, 0
        width0, width1 = self.width, 0
        for y in range(self.height):
            for x in range(self.width):
                if floor_layout[y][x] != VOID or block_layout[y][x] != VOID:
                    height0 = min(height0, y)
                    height1 = max(height1, y)
                    width0 = min(width0, x)
                    width1 = max(width1, x)
        block_layout = [row[width0:width1 + 1] for row in block_layout[height0:height1 + 1]]
        floor_layout = [row[width0:width1 + 1] for row in floor_layout[height0:height1 + 1]]
        result += '\n'.join([' '.join(map(int_to_char, ele)) for ele in block_layout]) + '\n\n'
        result += '\n'.join([' '.join(map(int_to_char, ele)) for ele in floor_layout]) + '\n\n'
        print(result)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_S):
            self.save_level()
        elif pyxel.btnp(pyxel.KEY_T):
            self.tp_count += 1
            self.tp_count %= 11 
        elif pyxel.btnp(pyxel.KEY_C):
            self.index += 1
            self.index %= len(self.sprite_range[self.range_index])
        elif pyxel.btnp(pyxel.KEY_X):
            self.index -= 1
            self.index %= len(self.sprite_range[self.range_index])
        elif pyxel.btnp(pyxel.KEY_F):
            self.range_index += 1
            self.range_index %= 2
            self.index %= len(self.sprite_range[self.range_index])
        elif pyxel.btnp(pyxel.KEY_SPACE):
            self.place_sprite()
        elif pyxel.btnp(pyxel.KEY_Z):
            self.undo()
        elif pyxel.btnp(pyxel.KEY_R):
            self.reset()

        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP):
            dy -= 1
        if pyxel.btnp(pyxel.KEY_DOWN):
            dy += 1
        if pyxel.btnp(pyxel.KEY_LEFT):
            dx -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT):
            dx += 1

        if dx != 0 or dy != 0:
            self.cursor_x += dx
            self.cursor_x %= self.width
            self.cursor_y += dy
            self.cursor_y %= self.height

    def display_sprite(self, sprite_int, x, y):
        if sprite_int == CURSOR:
            pyxel.blt(int(x * 16), int(y * 16), 1, 16, 16, 16, 16, 0)
        elif sprite_int == PLAYER:
            pyxel.blt(int(x * 16), int(y * 16), 1, 16, 32, 16, 16, 0)
        else:
            pos_x, pos_y = SPRITE_TRANSLATOR[sprite_int]
            pyxel.blt(int(x * 16), int(y * 16), 0, pos_x * 16, pos_y * 16, 16, 16, 14)
    
    def draw(self):
        pyxel.cls(0)
        

        pyxel.text(5, 11, "Sokoban Maker", 7)
        pyxel.text(10, 23, "S to save", 7)
        pyxel.text(60, 5, "Z to undo, F to change floors,", 11)
        pyxel.text(60, 14, "E to place and X/C to switch", 11)
        pyxel.text(60, 23, f"TP count: {self.tp_count} (T to change)", 10)
        length = len(self.sprite_range[self.range_index])
        sprites = [self.sprite_range[self.range_index][(self.index + i - 1)% length] for i in range(3)]
        for i, sprite in enumerate(sprites):
            self.display_sprite(sprite, 12.5 + i, 0.5)
        self.display_sprite(CURSOR, 13.5, 0.5)
        
        
        for y in range(self.height):
            for x in range(self.width):
                pos = (x * 16, (2 + y) * 16)
                pos_x, pos_y = pos
                block_cell = self.layouts[0][y][x]
                floor_cell = self.layouts[1][y][x]
                if block_cell == PLAYER:
                    pyxel.blt(pos_x, pos_y, 0, 0, FLOOR_TRANSLATOR[floor_cell] * 16, 16, 16, 14)
                    pyxel.blt(pos_x, pos_y, 1, 16, 32, 16, 16, 0)
                else:
                    if floor_cell == GATE:
                        block_cell = WALL
                    pyxel.blt(pos_x, pos_y, 0, BLOCKS_TRANSLATOR[block_cell] * 16, FLOOR_TRANSLATOR[floor_cell] * 16, 16, 16, 14)
                    # blt(x, y, img, u, v, w, h, [colkey])
                if (x, y) == (self.cursor_x, self.cursor_y):
                    pyxel.blt(pos_x, pos_y, 1, 16, 16, 16, 16, 0)


def char_to_int(char):
    translator = {
        '@': PLAYER,
        '_': VOID,
        '#': WALL,
        'o': BOX,
        'x': TARGET,
        'b': BUTTON,
        'g': GATE,
        'p': FIRST_BOX,
        't': TELEPORT_BOX
    }
    return translator[char]

def int_to_char(integer):
    translator = {
        PLAYER: '@',
        VOID: '_',
        WALL: '#',
        BOX: 'o',
        TARGET: 'x',
        BUTTON: 'b',
        GATE: 'g',
        FIRST_BOX: 'p',
        TELEPORT_BOX: 't'
    }
    return translator[integer]

if __name__ == "__main__":
    LevelCreator()