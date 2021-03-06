# our magic factory makes game items and objects for us.
# methods prefixed with spawn_ are wrappers that return a random
# object within a certain genre. i.e. spawn_foliage could return
# a tree, a bush, a cactus...

import os
import copy
import random
import lib.libtcodpy as libtcod
import constants as C
import classes as cls

# define our tile characters here so we can do easy ascii to map lookups
CHAR_FENCE = "#"
CHAR_GRAVEL = ":"
CHAR_STONE = chr(176)
CHAR_WATER = "~"
CHAR_BRICK = chr(177)
CHAR_TOY = chr(13)
CHAR_FOOD = chr(3)
CHAR_TREE = chr(6)
CHAR_BUSH = chr(5)
CHAR_FLOWERS = chr(15)

def dice(sides):
    return random.randint(0, sides) == 0
    
#===============================================================[[ Foliage ]]

def get_tree():
    names = ('Tree', 'Oak Tree', 'Bark Tree', 'Big Tree')
    colors = (libtcod.darkest_lime, libtcod.darkest_amber, libtcod.darkest_orange, libtcod.darkest_green)
    fol = cls.ItemBase()
    fol.char = CHAR_TREE
    fol.name = random.choice(names)
    fol.fgcolor = random.choice(colors)
    fol.blocking = False
    fol.seethrough = False
    return fol

def get_bush():
    names = ('Shrubbery', 'Thicket', 'Thornbush', 'Rosebush')
    colors = (libtcod.darkest_chartreuse
            , libtcod.darkest_green, libtcod.darkest_lime)
    fol = cls.ItemBase()
    fol.char = CHAR_BUSH
    fol.name = random.choice(names)
    fol.fgcolor = random.choice(colors)
    fol.blocking = False
    fol.fov_limit = random.randint(1, 3)
    return fol
    
def get_flower():
    names = ('Flowers', 'Roses')
    colors = (libtcod.light_amber, libtcod.light_magenta
            , libtcod.light_red, libtcod.light_azure, libtcod.light_yellow)
    fol = cls.ItemBase()
    fol.char = CHAR_FLOWERS
    fol.name = random.choice(names)
#    fol.bgcolor = libtcod.dark_green
    fol.fgcolor = random.choice(colors)
    fol.blocking = False
    fol.fov_limit = random.randint(1, 3)
    return fol

def spawn_foliage(currentmap, amount, thicket_size=4, density=10):
    """
        spawn amount of random foliages, using currentmap to test against
        overlapping locations. Take care not to spawn too many when the 
        map is full, this will enter an unbreakable loop.
        
        adjust the <thicket_size> and <density> parameters accordingly.
    """
    plant_choices = (get_tree
                    ,get_bush
                    ,get_flower
                    )

    for loop in range(amount):
        while True:
            x = random.randint(0, C.MAP_WIDTH - thicket_size - 1)
            y = random.randint(0, C.MAP_HEIGHT - thicket_size - 1)
            if currentmap[x][y].isblank():
                for thicket in range(density):
                    tx = x + random.randint(1, thicket_size)
                    ty = y +random.randint(1, thicket_size)
                    if currentmap[tx][ty].isblank():
                        currentmap[tx][ty] = random.choice(plant_choices)()
                break

#=================================================================[[ Water ]]

def get_pool_tile():
    colors = (libtcod.sky, libtcod.azure, libtcod.dark_cyan, libtcod.dark_azure)
    puddle = cls.ItemBase()
    puddle.drinkable = True
    puddle.char = CHAR_WATER
    puddle.name = "pool"
    puddle.fgcolor = random.choice(colors)
    puddle.bgcolor = libtcod.darker_sky
    puddle.message = "*splash*"
    return puddle

def spawn_pond(currentmap, amount, pond_size=4, density=6):
    """
        Spawn a pond.
    """
    for loop in range(amount):
        while True:
            x = random.randint(pond_size + 3, C.MAP_WIDTH - pond_size - 3)
            y = random.randint(pond_size + 3, C.MAP_HEIGHT - pond_size - 3)
            
            if density == 0:
                # fill the entire range
                x = x - pond_size
                y = y - pond_size
                for ty in range(pond_size):
                    for tx in range(pond_size):
                        tile = currentmap[x + tx][y + ty]
                        if tile.isblank():
                            wetness = get_pool_tile()
                            wetness.char = CHAR_WATER
                            wetness.fgcolor = POOL_FG
                            wetness.bgcolor = POOL_BG
                            wetness.name = "Pool"
                            currentmap[x + tx][y + ty] = wetness
                break
            else:
                # spot fill the range
                for litres in range(density):
                    tx = x + random.randint(1, pond_size)
                    ty = y +random.randint(1, pond_size)
                    if currentmap[tx][ty].isblank():
                        # transfer the current cell bgcolor
                        bgcolor = currentmap[tx][ty].bgcolor
                        puddle = get_pool_tile()
                        currentmap[tx][ty] = puddle
            break

#=============================================================[[ Inventory ]]

