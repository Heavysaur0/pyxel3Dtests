import numpy as np
import pyxel

from render.object import Object
from render.camera import Camera
from render.render import Render
from render.mesh import Mesh

from stack import Stack

from options import W_WIDTH, W_HEIGHT, TILE_SIZE
from options import VOID, PLAYER, WALL, BOX, TARGET, LEVEL_CHAR_TRANSLATOR, FLOOR_CHAR_TRANSLATOR


def face_quad(x, y, w, h, face):
    # Return the 4 vertices for a quad at (x, y) of size (w, h) facing `face`
    if face == 'top':
        return [
            (x,     1, y    ),
            (x,     1, y + h),
            (x + w, 1, y + h),
            (x + w, 1, y    ),
        ]
    elif face == 'left':
        return [
            (x, 0, y + h),
            (x, 1, y + h),
            (x, 1, y    ),
            (x, 0, y    ),
        ]
    elif face == 'right':
        return [
            (x + w, 0, y    ),
            (x + w, 1, y    ),
            (x + w, 1, y + h),
            (x + w, 0, y + h),
        ]
    elif face == 'front':
        return [
            (x + w, 0, y + h),
            (x + w, 1, y + h),
            (x,     1, y + h),
            (x,     0, y + h),
        ]
    elif face == 'back':
        return [
            (x,     0, y),
            (x,     1, y),
            (x + w, 1, y),
            (x + w, 0, y),
        ]
    else:
        raise ValueError(f"Unknown face: {face}")

def find(array, element):
    for index, ele in enumerate(array):
        if ele == element:
            return index
    return -1


