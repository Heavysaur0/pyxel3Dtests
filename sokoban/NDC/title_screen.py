import pyxel
from copy import deepcopy

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

# LEVELS_STRING = open("sokoban/test_test.txt", 'r').read()
LEVELS_STRING = """0

_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ # # # # # _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ # # # # # _ # _ _ _ # # # # # # # # _
_ # # # # _ _ _ _ _ # _ _ _ # # # @ o _ _ _ _ _ _ _ _ # _
_ # _ _ # # # # _ _ # _ # _ _ # # # _ # # # # _ o o o # _
# # o _ _ _ _ # _ _ # _ o _ _ _ _ _ _ _ # _ _ # _ o _ # _
# _ _ _ # o _ # _ # # # _ # # _ o _ o _ # _ o _ o o _ # _
# _ _ _ _ o o # # # _ o o _ # _ # # o # # _ _ _ o _ _ # _
# _ _ # _ _ _ _ _ _ _ o _ o # _ # _ _ # # # # # _ o _ # _
# # # # # # # _ # # # # _ _ _ _ # _ _ _ _ _ _ _ # _ _ # _
# # # # # _ # _ # _ _ _ _ # # # # _ # # # # # _ # # _ # #
# _ _ _ # # # _ # _ # # # # # # # _ # _ _ _ # _ o _ o _ #
# _ o _ _ _ _ o # _ o _ _ _ o _ o _ _ _ o _ # _ _ _ _ _ #
# # _ # # # # _ # _ o _ _ _ _ _ _ o _ # o # # _ # # # # #
_ # _ # # _ _ _ _ # # # o # # # # _ _ # _ # # _ # # # # _
_ # _ # # _ _ o _ _ # _ _ _ # _ _ # # # _ # # _ # _ _ # _
# # _ # # # # _ o _ # o _ o # _ _ _ _ # _ # # _ _ o _ # _
# _ _ # _ _ _ # o _ # _ o _ # _ _ o _ # _ # # # # _ _ # _
# _ o _ _ o _ # _ _ _ _ o _ # # o o _ # _ _ _ _ # o _ # _
# _ _ # # _ # # _ _ _ o _ _ # # _ _ _ o _ _ # _ _ _ _ # _
# # # # _ _ # # # # # # # # # # _ # # # _ _ # # # # # # _
_ _ _ # _ o _ _ _ _ _ _ _ _ _ _ o _ # # # # # _ _ _ _ _ _
_ _ _ # _ _ # # # # # # # # # _ _ _ # _ _ _ _ _ _ _ _ _ _
_ _ _ # # # # _ _ _ _ _ _ _ # # # # # _ _ _ _ _ _ _ _ _ _

_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ x _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ x _ _ _ _ _ _ _ _ _ x x _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ x _ x _ _ _ _ _ _ x x _ _ _
_ x _ x x _ x _ _ _ _ _ x _ _ _ _ _ _ _ _ _ _ _ _ x x _ _
_ _ _ _ _ _ _ x x _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ x x _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ x _ _ _ _ _ x _ _ _ _ _ _ x _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ x _ _ _ _ _ _ _ _ _ _ _ _ _ x _ x _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ x _ x _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ x _ _ _ x _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ x _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ x x x _ x x x _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ x x _ _ _ _ x _ _ _ _ _ _ _ x _ _ _
_ _ _ _ _ _ _ _ x _ _ _ x x _ _ x x _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ x x x x x _ _ _ _ _ _ _ _ _ _ _ x _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ x _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

0

# # # # # # # # #
# _ @ _ o _ _ _ #
# # # # # # # # #

_ _ _ _ _ _ _ _ _
_ _ _ _ _ _ x _ _
_ _ _ _ _ _ _ _ _

0

# # # # # # #
# # # _ # # #
# # # o # # #
# _ o @ o _ #
# # # o # # #
# # # _ # # #
# # # # # # #

_ _ _ _ _ _ _
_ _ _ x _ _ _
_ _ _ _ _ _ _
_ x _ _ _ x _
_ _ _ _ _ _ _
_ _ _ x _ _ _
_ _ _ _ _ _ _

0

# # # # # # # #
# # # # # _ _ #
# # _ _ _ _ _ #
# @ _ o o o _ #
# # _ _ _ _ _ #
# # # # # # _ #
# # # # # # # #

_ _ _ _ _ _ _ _
_ _ _ _ _ x x _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ x _
_ _ _ _ _ _ _ _

0

# # # # # # # # # #
# _ _ _ _ _ _ _ _ #
# _ _ _ _ _ _ _ _ #
# _ @ _ _ _ o _ _ #
# _ o _ _ _ _ _ _ #
# _ _ _ _ _ _ _ _ #
# _ _ _ _ _ _ _ _ #
# # # # # # # # # #

_ _ _ _ _ _ _ _ _ _
_ _ _ _ g _ _ _ _ _
_ _ _ _ g _ b _ x _
_ _ _ _ g _ _ _ _ _
_ _ _ _ g _ _ _ _ _
_ _ b _ g _ _ _ x _
_ _ _ _ g _ _ _ _ _
_ _ _ _ _ _ _ _ _ _

1

# # # # # # # # # # # #
# _ _ _ _ _ _ _ _ _ _ #
# _ @ p _ _ _ _ _ _ _ #
# _ _ _ _ _ _ _ _ _ _ #
# # # # # # # # # # # #

_ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ g _ _ _ _ _
_ _ _ b _ _ g _ _ x _ _
_ _ _ _ _ _ g _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _

1

# # # # # # # # # # # #
# _ _ o _ _ _ _ _ _ _ #
# _ @ _ s _ _ _ _ _ _ #
# _ _ _ _ _ _ _ _ _ _ #
# # # # # # # # # # # #

_ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ b _ g _ x _ _
_ _ _ _ _ _ _ g _ _ _ _
_ _ _ _ _ _ _ g _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _

0

_ _ # # # #
_ _ # _ _ #
_ _ # o _ #
# # # _ @ #
# _ _ o _ #
# _ # _ _ #
# _ _ o _ #
# # # _ _ #
_ _ # # # #

_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ x _
_ _ _ _ x _
_ _ _ _ x _
_ _ _ _ _ _
_ _ _ _ _ _

3

# # # # # # # #
# _ _ t _ _ _ #
# _ # # # # _ #
# @ _ p _ # _ #
# _ # # # # _ #
# _ _ t _ _ _ #
# # # # # # # #

_ _ _ _ _ _ _ _
_ _ _ _ _ _ x _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ x _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ x _
_ _ _ _ _ _ _ _

0

# # # # # # _ _
# _ _ _ _ # # #
# _ o _ o _ _ #
# _ _ # @ _ _ #
# # # # # # # #

_ _ _ _ _ _ _ _
_ x _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ x _ _ _ _ _
_ _ _ _ _ _ _ _

0

_ _ _ # # # # # _ _ _
# # # # _ _ _ # # # #
# _ _ # o _ _ _ _ _ #
# _ o o _ _ _ _ # _ #
# @ _ _ # o _ o # _ #
# # # _ # _ _ _ # _ #
_ # _ _ # # # # # _ #
_ # _ _ _ _ _ _ _ _ #
_ # # # # # # # # # #

_ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _
_ _ _ _ x x x x x _ _
_ _ _ _ _ _ _ _ _ _ _

0

_ _ _ _ _ _ _ # # # # _ _
_ # # # # # # # _ _ # _ _
_ # _ _ _ _ _ _ _ o # # _
_ # _ # # # # # _ _ _ # #
# # _ # _ _ _ # _ # _ _ #
# _ _ # _ o _ _ o _ # _ #
# _ # # # _ # @ _ _ # _ #
# _ # _ o _ # o # # # _ #
# _ # _ _ _ _ _ # _ _ _ #
# _ _ # _ # _ _ # _ # # #
# # _ o _ # # # # _ # _ _
_ # # _ _ _ _ _ _ _ # _ _
_ _ # _ _ # # # # # # _ _
_ _ # # # # _ _ _ _ _ _ _

_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ x _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ x x _ _ _ _ _
_ _ _ _ _ _ _ x x _ _ _ _
_ _ _ _ _ _ _ x _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _

0

_ _ # # # # _ _ _ _ _ _ _ _
# # # _ _ # # # # # # # # #
# _ _ _ _ _ _ _ _ _ _ _ _ #
# _ _ o _ o _ o _ o _ o _ #
# # _ # # # # # # # # _ # #
# _ _ _ _ _ _ _ _ _ _ _ # _
# _ o # # _ o _ o _ o o # _
# # _ # # # # # # # # _ # _
_ # _ _ _ _ _ @ _ _ _ _ # _
_ # # # # # # # # # # # # _

_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ x _ _ _ _ _ _ _ _ _ _ _
_ _ x x x x _ x _ x _ _ _ _
_ _ x _ _ _ _ _ _ _ _ x _ _
_ _ x _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _"""