def place_on_map(game_map, game_objects, item, near_xy=None):
    """
        place item on a blank map tile. dont overlap existing objects either.
    """
    tries = 0
    radius = 4
    while True:
        tries = tries + 1
        if tries % 10 == 0:
            radius = radius + 1
        if near_xy:
            x = random.randint(near_xy[0] - radius, near_xy[0] + radius)
            y = random.randint(near_xy[1] - radius, near_xy[1] + radius)
            if x > C.MAP_WIDTH - 3:
                x = C.MAP_WIDTH - 3
            if y > C.MAP_HEIGHT - 3:
                y = C.MAP_HEIGHT - 3
            if x < 4:
                x = 4
            if y < 4:
                y = 4
        else:
            x = random.randint(4, C.MAP_WIDTH - 4)
            y = random.randint(4, C.MAP_HEIGHT - 4)
        # test against blocked map tiles
        try_again = game_map[x][y].blocking
        # test against object collisions
        if not try_again:
            for obj in game_objects:
                if obj.x == x and obj.y == y:
                    try_again = True
        if game_map[x][y].isblank() and not try_again:
            item.x, item.y = (x, y)
            break

def get_toy():
    """
        get a random toy artifact.
    """
    toy_names = ("a tennis ball", "a bouncy ball", "a rubber bone", "a knotted rope"
                ,"a rubber chicken", "a rubber ducky", "a fluffy ball"
                , "a dog tag", "a stick", "a food bowl", "a blanket", "a bouncy ball"
                )
#    toy_colors = (libtcod.light_green, libtcod.lighter_red
#                , libtcod.lighter_blue, libtcod.lighter_yellow
#                , libtcod.lighter_lime, libtcod.lighter_sea, libtcod.lighter_han
#                , libtcod.lighter_violet, libtcod.lighter_fuchsia)
    toy = cls.ItemBase()
    toy.name = random.choice(toy_names)
    toy.char = CHAR_FOOD
    toy.fgcolor = libtcod.yellow
    toy.carryable = True
    return toy


def get_food():
    """
        get a food stuff.
    """
    names = ("a biscuit", "a cherry pie", "a bone", "a banana", "salami", "a peach", "a pizza slice")
    eat = cls.ItemBase()
    eat.name = random.choice(names)
    eat.char = CHAR_FOOD
    eat.fgcolor = libtcod.light_magenta
    eat.carryable = True
    eat.edible = True
    return eat
    
#================================================================[[ Quests ]]

#def generate_quest(game_map, game_objects, default_attack_rating):
#    """
#        generate a quest and place it in game.
#    """

#    # use these variables in messages:
#    # %a - for antagonist, ie the one to recover the item from
#    # %b - for the berieved, who lost their precious toy
#    # %i - for the item name in question
#    quests = (
#        "I have lost my %i!\nPlease help me..."
#        ,"I played in the garden and\nnow my %i is missing.\nHelp me look?"
#        ,"%a took my %i.\nCan you bring it back for me?"
#    )
#    thankyous = (
#        "You found my %i,\nThank you!"
#        ,"My %i!\nI hope %a was not\nmuch trouble.\nMy Hero!"
#        ,"My Hero!\nI will always remember\nthis moment!"
#        ,"Thank you TopDog!\nMy %i is safe again..."
#    )
#    
#    # gen quest
#    quest = cls.Quest()
#    quest.reward_cmd = "player.hp = 100"
#    
#    # gen quest item
#    item = get_toy()
#    item.quest_id = quest.quest_id
#    
#    quest_text = random.choice(quests).replace("%i", item.name)
#    quest.title = "find the %s" % (item.name)
#    quest.thankyou = random.choice(thankyous).replace("%i", item.name)
#    npc = None
#    
#    # give to a NPC, or place quest item on the map
##    if random.randint(0, 1) == 0:
#    if True:
#        npc = get_random_npc(attack_rating=default_attack_rating)
#        # set attack_rating if hostile, otherwise NPC hits with 0 damaage :p
#        npc.action_ai.hostile = False
#        if npc.action_ai.hostile:
#            npc.move_ai.behaviour = random.choice((cls.MoveAI.HUNTING, cls.MoveAI.NEUTRAL))
#        else:
#            npc.move_ai.behaviour = cls.MoveAI.NEUTRAL
#        quest_text = quest_text.replace("%a", npc.name)
#        quest.thankyou = quest.thankyou.replace("%a", npc.name)
#        npc.fgcolor = libtcod.pink
#        # quest ai
#        quest_ai = cls.QuestAI(npc)
#        quest_ai.quest_id = quest.quest_id
#        quest_ai.item = item
#        # let the offender say something
##        quest_ai.message = "here take it!"     # antagonist dialogue message
#        quest.owner = npc
#        npc.quest_ai = quest_ai
#        # done
#        place_on_map(game_map, game_objects, npc)
#        game_objects.append(npc)
#    else:
#        place_on_map(game_map, game_objects, item)
#        game_objects.append(item)
#        quest_text = quest_text.replace("%a", "some animal")
#    
#    # gen quest giver
#    giver = get_random_npc()
#    aai = cls.ActionAI(giver)
#    aai.dialogue_text = quest_text
#    aai.hostile = False
#    aai.quest = quest
#    giver.action_ai = aai
#    giver.fgcolor = libtcod.yellow
#    place_on_map(game_map, game_objects, giver)
#    game_objects.append(giver)


