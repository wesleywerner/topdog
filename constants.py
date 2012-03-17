import lib.libtcodpy as libtcod
VERSION = "0.1"

# engine
SCREEN_WIDTH = 44
SCREEN_HEIGHT = 50
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
LIMIT_FPS = 20
FULLSCREEN = False

# drawing positions
MAP_TOP = 8
MAP_LEFT = 2
MAP_WIDTH = 40
MAP_HEIGHT = 40
MESSAGES_LEFT = 3
MESSAGES_TOP = 1
STAT_HEART_LEFT = 2
STAT_HEART_TOP = 6
STATS_SCREEN_LEFT = 14
STATS_SCREEN_TOP = 12

# game states
STATE_MENU = 0x1
STATE_PLAYING = 0x2
STATE_DIALOGUE = 0x3
STATE_STATS = 0x4
STATE_HELP = 0x5

# player tweaks
FOV_RADIUS_DEFAULT = 6         # default player fov. gets reduces under shrubbery.
PLAYER_THIRST_INDEX = 400       # amount of moves before we get thirsty
PLAYER_PIDDLE_INDEX = 3         # amount ofquesnches before we need to piddle
PLAYER_WEAK_HP_DICE = 12        # if weak, the dice roll that reduces hp each move

# make less typing
COL1 = libtcod.COLCTRL_1
COL2 = libtcod.COLCTRL_2
COL3 = libtcod.COLCTRL_3
COL4 = libtcod.COLCTRL_4
COL5 = libtcod.COLCTRL_5
COLS = libtcod.COLCTRL_STOP