class Level:
    def __init__(self, layout: str):
        self.camera = Camera((-8, 12, -8), -20, 140)
        self.render = Render(self.camera, cull_face=True, depth_sort=True)
        
        self.width: int = 0
        self.height: int = 0

        self.initial_boxes: set[tuple[int, int]] = set()
        self.boxes: set[tuple[int, int]] = set()
        self.targets: set[tuple[int, int]] = set()

        self.initial_player_pos: tuple[int, int] = (0, 0)
        self.player_pos: tuple[int, int] = (0, 0)
        self.player_facing: tuple[int, int] = (1, 0)

        self.level, self.floor = self.get_level_floor(layout)

        self.mesh = self.get_mesh()
        self.object = Object(self.render, self.mesh)

        self.moves = Stack()
        self.quit = False
        self.won = False

    def get_level_floor(self, layout):
        layout = [row.strip() for row in layout.split('\n')]
        layout = [row for row in layout if row]

        self.height = len(layout)
        self.width = len(layout[0])

        level = np.zeros((self.width, self.height), dtype=bool)
        floor = np.zeros((self.width, self.height), dtype=np.uint8)
        for y in range(self.height):
            for x in range(self.width):
                char = layout[y][x]
                level_tile = LEVEL_CHAR_TRANSLATOR[char]
                floor_tile = FLOOR_CHAR_TRANSLATOR[char]

                level[x, y] = level_tile == WALL
                floor[x, y] = floor_tile

                if level_tile == BOX:
                    self.initial_boxes.add((x, y))
                    self.boxes.add((x, y))
                elif level_tile == PLAYER:
                    self.initial_player_pos = (x, y)
                    self.player_pos = (x, y)
                if floor_tile == TARGET:
                    self.targets.add((x, y))

        if len(self.boxes) != len(self.targets):
            raise ValueError(f"The should be an exact amount of targets and boxes. "
                             f"Num of boxes: {len(self.boxes)}, num of targets: {len(self.targets)}.")

        return level, floor

    def greedy_mesh_2d(self, mask, face, vertex_data, index_data, index_map, 
                       color_data, fill_data, outer_border_data):
        visited = np.zeros_like(mask, dtype=bool)
        for x in range(self.width):
            for y in range(self.height):
                if not mask[x, y] or visited[x, y]:
                    continue

                # Start growing a quad
                w, h = 1, 1
                while x + w < self.width and mask[x + w, y] and not visited[x + w, y]:
                    w += 1
                done = False
                while y + h < self.height:
                    for dx in range(w):
                        if not mask[x + dx, y + h] or visited[x + dx, y + h]:
                            done = True
                            break
                    if done: break
                    h += 1

                # Mark visited
                for dx in range(w):
                    for dy in range(h):
                        visited[x + dx, y + dy] = True

                # Add quad
                verts = face_quad(x, y, w, h, face)
                offset = len(vertex_data)
                indices = []

                for vertex in verts:
                    if vertex in index_map:
                        indices.append(index_map[vertex])
                    else:
                        index_map[vertex] = offset
                        vertex_data.append(vertex)
                        indices.append(offset)
                        offset += 1

                index_data.append(indices)
                border = face in ('right', 'left', 'front', 'back')
                fill_data.append(True)
                outer_border_data.append(1 if border else -1)
                color_data.append(9 if border else 13)

    def should_create_face(self, x, y, dx, dy):
        # Determines whether a face is visible in that direction
        if not self.level[x, y]:
            return False
        if dx == dy == 0:
            return True
        nx, ny = x + dx, y + dy
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return True
        return not self.level[nx, ny]

    def get_mesh(self):
        vertex_data = []
        index_data = []
        index_map = {}
        color_data = []
        fill_data = []
        outer_border_data = []

        directions = [
            ('top', 0, 0, 1),
            ('left', -1, 0, 0),
            ('right', 1, 0, 0),
            ('front', 0, 1, 0),
            ('back', 0, -1, 0),
        ]

        for face, dx, dy, dz in directions:
            mask = np.zeros((self.width, self.height), dtype=bool)
            for x in range(self.width):
                for y in range(self.height):
                    if self.should_create_face(x, y, dx, dy):
                        mask[x, y] = True
            self.greedy_mesh_2d(mask, face, vertex_data, index_data, index_map, color_data, 
                                fill_data, outer_border_data)

        return Mesh(vertex_data, index_data, color_data,
                    fill_data=fill_data,
                    outer_border_data=outer_border_data)

    def reset(self):
        self.player_pos = self.initial_player_pos
        self.boxes = self.initial_boxes.copy()
        self.moves = Stack()

    def victory(self):
        for target in self.targets:
            if not target in self.boxes:
                return False
        return True

    def is_solid(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.level[x, y] or self.is_box(x, y)

    def is_box(self, x, y):
        return (x, y) in self.boxes

    def is_pushable(self, x, y, dx, dy):
        new_x, new_y = x + dx, y + dy
        if (x, y) in self.boxes:
            if self.level[new_x, new_y] or self.is_solid(new_x, new_y) or self.is_box(new_x, new_y):
                return False
            return True

    def move_player(self, dx, dy):
        new_x, new_y = self.player_pos[0] + dx, self.player_pos[1] + dy

        if self.is_box(new_x, new_y) and self.is_pushable(new_x, new_y, dx, dy):
            box_position = (new_x + dx, new_y + dy)
            # Append current move: player position, box position, next box position
            self.moves.append((self.player_pos, (new_x, new_y), box_position))
            self.boxes.remove((new_x, new_y))
            self.boxes.add(box_position)
            self.player_pos = (new_x, new_y)
        elif not self.is_solid(new_x, new_y):
            self.moves.append((self.player_pos, ))
            self.player_pos = (new_x, new_y)

        self.player_facing = (dx, dy)

    def undo(self):
        if self.moves.is_empty():
            return
        move = self.moves.pop()
        if len(move) == 1:
            # Just moved
            self.player_pos = move[0]
        elif len(move) == 3:
            # Pushed a box
            self.player_pos, box_pos, curr_box_pos = move
            self.boxes.remove(curr_box_pos)
            self.boxes.add(box_pos)

    def update(self):
        self.render.clear()
        
        self.quit = pyxel.btnp(pyxel.KEY_Q)

        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
        elif pyxel.btnp(pyxel.KEY_Z):
            self.undo()

        if self.victory():
            self.quit = True
            self.won = True

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

        self.camera.update()
        self.object.update()

    def draw(self):
        self.object.draw()
        self.render.draw()


if __name__ == '__main__':
    LEVELS = """
    ########
    #####@.#
    ####.$$#
    ####-$-#
    ###-.#-#
    ###----#
    ###--###
    ########


    ########
    ###-.###
    ###-@###
    #.-$.###
    #-#--###
    #-$$-###
    ###--###
    ########


    ########
    #+-$-###
    #-$--###
    #-#--###
    #--$####
    #.#-####
    #.--####
    ########


    ########
    ####@-##
    ##---$##
    ##-#.-##
    ##---$##
    ####.$-#
    ####--.#
    ########


    ########
    ##@-####
    ##$$####
    #-$---##
    #-#--.##
    #.---###
    ###-.###
    ########


    ########
    ####--.#
    ####---#
    ###..$.#
    ###-#$-#
    ###--$$#
    #####@-#
    ########
    """.split("\n\n")
    LEVELS = ["""
_____##################______
_____#--#@-########---#______
_____#---$-##---------#______
_____#--#--##$######-####____
_____##.#-##--#---#-$-.-#____
####_-#-#--#---$#-#---#-#____
#--####-##*#-##----####-#____
#-.*----#-.$$-#-$$-####-#____
#--$$$-##-.$--#-$--#----#____
##*#-##--$.#--#$--#--######__
_#.--##-$..-##--$-#-#-----#__
_#-#-####--$-----##-#.##**##_
_#--..--######-####-.--$---#_
_#####$-...-$-....-#-*-#$--#_
__#--.--##$.######-##-.--###_
__#-##*#---$-#####.$-$-###___
###$-..#.#--$---##.--.#--#___
#--..#.#-$$*-##--##-###-.####
#-$$$-$-..-.-###--#---$*-.--#
###.-$-#####$####$#*###-.*.-#
_#--####---.-----.*--##*--###
##-#####-##.#####-##--*-.##__
#------#..$.-####-###-#--#___
#-$$#--$..#..$--------####___
#----$$##-#######-#$#$#______
###$$--$--#____#--$---#______
__#----####____#----###______
__######_______#--###________
_______________####__________
"""]


    class App:
        def __init__(self):
            self.level = None
            self.index = 0
            self.re_level()
            pyxel.init(W_WIDTH, W_HEIGHT, fps=30)

        def update(self):
            self.level.update()
            if pyxel.btnp(pyxel.KEY_Q):
                self.index -= 1
                self.re_level()
            elif pyxel.btnp(pyxel.KEY_D):
                self.index += 1
                self.re_level()

        def re_level(self):
            self.index %= len(LEVELS)
            self.level = Level(None, LEVELS[self.index])

        def draw(self):
            self.level.draw()

        def run(self):
            pyxel.run(self.update, self.draw)

    app = App()
    app.run()