def link_quest(game_map, game_objects 
            , title, quest_master, quest_item
            , quest_npc=None, success_dialogue=None, success_command=None
            ):
    """
        Link the given items together into a quest.
        quest_master gives us the quest.
        quest_npc keeps the item we must retrieve.
    """
    # message placeholders
    # %a - for antagonist, ie the one to recover the item from
    # %b - for the berieved, who lost their precious toy
    # %i - for the item name in question
    
    # AI (master gives the quest, npc has the item)
    ai_master = cls.QuestAI()
    quest_master.quest_ai = ai_master
    quest_item.quest_id = ai_master.quest_id
    
    if quest_npc:
        ai_npc = copy.deepcopy(ai_master)
        ai_npc.owner = quest_npc
        ai_npc.item = quest_item
        quest_npc.quest_ai = ai_npc
        title = title.replace("%npca", quest_npc.name)
        title = title.replace("%npcb", quest_master.name)
        title = title.replace("%item", quest_item.name)
    else:
        # no npc carries this item, its placed on the map.
        ai_master.owner = quest_master
    title = title.replace("%npca", "the culprit")
    title = title.replace("%npcb", quest_master.name)
    title = title.replace("%item", quest_item.name)
    ai_master.title = title
    ai_master.owner = quest_master
    # replace dialogue placeholders
    success_dialogue = [e.replace("%npcb", quest_master.name).replace("%item", quest_item.name) \
        for e in success_dialogue]
#    success_dialogue = success_dialogue.replace("%b", quest_master.name)
#    success_dialogue = success_dialogue.replace("%i", quest_item.name)
    ai_master.success_dialogue = success_dialogue


def add_random_quest(game_map, game_objects):
    """
        give a quest using random characters.
    """
    dialogues = (
        "I have lost my %item,\nPlease help me find it."
        ,"I played in the garden and\nnow my %item is missing.\nHelp me find it?"
        ,"I lost my %item,\n please find it for me Top Dog!"
        ,"%npca took my %item.\nCan you bring it back for me?"
    )
    thankyous = (
        ("You found my %item,\nThank you!")
        ,("My %item!\nI hope %npca was not\nmuch trouble.\nMy Hero!")
        ,("Thanks for returning my %item.\nI will remember this moment!")
        ,("Thank you, my %item is safe again.")
    )
    
    title = "%npcb: find %item"
    dialogue = random.choice(dialogues)
    success = random.choice(thankyous)
    
    quest_item = get_toy()
    quest_master = get_random_npc()
    quest_npc = None

    # use a quest npc to carry the item
    if dice(2):
        # is it hostile?
        if dice(6):         #!
            quest_npc = get_random_npc(attack_rating=1)
        else:
            quest_npc = get_random_npc()
        dialogue = dialogue.replace("%npca", quest_npc.name)
        place_on_map(game_map, game_objects, quest_npc)
        game_objects.append(quest_npc)
        quest_item.x = 0
    else:
        dialogue = dialogue.replace("%npca", "some thief")
        place_on_map(game_map, game_objects, quest_item)
        game_objects.append(quest_item)
    # set quest giver dialogue
    dialogue = dialogue.replace("%item", quest_item.name)
    quest_master.action_ai.dialogue_text = dialogue
    # place all on the map
    place_on_map(game_map, game_objects, quest_master)
    game_objects.append(quest_master)
    # glue the quest together
    link_quest(game_map, game_objects 
            , title, quest_master, quest_item
            , quest_npc, success_dialogue=[success])

#=================================================================[[ NPC's ]]

def get_random_npc(npc_char=None, attack_rating=None, dialogue_text=None):
    """
        get a randomly generated npc.
    """
    dna_bank = {
         "m": "mouse"
        ,"j": "monkey"
        ,"d": "dog"
        ,"D": "big dog"
        ,"c": "cat"
        ,"s": "squirrel"
        ,"b": "bird"
        ,"p": "parrot"
    }
    if not npc_char:
        npc_char = random.choice(dna_bank.keys())
    # NPC
    npc = cls.AnimalBase()
    npc.blocking = True
    npc.char = npc_char
    npc.fgcolor = libtcod.light_sky
    npc.name = dna_bank[npc_char]
    npc.move_step = random.randint(1, 3)
    npc.dialogue_text = dialogue_text
    # move AI
    mov = cls.MoveAI(npc)
    npc.move_ai = mov
    mov.behaviour = random.choice((cls.MoveAI.NEUTRAL, cls.MoveAI.SKITTISH))
    # action AI
    act = cls.ActionAI(npc)
    if attack_rating:
        if attack_rating > 0:
            mov.behaviour = cls.MoveAI.HUNTING
            act.attack_rating = attack_rating
            act.hostile = True
    npc.action_ai = act
    
    return npc


