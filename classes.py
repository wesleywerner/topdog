import math
import random
import lib.libtcodpy as libtcod
import constants as C

def dice(sides):
    return random.randint(0, sides) == 0
    
class Dialogue():
    def __init__(self, npc_name, npc_picture, dialogue):
        self.npc_name = npc_name
        self.npc_picture = npc_picture
        self.dialogue = dialogue
    
class ItemBase(object):
    """
        Inanimate items (foliage, water, walls) and map tiles.
    """
    def __init__(self
                ,blanktile=False
                ,char=".", name=""
                ,fgcolor=libtcod.white
                ,bgcolor=libtcod.black):
        self.x = 0
        self.y = 0
        self.blanktile = blanktile
        self.char = char
        self.name = name
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.blocking = False
        self.seethrough = True
        self.seen = False
        self.drinkable = False
        self.edible = False
        self.carryable = False
        self.fov_limit = None
        self.message = None


class ActionAI(object):
    """
        Handles interaction with other beings.
    """
    def __init__(self, owner):
        self.owner = owner
        self.hostile = False
        self.dialogue_text = None
        self.picture = None
        self.quest = None
        self.attack_rating = 0
    
    def contact_with(self, target):
        npc = self.owner
        if isinstance(target, Player):
            #TODO: logic here for behaviour
            if self.dialogue_text:
                # show dialogue to the player
                if type(self.dialogue_text) is list:
                    # this is a list of dialogues, talk our ear off
                    target.add_dialogue(Dialogue(npc.name, self.picture
                                            , self.dialogue_text.pop()))
                    if len(self.dialogue_text) == 0:
                        self.dialogue_text = None
                else:
                    # a one-liner dialogue
                    target.add_dialogue(Dialogue(npc.name, self.picture
                                            , self.dialogue_text))
                    self.dialogue_text = None
            elif self.quest:
                # give the player our quest
                target.add_quest(self.quest)
                self.quest = None
            elif self.hostile:
                # enact some hostility
                target.take_damage(npc, self.attack_rating)


class ActionManual(ActionAI):
    """
        The Action attribute for the player
    """
    def __init__(self, owner):
        self.owner = owner

    def contact_with(self, target):
        player = self.owner
        if isinstance(target, AnimalBase):
            # engage!
            if target.action_ai:
                if target.action_ai.hostile:
                    target.take_damage(target, player.action_ai.attack_rating)
                    player.add_message("you bite for %s damage" % \
                                         (player.action_ai.attack_rating))
            # let them have a go
            if target.action_ai:
                target.action_ai.contact_with(player)
            

class MoveAI(object):
    """
        Handles NPC movement.
        SKITTISH: keeps its distance
        NEUTRAL: indifferent
        FRIENDLY: follows the player at random times
        HUNTING: actively persues the player
    """
    SKITTISH = 0x0
    NEUTRAL = 0x1
    FRIENDLY = 0x2
    HUNTING = 0x3

    def __init__(self, owner):
        self.owner = owner
        self.behaviour = None
        self.erraticity = 10
        self.prey_x = 0
        self.prey_y = 0

    def take_turn(self, game_map, fov_map, path_map, game_objects, playerxy):
        npc = self.owner
        x, y = (0, 0)
        if self.behaviour == MoveAI.SKITTISH:
            x, y = playerxy
            libtcod.map_compute_fov(fov_map, npc.x, npc.y, npc.fov_radius
                                            ,C.FOV_LIGHT_WALLS, C.FOV_ALGO)
            if libtcod.map_is_in_fov(fov_map, x, y):
                # player in sight!
                if libtcod.path_compute(path_map, npc.x, npc.y, x, y):
                    x, y = libtcod.path_walk(path_map, True)
                    if not x is None:
                        npc.move(game_map, game_objects, npc.x - x, npc.y - y)
        elif self.behaviour == MoveAI.NEUTRAL:
            if dice(self.erraticity):
                x = random.randint(-1, 1)
            if dice(self.erraticity):
                y = random.randint(-1, 1)
            npc.move(game_map, game_objects, x, y)
        elif self.behaviour == MoveAI.FRIENDLY:
            pass
        elif self.behaviour == MoveAI.HUNTING:
            # look for prey
            x, y = playerxy
            libtcod.map_compute_fov(fov_map, npc.x, npc.y, npc.fov_radius
                                            ,C.FOV_LIGHT_WALLS, C.FOV_ALGO)
            if libtcod.map_is_in_fov(fov_map, x, y):
                # player in sight!
                if libtcod.path_compute(path_map, npc.x, npc.y, x, y):
                    self.prey_x = x
                    self.prey_y = y
                    x, y = libtcod.path_walk(path_map, True)
                    if not x is None:
                        npc.move(game_map, game_objects, x - npc.x, y - npc.y)
            else:
                # prowl last know prey location
                if libtcod.path_compute(path_map, npc.x, npc.y
                                        ,self.prey_x, self.prey_y):
                    x, y = libtcod.path_walk(path_map, True)
                    if not x is None:
                        npc.move(game_map, game_objects, x - npc.x, y - npc.y)
            

