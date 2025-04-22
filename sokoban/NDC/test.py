import itertools


TELEPORT_BOX = -3
FIRST_BOX = -2
PLAYER = -1
VOID = 0
WALL = 1
BOX = 2
TARGET = 3


string = """
________________#####________
__________#####_#---########_
_####_____#---###@$.-------#_
_#--####__#-#--###-####-$$$#_
##$----#__#-$--.----#--#-*.#_
#---#$-#_###-##.$.$-#-$-**-#_
#.-..$*###-$*-#-##$##---$..#_
#--#---..--$-$#-#--#####.*-#_
#######-####.---#-.-----#.-#_
#####-#-#----####-#####-##-##
#---###-#.#######-#---#.$.$-#
#-$----$#-$---$-$---$-#-----#
##-####.#.$------$-#$##-#####
_#-##---.###*####--#-##-####_
_#-##--$--#-.-#--###-##-#--#_
##-####.*.#*.*#----#-##--$-#_
#--#---#$-#.*-#--*-#-####.-#_
#-$--$-#.---*.##**-#----#$-#_
#--##-##-..*..##---$--#--.-#_
####--##########.###--######_
___#-$----------$-#####______
___#--#########---#__________
___####_______#####__________
"""

block_translator = {
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
floor_translator = {
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

def treat_string(string):
    lst = string.splitlines()
    stripped_start = list(itertools.dropwhile(lambda x: x == "", lst))
    stripped_end = list(itertools.dropwhile(lambda x: x == "", reversed(stripped_start)))
    lst = list(reversed(stripped_end))
    width = len(max(lst, key=len))
    height = len(lst)
    blocks = [[block_translator[char] for char in string] for string in lst]
    floor = [[floor_translator[char] for char in string] for string in lst]
    return blocks, floor

print(treat_string(string))