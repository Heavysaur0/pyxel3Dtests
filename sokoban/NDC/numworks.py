from copy import deepcopy
import kandinsky as kd
import ion

TELEPORT_BOX = -3
PLAYER = -1
VOID = 0
WALL = 1
BOX = 2
TARGET = 3


BLOCKS_TRANSLATOR = {
    VOID: 0,
    BOX: 1,
    WALL: 3
}
FLOOR_TRANSLATOR = {
    VOID: 0,
    TARGET: 1
}

# LEVELS_STRING = open("sokoban/test_test.txt", 'r').read()
LEVELS_STRING = """"""

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
        self.state = "title_screen"
        self.level: Level
        self.title_screen = TitleScreen()

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
    TRANSLATE_BLOCK = {
        ' ': VOID,
        '_': VOID,
        '-': VOID,
        '#': WALL,
        '$': BOX,
        '@': PLAYER,
        '+': PLAYER,
        '.': VOID,
        '*': BOX
    }
    TRANSLATE_FLOOR = {
        ' ': VOID,
        '_': VOID,
        '-': VOID,
        '#': VOID,
        '$': VOID,
        '@': VOID,
        '+': TARGET,
        '.': TARGET,
        '*': TARGET
    }
    def __init__(self, layouts) -> None:
        self.initial_tp_count = tp_count

        self.block_layout, self.floor_layout = layouts
        self.player_x: int
        self.player_y: int
        self.width = len(block_level_layout[0])
        self.height = len(block_level_layout)
        self.x_offset = (SCREEN_WIDTH / 16 - self.width) * SCREEN_WIDTH / 32
        self.y_offset = (SCREEN_HEIGHT / 16 - 2 - self.height) * SCREEN_HEIGHT / 32

        self.level: list[list[int]]
        self.floor_level: list[list[int]]
        self.targets = []
        self.moves = []
        self.won = False
        self.quit = False

        self.reset_level()

    def reset_level(self) -> None:
        self.targets = []
        self.moves = []
        self.init_level()
        self.init_floor()

    def treat_string(self, string):
        lst = string.splitlines()
        stripped_start = list(itertools.dropwhile(lambda x: x == "", lst))
        stripped_end = list(itertools.dropwhile(lambda x: x == "", reversed(stripped_start)))
        lst = list(reversed(stripped_end))
        width = len(max(lst, key=len))
        height = len(lst)
        blocks = [[self.TRANSLATE_BLOCK[char] for char in string] for string in lst]
        floor = [[self.TRANSLATE_FLOOR[char] for char in string] for string in lst]
    
    def init_level(self) -> None:
        self.level = deepcopy(self.block_layout)
        for y, row in enumerate(self.level):
            for x, cell in enumerate(row):
                if cell == PLAYER:
                    self.level[y][x] = VOID  # Clear the initial player position
                    self.player_x = x
                    self.player_y = y

    def init_floor(self) -> None:
        self.floor_level = deepcopy(self.floor_layout)
        for y, row in enumerate(self.floor_level):
            for x, cell in enumerate(row):
                if cell == TARGET:
                    self.targets.append((x, y))  # Add the targets

    def has_won(self) -> bool:
        for x, y in self.targets:
            if self.level[y][x] != BOX:
                return False
        else:
            return True

    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.level[y][x] == VOID

    def is_pushable(self, x, y, dx, dy):
        new_x, new_y = x + dx, y + dy
        return self.level[y][x] == BOX and self.is_walkable(new_x, new_y)

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if self.is_pushable(new_x, new_y, dx, dy):
            self.moves.append((self.player_x, self.player_y, new_x, new_y, new_x + dx, new_y + dy))
            temp = self.level[new_y][new_x]
            self.level[new_y][new_x] = VOID
            self.level[new_y + dy][new_x + dx] = temp
            self.player_x, self.player_y = new_x, new_y
        elif self.is_walkable(new_x, new_y):
            self.moves.append((self.player_x, self.player_y, new_x, new_y))
            self.player_x, self.player_y = new_x, new_y
        self.player_facing = (dx, dy)

    def undo(self):
        if self.moves:
            move = self.moves.pop()
            if len(move) == 4:
                old_x, old_y, new_x, new_y = move
                self.level[new_y][new_x], self.level[old_y][old_x] = self.level[old_y][old_x], self.level[new_y][new_x]
                self.player_x, self.player_y = old_x, old_y
            elif len(move) == 6:
                self.player_x, self.player_y, old_x, old_y, old_bx, old_by = move
                self.level[old_y][old_x] = self.level[old_by][old_bx]
                self.level[old_by][old_bx] = VOID

    def update(self):
        change = False
        self.quit = pyxel.btnp(pyxel.KEY_Q)
        if pyxel.btnp(pyxel.KEY_R):
            change = True
            self.reset_level()
        elif pyxel.btnp(pyxel.KEY_Z):
            change = True
            self.undo()

        if self.has_won():
            self.quit = True
            self.won = True
            self.reset_level()

        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP):
            change = True
            dy -= 1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            change = True
            dy += 1
        elif pyxel.btnp(pyxel.KEY_LEFT):
            change = True
            dx -= 1
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            change = True
            dx += 1

        if dx != 0 or dy != 0:
            self.move_player(dx, dy)
        
        if change:
            self.draw()

    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                pos_x, pos_y = (self.x_offset + x * 16, self.y_offset + y * 16)
                block_cell = self.level[y][x]
                floor_cell = self.floor_level[y][x]
                kd.fill_rect(x, y, width, height, ())
        
        pyxel.blt(self.x_offset + self.player_x * 16, self.y_offset + self.player_y * 16, 1, (1 + self.player_facing[0]) * 16, (1 + self.player_facing[1]) * 16, 16, 16, 0)


if __name__ == "__main__":
    Game()