def spawn_level_objects(game_map, game_level):
    """
        create a bunch of level objects.
    """
    toys = 0
    npcs = 0
    food = 0
    objects = []
    
    # level progression grid format
    # --------------------------------
    #     NPC     |  TOYS   |  FOOD |
    # --------------------------------
    #   (min,max, |         |       |
    #     attack_rating)    |       |
    #             |,(min,max)       |
    #             |       ,(min,max)|
    progression = (
        ((0, 1, 1)  ,(1, 2)  ,(1, 1))
       ,((0, 1, 1)  ,(1, 2)  ,(1, 1))
       ,((0, 1, 1)  ,(1, 3)  ,(1, 1))
       ,((0, 2, 1)  ,(1, 3)  ,(1, 1))
       ,((1, 2, 2)  ,(2, 3)  ,(1, 2))
       ,((1, 2, 2)  ,(2, 3)  ,(1, 2))
       ,((1, 3, 2)  ,(2, 4)  ,(1, 2))
       ,((1, 3, 2)  ,(2, 4)  ,(1, 3))
       ,((2, 4, 3)  ,(6, 9)  ,(2, 3))
       ,((2, 4, 3)  ,(2, 4)  ,(2, 3))
    )
    
    prog = progression[game_level]
    npcs = random.randint(prog[0][0], prog[0][1])
    toys = random.randint(prog[1][0], prog[1][1])
    food = random.randint(prog[2][0], prog[2][1])
        
    # npcs
    for item in range(npcs):
        npc = get_random_npc(npc_char=None, attack_rating=random.randint(0, prog[0][2]))
        place_on_map(game_map, objects, npc)
        objects.append(npc)
    # toys
    for item in range(toys):
        toy = get_toy()
        place_on_map(game_map, objects, toy)
        objects.append(toy)
    # food
    for item in range(food):
        eat = get_food()
        place_on_map(game_map, objects, eat)
        objects.append(eat)
    
    return objects


def get_random_dialogue():
#    dlgs = ("Nice day today, isn't it?'",)
#    return random.choice(dlgs)
    return None
    

def add_random_npc(game_map, game_objects, npc_char=None, attack_rating=None, dialogue_text=None):
    npc = get_random_npc()
    npc.action_ai.dialogue_text = dialogue_text
    place_on_map(game_map, game_objects, npc)
    game_objects.append(npc)
    

def spawn_level_quests(game_map, game_objects, game_level):
    """
        create quests based on the level.
    """
    if game_level == 2:
        add_random_quest(game_map, game_objects)
        add_random_npc(game_map, game_objects
                , npc_char=None, attack_rating=None
                , dialogue_text="Ye, I know of the Fat Cats, the Mafioso..." \
                "\n\nI'd watch your back if I were you, those Cats scratch!")
        
    elif game_level == 3:
        add_random_quest(game_map, game_objects)
        add_random_npc(game_map, game_objects, npc_char=None
                , attack_rating=None, dialogue_text=get_random_dialogue())
        add_random_npc(game_map, game_objects
                , npc_char=None, attack_rating=None
                , dialogue_text="Ever had stitches in your snout?\n\n" \
                "I had 3 stiches where " \
                "the Mafioso scratched me. I refused to give them my dinner.")

    elif game_level == 4:
        add_random_quest(game_map, game_objects)
        add_random_npc(game_map, game_objects, npc_char=None
                , attack_rating=None, dialogue_text=get_random_dialogue())
        add_random_npc(game_map, game_objects, npc_char=None
                , attack_rating=None, dialogue_text=get_random_dialogue())
        
    elif game_level == 5:
        add_random_quest(game_map, game_objects)
        add_random_quest(game_map, game_objects)
        add_random_npc(game_map, game_objects, npc_char=None
                , attack_rating=None, dialogue_text=get_random_dialogue())
        
    elif game_level == 6:
        add_random_quest(game_map, game_objects)
        add_random_quest(game_map, game_objects)
        add_random_quest(game_map, game_objects)
        add_random_npc(game_map, game_objects, npc_char=None
                , attack_rating=None, dialogue_text=get_random_dialogue())
        add_random_npc(game_map, game_objects, npc_char=None
                , attack_rating=None, dialogue_text=get_random_dialogue())
        
    elif game_level == 7:
        add_random_quest(game_map, game_objects)
        add_random_quest(game_map, game_objects)
        add_random_quest(game_map, game_objects)
        add_random_npc(game_map, game_objects, npc_char=None
                , attack_rating=None, dialogue_text=get_random_dialogue())
        
#    elif game_level == 8:
#        
#    elif game_level == 9:
#        
#    


