import pyxel
from time import perf_counter

from render.mesh import Mesh
from level import Level

from options import W_WIDTH, W_HEIGHT, SCALE

"""List of how to string levels:
* '_': void
* '#': wall
* '-': ground
* '.': target
* '$': box
* '@': player
* '*': box on target
* '+': player on target
"""

LEVEL = """
####__
#-.#__
#--###
#*--@#
#--$-#
#--###
####__
"""

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


CUBE_VERTICES = tuple((a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1))
CUBE_INDICES = (
    (0, 1, 2), (2, 1, 3), # Bottom face
    (1, 0, 4), (1, 4, 5), # Front face
    (0, 2, 4), (4, 2, 6), # Left face
    (3, 1, 5), (3, 5, 7), # Right face
    (5, 4, 6), (5, 6, 7), # Top face
    (2, 3, 6), (6, 3, 7) # Back face
)
CUBE_COLOR = tuple((i % 15) + 1 for i in range(len(CUBE_INDICES)))


class App:
    def __init__(self):
        pyxel.init(W_WIDTH, W_HEIGHT, fps=60, display_scale=SCALE)
        self.meshes = {}
        self.level = None
        self.index = 0

        self.current_time = perf_counter()
        self.delta_time = 0
        self.time = 0

        self.load_meshes()

    def load_meshes(self):
        self.meshes["cube"] = Mesh(CUBE_VERTICES, CUBE_INDICES, CUBE_COLOR)

    def update(self):
        if self.level is not None:
            self.level.update()
        else:
            if pyxel.btnp(pyxel.KEY_Q):
                self.index -= 1
                self.level = None
            if pyxel.btnp(pyxel.KEY_D):
                self.index += 1
                self.level = None

        if self.level is None:
            self.re_level()

    def re_level(self):
        self.index %= len(LEVELS)
        self.level = Level(LEVELS[self.index])

    def draw(self):
        pyxel.cls(0)
        if self.level is not None:
            self.level.draw() # Buffer triangles into the render and draw them

        current_time = perf_counter()
        self.delta_time = current_time - self.current_time
        print(f"FPS: {1 / self.delta_time}")

        self.current_time = current_time
        self.time += self.delta_time

    def run(self):
        pyxel.run(self.update, self.draw)


if __name__ == '__main__':
    app = App()
    app.run()