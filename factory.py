# our magic factory makes game items and objects for us.
# methods prefixed with spawn_ are wrappers that return a random
# object within a certain genre. i.e. spawn_foliage could return
# a tree, a bush, a cactus...

import os
import random
import lib.libtcodpy as libtcod
import constants as C
import classes as cls

# define our tile characters here so we can do easy ascii to map lookups
CHAR_FENCE = "#"
CHAR_TAR = ":"
CHAR_WATER = "~"
CHAR_BRICK = chr(177)
CHAR_TREE = chr(6)
CHAR_BUSH = chr(5)
CHAR_FLOWERS = chr(15)

#===============================================================[[ Foliage ]]

def get_tree():
    names = ('Tree', 'Oak Tree', 'Bark Tree', 'Big Tree')
    colors = (libtcod.darkest_lime, libtcod.darker_amber
            ,libtcod.darkest_amber, libtcod.darker_orange, libtcod.darkest_green)
    fol = cls.ItemBase()
    fol.char = CHAR_TREE
    fol.name = random.choice(names)
    fol.fgcolor = random.choice(colors)
    fol.blocking = False
    fol.seethrough = False
    return fol

def get_bush():
    names = ('Shrubbery', 'Thicket', 'Thornbush', 'Rosebush')
    colors = (libtcod.darker_chartreuse, libtcod.darkest_chartreuse
            , libtcod.darker_green, libtcod.darkest_green, libtcod.darkest_lime)
    fol = cls.ItemBase()
    fol.char = CHAR_BUSH
    fol.name = random.choice(names)
    fol.fgcolor = random.choice(colors)
    fol.blocking = False
    fol.fov_limit = random.randint(3, C.FOV_RADIUS_DEFAULT / 2)
    return fol
    
def get_flower():
    names = ('Flowers', 'Roses')
    colors = (libtcod.light_amber, libtcod.light_magenta
            , libtcod.light_red, libtcod.light_azure, libtcod.light_yellow)
    fol = cls.ItemBase()
    fol.char = CHAR_FLOWERS
    fol.name = random.choice(names)
    fol.fgcolor = random.choice(colors)
    fol.blocking = False
    fol.fov_limit = random.randint(3, C.FOV_RADIUS_DEFAULT / 2)
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
            if currentmap[x][y].blanktile:
                for thicket in range(density):
                    tx = x + random.randint(1, thicket_size)
                    ty = y +random.randint(1, thicket_size)
                    if currentmap[tx][ty].blanktile:
                        currentmap[tx][ty] = random.choice(plant_choices)()
                break

#=================================================================[[ Water ]]

def get_puddle():
    colors = (libtcod.sky, libtcod.azure, libtcod.darker_sky, libtcod.darkest_azure)
    puddle = cls.ItemBase()
    puddle.drinkable = True
    puddle.char = CHAR_WATER
    puddle.name = "puddle"
    puddle.fgcolor = random.choice(colors)
    puddle.message = "*splash*"
    return puddle

def get_pool_tile():
    puddle = cls.ItemBase()
    puddle.drinkable = True
    puddle.char = CHAR_WATER
    puddle.name = "pool"
    puddle.fgcolor = libtcod.sky
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
                        if tile.blanktile:
                            wetness = get_puddle()
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
                    if currentmap[tx][ty].blanktile:
                        # transfer the current cell bgcolor
                        bgcolor = currentmap[tx][ty].bgcolor
                        puddle = get_puddle()
                        currentmap[tx][ty] = puddle
            break

#=============================================================[[ Inventory ]]

def spawn_toys(game_map):
    """
        Make some toys for fido.
    """
    toys = []
    how_many = random.randint(1, 4)
    toy_names = ("tennis ball!", "bouncy ball", "rubber bone", "knotted rope"
                ,"rubber chicken", "rubber ducky")
    toy_colors = (libtcod.lighter_green, libtcod.lighter_red
                , libtcod.lighter_blue, libtcod.lighter_yellow
                , libtcod.lighter_lime, libtcod.lighter_sea, libtcod.lighter_han
                , libtcod.lighter_violet, libtcod.lighter_fuchsia)
    
    for item in range(how_many):
        toy = cls.ItemBase()
        toy.name = random.choice(toy_names)
        toy.char = chr(3)
        toy.fgcolor = random.choice(toy_colors)
        toy.carryable = True
        while True:
            x = random.randint(1, C.MAP_WIDTH - 2)
            y = random.randint(1, C.MAP_HEIGHT - 2)
            if game_map[x][y].blanktile:
                toy.x, toy.y = (x, y)
                toys.append(toy)
                break
    return toys