class AnimalBase(object):
    """
        Living things (NPC's) and the Player.
    """
    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = 100
        self.char = "?"
        self.name = "?"
        self.fgcolor = None
        self.seen = False
        self.moves = 0
        self.move_step = 1
        self.carryable = False
        self.carrying = None
        self.fov_radius = C.FOV_RADIUS_DEFAULT
        self.move_ai = None
        self.action_ai = None
        self.flying = False

    def take_damage(self, attacker, damage):
        self.hp = self.hp - damage
        if self.hp < 0:
            self.name = "%s corpse" % (self.name)
            self.char = ";"
            self.fgcolor = libtcod.red
            self.blocking = False
            self.move_ai = None
            self.action_ai = None
    
    def take_turn(self):
        if self.move_ai:
            self.move_ai.take_turn()
        
    def move(self, game_map, game_objects, xoffset, yoffset):
        """
            Move to the given xy offset if non blocking and not in deep water.
            Return True if so.
        """
        if xoffset == 0 and yoffset == 0:
            return True
        x = self.x + xoffset
        y = self.y + yoffset
        # test if within the map bounds, and no tiles block us
        if x >= 0 and x < C.MAP_WIDTH and y >= 0 and y < C.MAP_HEIGHT:
            tile = game_map[x][y]
            # cant move into a drinkable tile if already on one
            near_deep_water = tile.drinkable and game_map[self.x][self.y].drinkable
            if not tile.blocking and not near_deep_water or self.flying:
                # test if moving against another being
                blocking_us = False
                for being in game_objects:
                    if being.x == x and being.y == y and being.blocking:
                        blocking_us = True
                        if self.action_ai:
                            self.action_ai.contact_with(being)
                        break
                if not blocking_us:
                    self.moves = self.moves + 1
                    # but if we are little slow, we may need to way for next
                    # turn to move :p
                    if self.moves % self.move_step == 0:
                        self.x = x
                        self.y = y
                        return True

    def get_xy_towards(self, x, y):
        """
            Get the XY for moving towards the given location.
        """
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        # normalize to length 1 keeping direction
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return (dx, dy)


class Player(AnimalBase):
    """
        Tracks the player state and provides helper functions
    """
    def __init__(self):
        super(Player, self).__init__()
        self.x = 1
        self.y = 1
        self.char = "@"
        self.name = "player"
        self.fgcolor = libtcod.white
        self.blocking = True
        self.weak = False
        self.thirsty = False
        self.hungry = False
        self.mustpiddle = False
        self.quenches = 0
        self.level = 0
        self.score = 0
        self.message_trim_idx = 0
        self.messages = []
        self.seen = True
        self.wizard = False
        self.dialogues = []

    def add_quest(self, quest):
        #TODO notify player of our new quest
        self.add_message("got a quest!")
    
    def add_dialogue(self, dialogue):
        self.dialogues.append(dialogue)
        
    def take_damage(self, attacker, damage):
        self.hp = self.hp - damage
        self.add_message("The %s hit you for %s" % (attacker.name, damage))

    def get_hearts(self):
        """
            Return a count of hearts indicating our hp.
        """
        return int(self.hp / 10.0)
        
    def pickup_item(self, objects):
        for obj in objects:
            if obj.x == self.x and obj.y == self.y and obj.carryable:
                if not obj is self.carrying:
                    if self.carrying:
                        self.carrying.x, self.carrying.y = (obj.x, obj.y)
                    self.carrying = obj
                    self.carrying.x = 0
                    self.add_message("picked up %s" % (obj.name))
                break
    
    def move(self, game_map, game_objects, x, y):
        """
            If our parent moves okay, do some special player checks.
        """
        if super(Player, self).move(game_map, game_objects, x, y):
            self.message_trim_idx += 1
            self.pickup_item(game_objects)
            if self.message_trim_idx % 10 == 0:
                self.trim_message()
            if self.moves % C.PLAYER_THIRST_INDEX == 0:
                if self.thirsty:
                    self.weak = True
                self.thirsty = True
            tile = game_map[x][y]
            if tile.message:
                self.add_message(tile.message)
            if tile.fov_limit:
                self.fov_radius = tile.fov_limit
            else:
                self.fov_radius = C.FOV_RADIUS_DEFAULT
            return True

    def can_warp(self, game_map):
        return isinstance(game_map[self.x][self.y], Hole)
    
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
            self.messages = [
                        "You %center%c the yard..." % 
                        (C.COL4, C.COLS)]

    def add_message(self, message):
        if not self.messages: 
            self.messages.append(message)
        else:
            if self.messages[-1] != message:
                self.messages.append(message)
        self.messages = self.messages[-5:]
        self.message_trim_idx = 1
    
    def trim_message(self):
        if self.messages:
            self.messages.reverse()
            self.messages.pop()
            self.messages.reverse()

    def quench_thirst(self, game_map):
        messages = ("%c*laps water*%c, woof!", "%c*lap*lap*gulp*%c"
                    , "%c*lap*lap*lap*%c")
        if game_map[self.x][self.y].drinkable:
            self.quenches = self.quenches + 1
            self.thirsty = False
            self.add_message(random.choice(messages) % (C.COL5, C.COLS))
            if self.quenches % C.PLAYER_PIDDLE_INDEX == 0:
                self.mustpiddle = True

    def do_piddle(self):
        if self.mustpiddle:
            pass


class NPC(AnimalBase):
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
        self.ai = None
        self.quest = None


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

class Hole(ItemBase):
    """
        Represents a hole in the fence, similar to the stairs in a dungeon.
    """
    def __init__(self):
        super(Hole, self).__init__()
        self.char = "O"


class Hint(object):
    """
        
    """
    def __init__(self):
        self.radius = 0
        self.message = None
        self.visible = False


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
    pass