def spawn_level_storyline(game_map, game_objects, player):
    """
        add some NPC's and dialogue for our doggy tail.
    """
    if player.level == 1:

        npc = get_random_npc(npc_char="b", attack_rating=None)
        npc.name = "Shona the bird"
        npc.picture = "icon-bird.png"
        npc.see_message = "Shona (b) chirps you closer..."
        npc.action_ai.dialogue_text = [
            "Go to the %cright%c, find %cJulie the mouse%c to learn about " \
                "quests... Good luck!\n^_^" % (C.COL2, C.COLS, C.COL2, C.COLS)
            ,"If you get thirsty running around, stand on some water to " \
                "[d]rink.\n\nIf you get hungry, pick up some " \
                "food and [e]at it.\n\nIf you have to [p]iddle" \
                ", stand next to something interesting for " \
                "extra points ;)"
            ,"Hi Top Dog!" \
            "\n\nWatch your health hearts and messages." \
            "\n\nWalk over items to pick them up in your mouth." \
            "\n\nYou can only carry one item at a time.\n\nWalk into other" \
            " animals to talk or fight, depending if they are hostile."
        ]

        npc_b = get_random_npc(npc_char="m", attack_rating=None)
        npc_b.name = "Julie the mouse"
        npc_b.picture = "icon-mouse.png"
        npc_b.action_ai.dialogue_text = [
        "The monkey stole my piece of cheese just now!" \
            "\n\nCan you go get it back for me, pleeeeeease?" \
            "\n\nThe monkey ran South, laughing like a maniac..."
        ,"Hi Top Dog, I am Julie the mouse. Can you help me?"
        ]

        quest_item = get_food()
        quest_item.name = "Julie's cheese"
        quest_item.edible = False
        
        npc_a = get_random_npc(npc_char="j", attack_rating=1)
        npc_a.move_ai.behaviour = cls.MoveAI.NEUTRAL
        npc_a.action_ai.dialogue_text = [
        "You want %c*this*%c cheese? Ha! Not without a fight!" % (C.COL5, C.COLS)]
        
        dlg_b = [
            "I just got a birdy-gram...\n\nThe dog next door, Girly, is" \
                " asking for you.\n\nIt is %c*important*%c.\n\nCrawl into " \
                "the hole along the fence... go find her..." % (C.COL2, C.COLS)
            ,"Oh thank you Top Dog! Those monkeys are always trouble..." \
                "\n\nOh, by the way..."
        ]
        
        link_quest(game_map, game_objects 
            , "get Julie's cheese from monkey", quest_master=npc_b, quest_item=quest_item
            , quest_npc=npc_a, success_dialogue=dlg_b, success_command=None
            )
        
        place_on_map(game_map, game_objects, player, near_xy=(2, 2))
        place_on_map(game_map, game_objects, npc, near_xy=(player.x, player.y))
        place_on_map(game_map, game_objects, npc_b, near_xy=(C.MAP_WIDTH, 2))
        place_on_map(game_map, game_objects, npc_a, near_xy=(2, C.MAP_HEIGHT))
        game_objects.extend((npc, npc_b, npc_a))


    elif player.level == 2:
        
        npc_a = get_random_npc(npc_char="d", attack_rating=None)
        npc_a.name = "Girly the dog"
        npc_a.picture = "icon-dog.png"
        npc_a.action_ai.dialogue_text = [
            "I don't know more, talk to other animals, they may know..."
            ,"I saw some really Fat Cats hanging around yesterday... " \
                "mischievious they are, I bet they are behind this.\n\n" \
                "Please help us find Puppy! Who knows what they will do to her..."
            ,"Hi Top Dog, Puppy was taken!"
        ]
        
        # this quest will just give us a biscuit when we talk to Girly
        q = cls.QuestAI()
        q.owner = npc_a
        q.item = get_food()
        q.item.name = "Biscuit"
        npc_a.quest_ai = q
        # link the quest to the player. they will see it in their quest list
        qdata = cls.QuestData(q.quest_id)
        qdata.quest_id = q.quest_id
        qdata.npc_name = npc_name = "Girly"
        qdata.title = "Talk to Girly the dog"
        player.give_quest(qdata, silent=False)
        place_on_map(game_map, game_objects, npc_a)
        game_objects.append(npc_a)
        
    elif player.level == 3:
        npc_b = get_random_npc(npc_char="s", attack_rating=None)
        npc_b.see_message = "The Squirrel forages for nuts"
        npc_b.action_ai.dialogue_text = (
            "Ye, I know of the Fat Cats... the Mafioso they call themselves." \
                "\n\nI'd watch your back if I were you, those Cats scratch!")
        place_on_map(game_map, game_objects, npc_b)
        game_objects.append(npc_b)
        
    elif player.level == 4:
        npc_b = get_random_npc(npc_char=None, attack_rating=None)
        npc_b.char="C"
        npc_b.name = "Fat Cat Charles"
        npc_b.move_ai.behavior = cls.MoveAI.NEUTRAL
        npc_b.picture = "icon-fat cat.png"
        npc_b.action_ai.dialogue_text = [
            "Find my nephew, Jinx, in the next yard. He can tell you how " \
                "to find them..."
            ,"I don't like them for taking Puppy, they chased me away when " \
                "I tried to stop them."
            ,"Yes I'm a Fat Cat Mafioso, we aren't all bad, just that..." \
                "\n\nwell, a couple of the other Cats are naughty, like mischief too much."
            ,"*hiss and sputters*\n\nHey hey take it easy, rover!"
            ]
        place_on_map(game_map, game_objects, npc_b)
        game_objects.append(npc_b)
        
    elif player.level == 5:
        npc_a = get_random_npc(npc_char="c", attack_rating=None)
        npc_a.name = "Jinx the cat"
        npc_a.picture = "icon-cat.png"
        npc_a.action_ai.dialogue_text = [
            "That should get their attention..."
            ,"The Mafioso cannot be found, but if you get their attention, " \
                "they will find you.\n\nHere, take this Jingly Ball lying " \
                "here, take it next door and go brag to the Monkey " \
                "how you took it from me..."
            ,"My uncle Charlie sent you, huh? Well fine..." \
                "\n\n*Jinx shoves a toy mouse to and fro*"]
        place_on_map(game_map, game_objects, npc_a)
        game_objects.append(npc_a)
        
        # spawn a jingly ball toy nearby
        toy = get_toy()
        toy.name = "Jinx's Jingly Ball"
        place_on_map(game_map, game_objects, toy, near_xy=(npc_a.x, npc_a.y))
        game_objects.append(toy)

    elif player.level == 6:
        npc_a = get_random_npc(npc_char="p", attack_rating=None)
        npc_a.name = "Shorty the Parrot"
        npc_a.picture = "icon-parrot.png"
        npc_a.action_ai.dialogue_text = [
            "*squawk* I've been keeping an eye on those Monkeys. *creeek*" \
                " I don't trust them." \
                "\n\nI bet they work with those Fat Cats, and they steal my seed!"
            ]
        place_on_map(game_map, game_objects, npc_a)
        game_objects.append(npc_a)
        
        npc_b = get_random_npc(npc_char="j", attack_rating=None)
        npc_b.name = "Crazy the Monkey"
        npc_b.picture = "icon-monkey.png"
        npc_b.action_ai.dialogue_text = [
            "You're a pretty crafty hound, taking that cat's Jingly Ball.\n\n" \
                "I have some friends who need animals like you.\n\n" \
                "Let me go talk to some friends..."
            ]
        place_on_map(game_map, game_objects, npc_b)
        game_objects.append(npc_b)

    elif player.level == 7:
        npc_b = get_random_npc(npc_char=None, attack_rating=None)
        npc_b.char="C"
        npc_b.name = "Fat Cat Tiny"
        npc_b.move_ai.behavior = cls.MoveAI.NEUTRAL
        npc_b.picture = "icon-fat cat.png"
        npc_b.action_ai.dialogue_text = [
            "We still like your style, come on next door, maybe you can help us..."
            ,"Listen pal, it will take more than Jingly Balls to play with us, " \
                "some advice: Stay clear of Jinx, or else..."
            ,"*grimmaces* So you're the Jingly Ball con? *purrrs*"
            ]
        place_on_map(game_map, game_objects, npc_b)
        game_objects.append(npc_b)
        
    elif player.level == 8:
        npc_a = get_random_npc(npc_char="p", attack_rating=None)
        npc_a.name = "Tweety the Parrot"
        npc_a.picture = "icon-parrot.png"
        npc_a.action_ai.dialogue_text = [
            "*squawks* Oh you gave me a fright!\n\nI'm watching all those Fat Cats " \
                "across the other side of the yard. I wonder what they are up to..."
            ]
        place_on_map(game_map, game_objects, npc_a, near_xy=(player.x, player.y))
        game_objects.append(npc_a)
        
        # make a gang of Fat Cats. place a lead in front to meet you with dialogue.
        # determine the angle relative to the player
        gang_xy = None
        opp_x = C.MAP_WIDTH - player.x