#=================================================================[[ NPC's ]]

##chances: 20% monster A, 40% monster B, 10% monster C, 30% monster D:
#choice = libtcod.random_get_int(0, 0, 100)
#if choice < 20:
#    #create monster A
#elif choice < 20+40:
#    #create monster B
#elif choice < 20+40+10:
#    #create monster C
#else:
#    #create monster D

def spawn_npcs(game_map):
    """
        Return a bunch of NPC's.
    """
    npcs = []
    
    for e in range(3):
        npc = cls.AnimalBase()
        npc.x = 1
        npc.y = 5 + e
        npc.char = "r"
        npc.name = "rat"
        npc.fgcolor = libtcod.blue
        npc.blocking = True
        npc.move_step = 1
        mai = cls.MoveAI(npc)
#        mai.behaviour = cls.MoveAI.HUNTING
        mai.behaviour = cls.MoveAI.FRIENDLY
        npc.move_ai = mai
        aai = cls.ActionAI(npc)
        aai.hostile = False
        aai.attack_rating = 5
        npc.action_ai = aai
        npcs.append(npc)
    
    return npcs
    
#===================================================================[[ Map ]]

def blank_map():
    """
        Return a new, blank map array.
    """
    colors = (libtcod.darkest_lime, libtcod.darkest_green
            , libtcod.darkest_sea, libtcod.darkest_chartreuse)
    newmap = [[ cls.ItemBase(
                blanktile=True
                ,fgcolor=random.choice(colors)
                ,bgcolor=libtcod.black) 
    for y in range(C.MAP_HEIGHT)]
        for x in range(C.MAP_WIDTH)]
    return newmap

def get_fence():
    panel = cls.ItemBase()
    panel.name = "Fence"
    panel.char = CHAR_FENCE
    panel.fgcolor = libtcod.dark_sepia
    panel.blocking = True
    panel.seethrough = False
    return panel

def get_hole():
    hole = cls.Hole()
    hole.name = "Spacebar to crawl through this hole..."
    hole.fgcolor = libtcod.sepia
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
            if game_map[xo][yo].blanktile:
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

def get_brick():
    """
        Make a brick tile.
    """
    brick = cls.ItemBase()
    brick.blocking = True
    brick.seethrough = False
    brick.name = "wall"
    brick.char = CHAR_BRICK
    brick.fgcolor = libtcod.dark_grey
    return brick

def get_path():
    """
        Make a tar tile.
    """
    tar = cls.ItemBase()
    tar.blocking = False
    tar.seethrough = True
    tar.fgcolor = libtcod.darker_grey
    tar.char = CHAR_TAR
    tar.name = ""
    return tar

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
                    "B": get_brick
                    ,"#": get_fence
                    ,CHAR_TAR: get_path
                    ,CHAR_WATER: get_pool_tile
                    ,'f': get_flower
                    ,'t': get_tree
                    ,'b': get_bush
                }
    map_data = read_map_file(random.randint(1, maps_available))
    for y in range(C.MAP_HEIGHT - 1 - 3):
        for x in range(C.MAP_WIDTH - 1 - 3):
            asciic = map_data[y][x]
            if asciic in tile_lookup:
                game_map[x + 2][y + 2] = tile_lookup[asciic]()

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
    print('loading font.')
    libtcod.console_set_custom_font('data/fonts/terminal12x12_gs_ro.png', 
                                    libtcod.FONT_TYPE_GREYSCALE |
                                    libtcod.FONT_LAYOUT_ASCII_INROW)
    print('creating screen.')
    libtcod.console_init_root(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, 
                              'TopDog -- v%s' % (C.VERSION), C.FULLSCREEN)
    print('running at %s fps.' % (C.LIMIT_FPS))
    libtcod.sys_set_fps(C.LIMIT_FPS)
    # default font color
    libtcod.console_set_default_foreground(0, libtcod.grey)
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
                                        ,libtcod.green
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
    print(count_available_maps())
    pass
