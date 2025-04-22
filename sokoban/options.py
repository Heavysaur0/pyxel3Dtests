
# Screen
W_WIDTH, W_HEIGHT = 256, 256
SCALE = 4
TILE_SIZE = 8 * SCALE



"""####__
#-.#__
#--###
#*---#
#----#
#--###
####__"""

# Level
VOID = 0
PLAYER = 1
WALL = 2
BOX = 3
TARGET = 3
LEVEL_CHAR_TRANSLATOR = {
    '_': VOID,
    '-': VOID,
    '.': VOID,
    '#': WALL,
    '$': BOX,
    '*': BOX,
    '@': PLAYER,
    '+': PLAYER
}
FLOOR_CHAR_TRANSLATOR = {
    '_': VOID,
    '-': VOID,
    '#': VOID,
    '$': VOID,
    '@': VOID,
    '.': TARGET,
    '*': TARGET,
    '+': TARGET
}

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