#        opp_y = C.MAP_HEIGHT - player.y
#        mid_x = C.MAP_WIDTH / 2
        mid_y = C.MAP_HEIGHT / 2
        gang_xy = (opp_x, mid_y)
        lead_xy = None
        if player.x < 5:
            # place lead to the left of the gant
            lead_xy = (gang_xy[0] - 5, gang_xy[1])
        else:
            # place lead to the right of the gant
            lead_xy = (gang_xy[0] + 5, gang_xy[1])
        
        # make thee Fat Cats
        for i in range(3):
            npc_b = get_random_npc(npc_char=None, attack_rating=1)
            npc_b.char="C"
            npc_b.name = "Mafioso %s" % (i)
            npc_b.action_ai.hostile = True
            npc_b.move_ai.behavior = cls.MoveAI.HUNTING
            place_on_map(game_map, game_objects, npc_b, near_xy=gang_xy)
            game_objects.append(npc_b)
        # and the lead
        npc_c = get_random_npc(npc_char=None, attack_rating=1)
        npc_c.char="C"
        npc_c.name = "Mafioso Boss"
        npc_c.action_ai.hostile = True
        npc_c.move_ai.behavior = cls.MoveAI.HUNTING
        npc_c.picture = "icon-fat cat.png"
        npc_c.action_ai.dialogue_text = [
            "In fact, I setup this 'meeting' to trick you. If you want this Puppy " \
                "you have to go through US first!"
            ,"We hear you are looking for this Puppy. You probably thought we want " \
                "your help...."
        ]
        place_on_map(game_map, game_objects, npc_c, near_xy=lead_xy)
        game_objects.append(npc_c)
            
        # tutu the hostage bird
        npc_d = get_random_npc(npc_char="b", attack_rating=None)
        npc_d.name = "Tutu the bird"
        npc_d.picture = "icon-bird.png"
        npc_d.action_ai.dialogue_text = [
            "They keep the Puppy in the next yard, go rescue him, quickly!"
            ,"Thank you for chasing them away! I thought they were going to eat me alive!"
            ]
        place_on_map(game_map, game_objects, npc_d, near_xy=gang_xy)
        game_objects.append(npc_d)

    elif player.level == 9:
        # carryable puppy npc
        npc_a = get_random_npc(npc_char=None, attack_rating=None)
        npc_a.char = "P"
        npc_a.name = "Puppy"
        npc_a.tag = "puppy"
        npc_a.picture = "icon-puppy.png"
        npc_a.move_ai.behavior = cls.MoveAI.NEUTRAL
        npc_a.move_step = 1        
        npc_a.action_ai.dialogue_text = [
            "We better go, before they return..."
            ,"Top Dog! I am so glad to see you!\n\nThose Fat Cats are nasty, " \
                "but I bit a couple of them..."
            ]
        place_on_map(game_map, game_objects, npc_a, near_xy=None)
        game_objects.append(npc_a)

        
    