LEVELS_SPLIT = LEVELS_STRING.split('\n\n')

LEVEL_COUNT = len(LEVELS_SPLIT) // 3

SCREEN_WIDTH, SCREEN_HEIGHT = 512, 512-16


class TitleScreen:
    def __init__(self):
        self.level = 0
        self.quit = False
        self.enter_level = False

    def update(self):
        self.enter_level = pyxel.btnp(pyxel.KEY_E)
        self.quit = pyxel.btnp(pyxel.KEY_Q)
        if pyxel.btnp(pyxel.KEY_UP):
            self.level = (self.level + 1) % len(LEVELS)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.level = (self.level - 1) % len(LEVELS)
        # if not LEVELS[max(0, self.level - 1)].won:
        #     self.level = 0

    def draw(self):
        pyxel.cls(0)
        pyxel.text(SCREEN_WIDTH / 2 - 20, SCREEN_HEIGHT / 2 - 60, "Sokoban", 7)
        pyxel.text(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 - 30, "Press ENTER to start", 11)
        pyxel.text(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 - 10, "Press Q to quit", 11)
        pyxel.text(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 + 10, f"Level : {self.level + 1}", 10)

class Game:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Sokoban", display_scale=2)
        self.state = "title_screen"
        self.level: Level
        self.title_screen = TitleScreen()
        pyxel.load("hallo.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.state == "title_screen":
            self.title_screen.update()
            if self.title_screen.quit:
                pyxel.quit()
            elif self.title_screen.enter_level:
                self.state = "level"
                self.level = LEVELS[self.title_screen.level]
                print(f"The user has entered level {self.title_screen.level}")
        elif self.state == "level":
            self.level.update()
            if self.level.quit:
                self.state = "title_screen"

    def draw(self):
        if self.state == "title_screen":
            self.title_screen.draw()
        elif self.state == "level":
            self.level.draw()


class Level:
    def __init__(self, tp_count, layouts) -> None:
        self.tp_count = tp_count
        self.initial_tp_count = tp_count

        block_level_layout, floor_level_layout = layouts
        self.player_x: int
        self.player_y: int
        self.width = len(block_level_layout[0])
        self.height = len(block_level_layout)
        self.x_offset = (SCREEN_WIDTH / 16 - self.width) * SCREEN_WIDTH / 32
        self.y_offset = (SCREEN_HEIGHT / 16 - 2 - self.height) * SCREEN_HEIGHT / 32

        self.block_layout = block_level_layout
        self.floor_layout = floor_level_layout

        self.player_facing = (0, -1)

        self.level: list[list[int]]
        self.floor_level: list[list[int]]
        self.last_block: tuple[int]
        self.targets = []
        self.moves = []
        self.button = False
        self.buttons = []
        self.gates = []
        self.reset_level()

        self.won = False
        self.quit = False

    def reset_level(self) -> None:
        self.tp_count = self.initial_tp_count
        self.last_block = (None, None)
        self.targets = []
        self.moves = []
        self.button = False
        self.buttons = []
        self.gates = []
        self.init_level()
        self.init_floor()

    def init_level(self) -> None:
        self.level = deepcopy(self.block_layout)
        for y, row in enumerate(self.level):
            for x, cell in enumerate(row):
                if cell == PLAYER:
                    self.level[y][x] = VOID  # Clear the initial player position
                    self.player_x = x
                    self.player_y = y
                elif cell == FIRST_BOX:
                    self.level[y][x] = TELEPORT_BOX
                    self.last_block = (x, y)

    def init_floor(self) -> None:
        self.floor_level = deepcopy(self.floor_layout)
        for y, row in enumerate(self.floor_level):
            for x, cell in enumerate(row):
                if cell == TARGET:
                    self.targets.append((x, y))  # Add the targets
                elif cell == BUTTON:
                    self.buttons.append((x, y))  # Add the targets
                elif cell == GATE:
                    self.gates.append((x, y))

    def has_won(self) -> bool:
        for x, y in self.targets:
            if self.level[y][x] not in (BOX, TELEPORT_BOX):
                return False
        else:
            return True

    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        if self.floor_level[y][x] == GATE:
            return self.button
        return self.level[y][x] == VOID

    def is_pushable(self, x, y, dx, dy):
        new_x, new_y = x + dx, y + dy
        return self.level[y][x] in (BOX, TELEPORT_BOX, STONE) and (not self.floor_level[y][x] == GATE or self.button) and self.is_walkable(new_x, new_y)

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if self.is_pushable(new_x, new_y, dx, dy):
            self.moves.append((self.player_x, self.player_y, new_x, new_y, new_x + dx, new_y + dy, self.last_block[0],
                               self.last_block[1]))
            temp = self.level[new_y][new_x]
            self.level[new_y][new_x] = VOID
            self.level[new_y + dy][new_x + dx] = temp
            self.player_x, self.player_y = new_x, new_y
            if self.level[new_y + dy][new_x + dx] == TELEPORT_BOX:
                self.last_block = (new_x + dx, new_y + dy)
        elif self.is_walkable(new_x, new_y):
            self.moves.append((self.player_x, self.player_y, new_x, new_y))
            self.player_x, self.player_y = new_x, new_y
        self.player_facing = (dx, dy)

    def teleport(self):
        if self.last_block != (None, None) and self.tp_count > 0:
            self.tp_count -= 1
            self.moves.append((self.player_x, self.player_y, *self.last_block, "hello"))
            x, y = self.last_block
            self.level[y][x] = VOID
            self.level[self.player_y][self.player_x] = TELEPORT_BOX
            temp = self.last_block
            self.last_block = (self.player_x, self.player_y)
            self.player_x, self.player_y = temp

    def undo(self):
        if self.moves:
            move = self.moves.pop()
            if len(move) == 5:
                move = move[:-1]
                self.last_block = (move[2], move[3])
                self.tp_count += 1
            if len(move) == 4:
                old_x, old_y, new_x, new_y = move
                self.level[new_y][new_x], self.level[old_y][old_x] = self.level[old_y][old_x], self.level[new_y][new_x]
                self.player_x, self.player_y = old_x, old_y
            elif len(move) == 8:
                self.player_x, self.player_y, old_x, old_y, old_bx, old_by, block_x, block_y = move
                self.level[old_y][old_x] = self.level[old_by][old_bx]
                self.level[old_by][old_bx] = VOID
                self.last_block = (block_x, block_y)

    def update(self):
        self.quit = pyxel.btnp(pyxel.KEY_Q)
        if pyxel.btnp(pyxel.KEY_R):
            self.reset_level()
        elif pyxel.btnp(pyxel.KEY_Z):
            self.undo()
        elif pyxel.btnp(pyxel.KEY_SPACE):
            self.teleport()

        if self.has_won():
            self.quit = True
            self.won = True
            self.reset_level()

        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP):
            dy -= 1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            dy += 1
        elif pyxel.btnp(pyxel.KEY_LEFT):
            dx -= 1
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            dx += 1

        if dx != 0 or dy != 0:
            self.move_player(dx, dy)

        for x, y in self.buttons:
            if self.level[y][x] in (BOX, TELEPORT_BOX, STONE) or (x, y) == (self.player_x, self.player_y):
                self.button = True
                break
        else:
            self.button = False

    def draw(self):
        pyxel.cls(0)

        pyxel.text(10, 14, "Sokoban", 7)
        pyxel.text(SCREEN_WIDTH / 2 - 70, 5, "Press R to restart and Z to undo", 11)
        pyxel.text(SCREEN_WIDTH / 2 - 70, 14, "Press Q to quit and SPACE to teleport", 11)
        pyxel.text(SCREEN_WIDTH / 2 - 70, 23, f"You have {self.tp_count} teleportation(s)", 10)
        
        for y in range(self.height):
            for x in range(self.width):
                pos = (self.x_offset + x * 16, self.y_offset + y * 16)
                pos_x, pos_y = pos
                block_cell = self.level[y][x]
                if (x, y) == self.last_block:
                    block_cell = FIRST_BOX
                floor_cell = self.floor_level[y][x]
                if floor_cell == GATE and not self.button:
                    block_cell = WALL
                pyxel.blt(pos_x, pos_y, 0, BLOCKS_TRANSLATOR[block_cell] * 16, FLOOR_TRANSLATOR[floor_cell] * 16, 16, 16, 14)
                # blt(x, y, img, u, v, w, h, [colkey])
        pyxel.blt(self.x_offset + self.player_x * 16, self.y_offset + self.player_y * 16, 1, (1 + self.player_facing[0]) * 16, (1 + self.player_facing[1]) * 16, 16, 16, 0)


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
        't': TELEPORT_BOX,
        's': STONE
    }
    return translator[char]


def interpret_level_string(big_strings):
    return (int(big_strings[0]),
            [[[char_to_int(char) for char in string.split(' ')] for string in big_string.splitlines()] for big_string in
             big_strings[1:]])


def get_from_text(index):
    return (LEVELS_SPLIT[3 * index], LEVELS_SPLIT[3 * index + 1], LEVELS_SPLIT[3 * index + 2])


def create_level(index):
    temp = get_from_text(index)
    tp_count, layouts = interpret_level_string(temp)
    return Level(tp_count, layouts)


LEVELS = [create_level(i) for i in range(LEVEL_COUNT)]

if __name__ == "__main__":
    Game()
