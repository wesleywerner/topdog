import os
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
                ,char=".", name=""
                ,fgcolor=libtcod.white
                ,bgcolor=libtcod.black):
        self.x = 0
        self.y = 0
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
        self.quest_id = None
    
    def isblank(self):
        return self.char == "."


class ActionAI(object):
    """
        Handles interaction with other beings.
    """
    def __init__(self, owner):
        self.owner = owner
        self.hostile = False
        self.dialogue_text = None
        self.attack_rating = 0
        self.quest = None
    
    def interact_with(self, target, game_objects):
        npc = self.owner
        if isinstance(target, Player):
            if self.dialogue_text:
                # show dialogue to the player
                if type(self.dialogue_text) is list:
                    # this is a list of dialogues, talk our ear off
                    target.add_dialogue(Dialogue(npc.name, npc.picture
                                            , self.dialogue_text.pop()))
                    if len(self.dialogue_text) == 0:
                        self.dialogue_text = None
                else:
                    # a one-liner dialogue
                    target.add_dialogue(Dialogue(npc.name, npc.picture
                                            , self.dialogue_text))
                    self.dialogue_text = None
            if self.hostile:
                # enact some hostility
                target.take_damage(npc, self.attack_rating)
#            if not self.hostile and npc.quest_ai:
#                target.give_quest(npc.name, npc.quest_ai.item)
#                npc.quest_ai = None
            if target.carrying and self.quest:
            #TODO: could move this out into the QuestAI.
            # then the quest giver must also get an instance of this class
                if target.carrying.quest_id:
                    if target.carrying.quest_id == self.quest.quest_id:
                        target.add_dialogue(Dialogue(npc.name, npc.picture
                                            , self.quest.thankyou))
                        self.quest = None
                        target.carrying = None
                        #TODO: give player reward


class ActionManual(ActionAI):
    """
        The Action attribute for the player
    """
    def __init__(self, owner):
        self.owner = owner

    def interact_with(self, target, game_objects):
        player = self.owner
        if isinstance(target, AnimalBase):
            # engage
            if target.action_ai:
                if target.action_ai.hostile:
                    target.take_damage(player, self.attack_rating)
                    player.msg("you bite for %s damage" % \
                             (player.action_ai.attack_rating))
                else:
                    player.msg("*sniffs* the %s" % (target.name))
            # let them have a go
            if target.action_ai:
                target.action_ai.interact_with(player, game_objects)
            if target.quest_ai:
                target.quest_ai.interact_with(player, game_objects)
        else:
            # action on inanimates, these are not tiles
            # but items in game_objects that are not AnimalBase
            player.msg("*sniffs* the %s" % (target.name))
            

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
            if dice(2):
                npc.move(game_map, game_objects, random.randint(-1, 1), random.randint(-1, 1))
            else:
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
            x, y = playerxy
            # player in sight!
            if libtcod.path_compute(path_map, npc.x, npc.y, x, y):
                # stick a little bit away
                if libtcod.path_size(path_map) > 3:
                    x, y = libtcod.path_walk(path_map, True)
                    if not x is None:
                        npc.move(game_map, game_objects, x - npc.x, y - npc.y)
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


class QuestAI(object):
    """
        Quest AI for NPC's.
    """
    def __init__(self, owner):
        self.owner = owner
        self.quest_id = None
        self.item = None
        self.message = None

    def interact_with(self, target, game_objects):
        npc = self.owner
        if isinstance(target, Player):
            #TODO: we can check if the player is seeking this quest via
            # [e for e in target.seek_quests if e.quest_id == self.quest_ai.quest_id]
            if self.message:
                target.add_dialogue(Dialogue(npc.name, npc.picture, self.message))
                self.message = None
            if not npc.action_ai.hostile and self.quest_id:
                target.msg("%s %c*gives*%c you a %s" % (npc.name, C.COL3, C.COLS, self.item.name))
                target.give_item(self.item)
                self.quest_id = None
            if npc.hp < 0 and self.quest_id:
                target.msg("%s %c*dropped*%c something!" % (npc.name, C.COL3, C.COLS))
                self.item.x = npc.x
                self.item.y = npc.y
                game_objects.append(self.item)
                self.quest_id = None

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
        self.blocking = True
        self.see_message = None
        self.moves = 0
        self.move_step = 1
        self.carryable = False
        self.carrying = None
        self.fov_radius = C.FOV_RADIUS_DEFAULT
        self.move_ai = None
        self.action_ai = None
        self.quest_ai = None
        self.quest = None
        self.flying = False
        self.picture = None

    def take_damage(self, attacker, damage):
        self.hp = self.hp - damage
        if self.hp < 0:
            if self.move_ai:
                if isinstance(attacker, Player):
                    attacker.msg("%s flees!" % (self.name))
                self.move_ai.behaviour = MoveAI.SKITTISH
    
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
            near_deep_water = tile.drinkable and \
                                            game_map[self.x][self.y].drinkable
            if not tile.blocking and not near_deep_water or self.flying:
                # test if moving against another being
                blocking_us = False
                for being in game_objects:
                    if being.x == x and being.y == y and being.blocking:
                        blocking_us = True
                        if self.action_ai:
                            self.action_ai.interact_with(being, game_objects)
                        if self.quest_ai:
                            self.quest_ai.interact_with(being, game_objects)
                        return True
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
        self.name = "topdog"
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
        self.wizard = True
        self.dialogues = []
        self.seek_quests = []
    
    def eat_item(self):
        if self.carrying:
            if self.carrying.edible:
                self.hp = self.hp + 15.0
                if self.hp > 100:
                    self.hp = 100
                self.carrying = None
                self.msg("Yum!")
        
    def give_item(self, item):
        """
            give player an inventory item, drops items if we have to.
        """
        if self.carrying:
            self.carrying.x, self.carrying.y = (self.x, self.y)
        self.carrying = item
        self.carrying.x = 0
        self.msg("got a %s" % (item.name))
    
    def give_quest(self, npc_name, quest):
        self.seek_quests.append(quest)
        self.msg("%s gave you a %c*quest*%c!" % (npc_name, C.COL2, C.COLS))
    
    def add_dialogue(self, dialogue):
        self.dialogues.insert(0, dialogue)
        
    def take_damage(self, attacker, damage):
        self.hp = self.hp - damage
        if self.hp < 0:
            self.hp = 0
        self.msg("The %s hit you for %s" % (attacker.name, damage))

    def get_hearts(self):
        """
            Return a count of hearts indicating our hp.
        """
        return int(self.hp / 10.0)
        
    def pickup_item(self, objects):
        for obj in objects:
            if obj.x == self.x and obj.y == self.y and obj.carryable:
                self.give_item(obj)
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
                self.msg(tile.message)
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

    def msg(self, message):
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
            self.msg(random.choice(messages) % (C.COL5, C.COLS))
            if self.quenches % C.PLAYER_PIDDLE_INDEX == 0:
                self.mustpiddle = True

    def do_piddle(self):
        if self.mustpiddle:
            pass


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


class Quest(object):
    """
        Quest details given to the player by a NPC.
    """
    def __init__(self):
        self.owner = None
        self.quest_id = os.urandom(2)
        self.title = None
        self.thankyou = None
        self.reward_cmd = None
    

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