#===================================================================[[ Map ]]


def blank_map():
    """
        Return a new, blank map array.
    """
#    colors = (libtcod.darkest_lime, libtcod.darkest_green
#            , libtcod.darkest_sea, libtcod.darkest_chartreuse)
    newmap = [[ cls.ItemBase(
                fgcolor=libtcod.darker_green
                ,bgcolor=libtcod.darker_green) 
    for y in range(C.MAP_HEIGHT)]
        for x in range(C.MAP_WIDTH)]
    return newmap

def get_fence():
    panel = cls.ItemBase()
    panel.name = "Fence"
    panel.char = CHAR_FENCE
    panel.bgcolor = libtcod.dark_sepia
    panel.fgcolor = libtcod.dark_sepia
    panel.blocking = True
    panel.seethrough = False
    return panel

def get_hole():
    hole = cls.Hole()
    hole.name = "Space/Enter crawls through this hole..."
    hole.bgcolor = libtcod.darker_sepia
    hole.fgcolor = libtcod.lighter_sepia
    return hole

def place_fence_holes(game_map):
    """
        Make a few random fence holes. Test they are at least next to grass
        or foliage to crawl through.
    """
    halfx = C.MAP_WIDTH / 2
    halfy = C.MAP_HEIGHT / 2
    for holes in range(random.randint(2, 4)):
        while True:
            x = random.randint(0, C.MAP_WIDTH - 1)
            y = random.randint(0, C.MAP_HEIGHT - 1)
            xo = 0
            yo = 0
            # snap the x/y to the nearest border
            # but only x, or only y, depending on dice roll
            if random.randint(0, 1) == 0:
                if x < halfx:
                    x = 0
                    xo = 1
                    yo = y
                else:
                    x = C.MAP_WIDTH - 1
                    xo = x - 1
                    yo = y
                yo
            else:
                if y < halfy:
                    y = 0
                    yo = 1
                    xo = x
                else:
                    y = C.MAP_HEIGHT - 1
                    yo = y - 1
                    xo = x
            # test there is a space or foliage alongside
            if game_map[xo][yo].isblank():
                game_map[x][y] = get_hole()
                break
    

def build_fence(game_map):
    """
        Outline the yard with a fence like structure.
    """
    for y in range(C.MAP_HEIGHT - 0):
        game_map[0][y] = get_fence()
        game_map[C.MAP_WIDTH - 1][y] = get_fence()
    for x in range(C.MAP_WIDTH - 0):
        game_map[x][0] = get_fence()
        game_map[x][C.MAP_HEIGHT - 1] = get_fence()
    place_fence_holes(game_map)


def plant_foliage(game_map):
    """
        Plant some trees and things onto the map.
    """
    # make a few large thickets
#    spawn_foliage(game_map, amount=2, thicket_size=12, density=2)
    # make a few smaller, denser thickets
#    spawn_foliage(game_map, amount=2, thicket_size=6, density=6)
    # spread some single greens around the map
    spawn_foliage(game_map, amount=10, thicket_size=1, density=1)
    # make some wet spots
    spawn_pond(game_map, amount=3, pond_size=10, density=2)

def get_brick(color=libtcod.dark_grey):
    """
        Make a brick tile.
    """
    brick = cls.ItemBase()
    brick.blocking = True
    brick.seethrough = False
    brick.name = "wall"
    brick.char = CHAR_BRICK
    brick.fgcolor = libtcod.darker_grey
    brick.bgcolor = color
    return brick

def get_path():
    """
        Make a gravel tile.
    """
    t = cls.ItemBase()
    t.blocking = False
    t.seethrough = True
    t.fgcolor = random.choice((libtcod.darkest_green, libtcod.darkest_sea, libtcod.darkest_chartreuse))
    t.char = CHAR_GRAVEL
    t.name = ""
    return t

def get_tile(char="?", fgcolor=libtcod.white, bgcolor=libtcod.red
            , blocks=False, seethrough=True, name="", msg=None):
    """
        Make a stone tile.
    """
    t = cls.ItemBase()
    t.blocking = blocks
    t.seethrough = seethrough
    t.bgcolor = bgcolor
    t.fgcolor = fgcolor
    t.char = char
    t.name = name
    t.message = msg
    return t
    
