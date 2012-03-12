#from constants import *
import constants as C
import lib.libtcodpy as libtcod

DEFAULT_BRAVERY = 100
THIRST_INDEX = 100
DEFAULT_PIDDLE = 100


class Object(object):
    """
        base Object for any other class that is placed on the map
    """
    BLANK_CHAR = "."
    def __init__(self, char=BLANK_CHAR, name="",
                fgcolor=libtcod.white, bgcolor=libtcod.black):
        self.x = 0
        self.y = 0
        self.char = char
        self.name = name
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.blocking = False
        self.seethrough = False
        self.visible = True
    
    def isblank(self):
        """ test if the tile is blank to be used for placing an object. """
        return self.char == Object.BLANK_CHAR
    

class Foliage(Object):
    def __init__(self):
        super(Foliage, self).__init__()

class Player(Object):
    """
        Tracks the player state and provides helper functions
    """
    def __init__(self):
        super(Player, self).__init__()
        self.x = 2
        self.y = 2
        self.char = "@"
        self.fgcolor = libtcod.white
        self.bravery = DEFAULT_BRAVERY
        self.piddleindex = DEFAULT_PIDDLE
        self.thirsty = False
        self.moves = 0
        self.level = 0
        self.score = 0
        self.scents = []
        self.hostiles = []
        self.quests = []
        self.automove_target = None
        self.messages = []
    
    def warp_prep(self):
        self.level = self.level + 1
        self.moves = self.moves + 1
        if self.x == 0:
            self.x = C.MAP_WIDTH - 2
        elif self.x == C.MAP_WIDTH - 1:
            self.x = 1
        if self.y == 0:
            self.y = C.MAP_HEIGHT - 2
        elif self.y == C.MAP_HEIGHT - 1:
            self.y = 1
        if self.level > 1:
            self.messages = ['You enter a yard.']

    def add_message(self, message):
        if not self.messages: 
            self.messages.append(message)
        else:
            if self.messages[-1] != message:
                self.messages.append(message)
        self.messages = self.messages[-4:]
    
    def trim_message(self):
        if self.messages:
            self.messages.reverse()
            self.messages.pop()
            self.messages.reverse()
    
    def fleeing(self):
        return self.bravery < 0
    
    def take_hit(self, damage):
        self.bravery = self.bravery - damage
    
    def recover_bravery(self):
        self.bravery = DEFAULT_BRAVERY

    def thirsty(self):
        if self.moves % THIRST_INDEX == 0:
            self.thirsty = True
        return self.thirsty

    def piddle(self):
        return self.piddleindex == 0

    def piddle_step(self):
        self.piddleindex = self.piddleindex - 1
        if self.piddleindex < 0:
            self.piddleindex = 0

    def move(self, gamemap, xoffset, yoffset):
        x = self.x + xoffset
        y = self.y + yoffset
        if x >= 0 and x < C.MAP_WIDTH and y >= 0 and y < C.MAP_HEIGHT:
            if gamemap[x][y].blocking:
                self.add_message("%cthe%c %c%s%c %cstops you%c" % 
                                 (libtcod.COLCTRL_3, libtcod.COLCTRL_STOP
                                 ,libtcod.COLCTRL_2
                                 ,gamemap[x][y].name
                                 ,libtcod.COLCTRL_STOP
                                 ,libtcod.COLCTRL_3, libtcod.COLCTRL_STOP))
            else:
                self.x = x
                self.y = y
                self.moves = self.moves + 1
                if self.moves % 15 == 0:
                    self.trim_message()

class GameState():
    """
        Handles game state via a stack based finite machine.
        push(constants.STATE) a state onto the stack
        peek() a look at the current state
        pop() the topmost item off the stack (and return it)
        is_empty() returns True if all states are popped
    """
    def __init__(self):
        self.stack = [C.STATE_PLAYING]
    
    def push(self, state):
        self.stack.append(state)
        
    def peek(self):
        if len(self.stack) == 0: return 0
        return self.stack[-1:][0]
        
    def pop(self):
        return self.stack.pop()
    
    def is_empty(self):
        return len(self.stack) == 0

class Water(Object):
    """
        Represents a water tile.
    """
    def __init__(self):
        super(Water, self).__init__()
        self.char = "~"
        self.name = "Water"

class Hole(Object):
    """
        Represents a hole in the fence, similar to the stairs in a dungeon.
    """
    def __init__(self):
        super(Hole, self).__init__()
        self.char = "O"
    

class Hint(Object):
    """
        
    """
    def __init__(self):
        self.radius = 0
        self.message = None
        self.visible = False


class NPC(Object):
    """
        Non Player Character.
    """
    def __init__(self):
        super(NPC, self).__init__()
        self.x = 0
        self.y = 0
        self.color = None
        self.char = "?"
        self.quests = []
        self.dialogue = None
        self.hostile = False
        self.fleeindex = 0

    def xy(self):
        return (self.x, self.y)

    def fleeing(self):
        return self.fleeindex == 0
    
    def flee_step(self, value):
        self.fleeindex = self.fleeindex - value
        if self.fleeindex < 0:
            self.fleeindex = 0


class Quest(object):
    def __init__(self):
        self.title = None
        self.item = None
        self.reward = None


class Scent(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 0
        self.reward = None
        self.detect_message = None
        self.found_message = None

class KeyHandler(object):
    """
        Handles keystrokes and maps them to functions.
        Supports multiple game states. Neat, huh.
    """
    def __init__(self):
        self.actionsdb = {}
    
    def add_actions(self, state, actions):
        self.actionsdb[state] = actions
    
    def handle_stroke(self, state):
        """
             key may be a libtcod.KEY_CODE or a letter.
        """
        key = libtcod.console_wait_for_keypress(True)
        if not key.pressed:
            return None         # ignore key releases
        if key.vk == libtcod.KEY_CHAR: 
            key = chr(key.c)
        else:
            key = key.vk
        if self.actionsdb[state].has_key(key):
            return self.actionsdb[state][key]

#=========================================================[[ Unit Test ]]
if __name__ == "__main__":
    t = Object()
    print(t.isblank())
