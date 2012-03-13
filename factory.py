# our magic factory makes game items and objects for us.
# methods prefixed with spawn_ are wrappers that return a random
# object within a certain genre. i.e. spawn_foliage could return
# a tree, a bush, a cactus...

import random
import lib.libtcodpy as libtcod
import constants as C
import classes as cls
import asciimaps

# all our colors are define here for easy changing

TREE_FG = libtcod.darker_amber
TREE_BG = libtcod.black
BUSH_FG = libtcod.darker_chartreuse
BUSH_BG = libtcod.black
POOL_BG = libtcod.darker_sky
POOL_FG = libtcod.sky
PUDDLE_FG = libtcod.sky
FENCE_BG = libtcod.darkest_grey
FENCE_FG = libtcod.darker_sepia
HOLE_FG = libtcod.sepia

# define our tile characters here so we can do easy ascii to map lookups
CHAR_FENCE = "#"
CHAR_TAR = ":"
CHAR_WATER = "~"
CHAR_BRICK = chr(177)
CHAR_TREE = chr(6)
CHAR_BUSH = chr(5)

#===============================================================[[ Foliage ]]

def get_tree():
    names = ('Tree', 'Oak Tree', 'Bark Tree', 'Big Tree')
    fol = cls.Object()
    fol.char = CHAR_TREE
    fol.name = random.choice(names)
    fol.fgcolor=TREE_FG
    fol.bgcolor=TREE_BG
    fol.blocking = True
    return fol

def get_bush():
    names = ('Shrubbery', 'Thicket', 'Thornbush', 'Rosebush')
    fol = cls.Object()
    fol.char = CHAR_BUSH
    fol.name = random.choice(names)
    fol.fgcolor=BUSH_FG
    fol.bgcolor=BUSH_BG
    fol.blocking = False
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
    puddle = cls.Object()
    puddle.drinkable = True
    puddle.char = CHAR_WATER
    puddle.name = "water puddle"
    puddle.fgcolor = PUDDLE_FG
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
                            wetness = cls.Object()
                            wetness.drinkable = True
                            wetness.char = CHAR_WATER
                            wetness.fgcolor = POOL_FG
                            wetness.bgcolor = POOL_BG
                            wetness.blocking = True
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

#===================================================================[[ Map ]]

def blank_map():
    """
        Return a new, blank map array.
    """
    newmap = [[ cls.Object(
                blanktile=True
                ,fgcolor=libtcod.darker_green
                ,bgcolor=libtcod.black) 
    for y in range(C.MAP_HEIGHT)]
        for x in range(C.MAP_WIDTH)]
    return newmap

def fence_segment():
    panel = cls.Object()
    panel.name = "Fence"
    panel.char = CHAR_FENCE
    panel.bgcolor = FENCE_BG
    panel.fgcolor = FENCE_FG
    panel.blocking = True
    return panel

def fence_hole():
    hole = cls.Hole()
    hole.name = "[SPACEBAR crawls through the Hole]"
    hole.fgcolor = HOLE_FG
    hole.bgcolor = FENCE_BG
    return hole

def make_fence_holes(gamemap):
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
            if gamemap[xo][yo].blanktile:
                gamemap[x][y] = fence_hole()
                break
    

def build_fence(gamemap):
    """
        Outline the yard with a fence like structure.
    """
    for y in range(C.MAP_HEIGHT):
        gamemap[0][y] = fence_segment()
        gamemap[C.MAP_WIDTH - 1][y] = fence_segment()
    for x in range(C.MAP_WIDTH):
        gamemap[x][0] = fence_segment()
        gamemap[x][C.MAP_HEIGHT - 1] = fence_segment()
    make_fence_holes(gamemap)


def plant_foliage(gamemap):
    """
        Plant some trees and things onto the map.
    """
    # make a few large thickets
    spawn_foliage(gamemap, amount=4, thicket_size=6, density=24)
    # spread some single greens around the map
    spawn_foliage(gamemap, amount=10, thicket_size=1, density=1)
    # make some pools
    spawn_pond(gamemap, amount=1, pond_size=random.randint(4, 10), density=0)
    # make some wet spots
    spawn_pond(gamemap, amount=4, pond_size=10, density=2)
    # build the fence
    build_fence(gamemap)

def get_brick():
    """
        Make a brick tile.
    """
    brick = cls.Object()
    brick.blocking = True
    brick.name = "wall"
    brick.char = CHAR_BRICK
    brick.fgcolor = libtcod.dark_grey
    return brick

def get_tar():
    """
        Make a tar tile.
    """
    tar = cls.Object()
    tar.blocking = False
    tar.seethrough = True
    tar.fgcolor = libtcod.darkest_grey
    tar.char = CHAR_TAR
    tar.name = "tarmac"
    return tar

def map_from_ascii(gamemap):
    """
        load map tiles from an ascii representation.
    """
    tile_lookup = {
                    "#": get_brick
                    ,CHAR_TAR: get_tar
                    ,CHAR_WATER: get_puddle
                }
    amap = random.choice(asciimaps.ASCIIMaps.maps)
    print(len(amap))
    print(len(amap[0]))
    print(amap)
    for y in range(C.MAP_HEIGHT - 1):
        for x in range(C.MAP_WIDTH - 1):
            asciic = amap[y][x]
            if asciic in tile_lookup:
                gamemap[x][y] = tile_lookup[asciic]()
    
def generate_map():
    """
        Generate a level map, plant trees and objects and NPC's.
    """
    gamemap = blank_map()
    map_from_ascii(gamemap)
    plant_foliage(gamemap)
    return gamemap


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
    libtcod.console_set_default_foreground(0, libtcod.light_grey)
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
                                        ,libtcod.dark_chartreuse
                                        ,libtcod.black)
    # tile and npc names
    libtcod.console_set_color_control(libtcod.COLCTRL_4
                                        ,libtcod.light_azure
                                        ,libtcod.black)
    # all other words
    libtcod.console_set_color_control(libtcod.COLCTRL_5
                                        ,libtcod.white
                                        ,libtcod.black)
    return libtcod.console_new(C.MAP_WIDTH, C.MAP_HEIGHT)

#=============================================================[[ Unit Test ]]
if __name__ == "__main__":
    gamemap = blank_map()
    map_from_ascii(gamemap)
    pass