def flip_map(game_map):
    """
        Transform the map by mirroring it on X/Y.
    """
    # mirror x
    if random.randint(0, 1) == 0:
        game_map.reverse()
    # mirror y
    if random.randint(0, 1) == 0:
        for e in game_map:
            e.reverse()
    
def read_map_file(map_index):
    """
        Read an ASCII map file and return it as a list of lines.
    """
    f = open(os.path.join('data', 'maps', 'map%s' % (map_index)))
    contents = f.read(3000)
    f.close()
    map_data = contents.split("\n")
    return map_data
    
def map_from_ascii(game_map, maps_available):
    """
        Load map tiles from an ascii representation.
    """
    # here we can map ascii values to our tile objects
    # since the ascii maps can't contain special chars
    tile_lookup = {
                    "B": "get_brick(libtcod.darker_grey)"
                    ,"R": "get_brick(libtcod.darker_flame)"
                    ,"=": "get_tile(CHAR_STONE, fgcolor=libtcod.darkest_grey, bgcolor=libtcod.darker_green)"
                    ,"-": "get_tile('-', fgcolor=libtcod.dark_green, bgcolor=libtcod.dark_green)"
                    ,"&": "get_tile('&', bgcolor=libtcod.darkest_yellow, fgcolor=random.choice((libtcod.darkest_yellow, libtcod.darkest_lime, libtcod.darker_gray)), blocks=True, name='compost', msg='the compost stinks good!')"
                    ,"[": "get_tile('[', bgcolor=libtcod.dark_grey, fgcolor=libtcod.light_grey, blocks=True, seethrough=False, name='car')"
                    ,"#": "get_fence()"
                    ,CHAR_GRAVEL: "get_path()"
                    ,";": "get_path()"
                    ,CHAR_WATER: "get_pool_tile()"
                    ,'f': "get_flower()"
                    ,'t': "get_tree()"
                    ,'b': "get_bush()"
                }
#                get_tile(char="?", color=libtcod.white, blocks=False, seethrough=True, name="")
#char="?", fgcolor=libtcod.white, bgcolor=libtcod.red
#            , blocks=False, seethrough=True, name="", msg=None

    map_data = read_map_file(random.randint(1, maps_available))
    for y in range(C.MAP_HEIGHT - 1 - 3):
        for x in range(C.MAP_WIDTH - 1 - 3):
            asciic = map_data[y][x]
            if asciic in tile_lookup:
                tile = eval(tile_lookup[asciic])
                game_map[x + 2][y + 2] = tile

def count_available_maps():
    """
        Get the count of maps available.
    """
    for num in range(100):
        if not os.path.exists(os.path.join("data", "maps", "map%s" % (num + 1))):
            return num
            break

def generate_map(maps_avail):
    """
        Generate a level map, plant trees and objects and NPC's.
    """
    game_map = blank_map()
    map_from_ascii(game_map, maps_avail)
    flip_map(game_map)
    plant_foliage(game_map)
    build_fence(game_map)
    fov_map = libtcod.map_new(C.MAP_WIDTH, C.MAP_HEIGHT)
    for y in range(C.MAP_HEIGHT - 1):
        for x in range(C.MAP_WIDTH - 1):
            libtcod.map_set_properties(fov_map, x, y
                                        ,game_map[x][y].seethrough
                                        ,not game_map[x][y].blocking and \
                                         not game_map[x][y].drinkable)
    path_map = libtcod.path_new_using_map(fov_map)
    return game_map, fov_map, path_map


#===============================================================[[ Libtcod ]]

def init_libtcod():
    startup_msg = ("analyzing air quality...", "calculating primordial soup..."
        ,"reading the future...", "carbon dating your hard drive..."
        ,"finding prime numbers...")
    print(random.choice(startup_msg))
    libtcod.console_set_custom_font('data/fonts/terminal12x12_gs_ro.png', 
                                    libtcod.FONT_TYPE_GREYSCALE |
                                    libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, 
                              'top dog -- v%s' % (C.VERSION), C.FULLSCREEN)
    libtcod.sys_set_fps(C.LIMIT_FPS)
    # default font color
    libtcod.console_set_default_foreground(0, libtcod.white)
    # set color control codes for inline string formatting
    # listed by priority: think defcon levels
    # high alert, priority one
    libtcod.console_set_color_control(libtcod.COLCTRL_1
                                        ,libtcod.light_red
                                        ,libtcod.black)
    # warning, danger will robinson
    libtcod.console_set_color_control(libtcod.COLCTRL_2
                                        ,libtcod.light_yellow
                                        ,libtcod.black)
    # informational, you got a quest item
    libtcod.console_set_color_control(libtcod.COLCTRL_3
                                        ,libtcod.light_green
                                        ,libtcod.black)
    # tile and npc names
    libtcod.console_set_color_control(C.COL4
                                        ,libtcod.light_azure
                                        ,libtcod.black)
    # all other words
    libtcod.console_set_color_control(libtcod.COLCTRL_5
                                        ,libtcod.white
                                        ,libtcod.black)
    return libtcod.console_new(C.MAP_WIDTH, C.MAP_HEIGHT)

#=============================================================[[ Unit Test ]]
if __name__ == "__main__":
    pass
