# our magic factory makes game items and objects for us.
# methods prefixed with spawn_ are wrappers that return a random
# object within a certain genre. i.e. spawn_foliage could return
# a tree, a bush, a cactus...

import random
import lib.libtcodpy as libtcod
import constants as C
import classes as cls

# all our colors are define here for easy changing

TREE_FG = libtcod.black
TREE_BG = libtcod.dark_green
BUSH_FG = libtcod.black
BUSH_BG = libtcod.dark_green
POOL_BG = libtcod.darker_sky
POOL_FG = libtcod.sky
PUDDLE_FG = libtcod.blue
FENCE_BG = libtcod.dark_grey
FENCE_FG = libtcod.grey
HOLE_BG = libtcod.dark_grey
HOLE_FG = libtcod.lightest_grey


#def dice(num, sides):
#    return sum(random.randrange(sides)+1 for die in range(num))

#===============================================================[[ Foliage ]]

def tree():
    return cls.Foliage(char="&", name="a Tree",
                      fgcolor=TREE_FG, 
                      bgcolor=TREE_BG)

def bush():
    return cls.Foliage(char="%", name="a Shrubbery",
                      fgcolor=BUSH_FG, 
                      bgcolor=BUSH_BG)
    
def spawn_foliage(currentmap, amount, thicket_size=4, density=10):
    """
        spawn amount of random foliages, using currentmap to test against
        overlapping locations. Take care not to spawn too many when the 
        map is full, this will enter an unbreakable loop.
        
        adjust the <thicket_size> and <density> parameters accordingly.
    """
    plant_choices = [tree()
                    ,bush()
                    ]

    for loop in range(amount):
        while True:
            x = random.randint(0, C.MAP_WIDTH - thicket_size - 1)
            y = random.randint(0, C.MAP_HEIGHT - thicket_size - 1)
            if currentmap[x][y].isblank():
                for thicket in range(density):
                    tx = x + random.randint(1, thicket_size)
                    ty = y +random.randint(1, thicket_size)
                    if currentmap[tx][ty].isblank():
                        currentmap[tx][ty] = random.choice(plant_choices)
                break

#=================================================================[[ Water ]]

def spawn_pond(currentmap, amount, pond_size=4, density=6):
    """
        Spawn a pond.
    """
    for loop in range(amount):
        while True:
            x = random.randint(pond_size, C.MAP_WIDTH - pond_size - 1)
            y = random.randint(pond_size, C.MAP_HEIGHT - pond_size - 1)
            
            if density == 0:
                # fill the entire range
                x = x - pond_size
                y = y - pond_size
                for ty in range(pond_size):
                    for tx in range(pond_size):
                        tile = currentmap[x + tx][y + ty]
                        if tile.isblank() or \
                        isinstance(tile, cls.Foliage):
                            wetness = cls.Water()
                            wetness.fgcolor = POOL_FG
                            wetness.bgcolor = POOL_BG
                            wetness.blocking = True
                            wetness.name = "a Pool"
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
                        puddle = cls.Water()
                        puddle.fgcolor = PUDDLE_FG
                        puddle.bgcolor = bgcolor
                        currentmap[tx][ty] = puddle
            break

#===================================================================[[ Map ]]

def new_map():
    """
        Return a new, blank map array.
    """
    newmap = [[ cls.Object(char=" ", bgcolor=libtcod.darker_green) 
    for y in range(C.MAP_HEIGHT)]
        for x in range(C.MAP_WIDTH)]
    return newmap

def fence_segment():
    panel = cls.Object()
    panel.name = "Fence"
    panel.char = "#"
    panel.bgcolor = FENCE_BG
    panel.fgcolor = FENCE_FG
    panel.blocking = True
    return panel

def fence_hole():
    hole = cls.Hole()
    hole.name = "Hole in the Fence"
    hole.fgcolor = HOLE_FG
    hole.bgcolor = HOLE_BG
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
            if gamemap[xo][yo].isblank():
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
    

def generate_map():
    """
        Generate a level map, plant trees and objects and NPC's.
    """
    gamemap = new_map()
    plant_foliage(gamemap)
    return gamemap


#===============================================================[[ Libtcod ]]

def init_libtcod():
    print('loading font.')
    libtcod.console_set_custom_font('data/fonts/arial12x12.png', 
                                    libtcod.FONT_TYPE_GREYSCALE |
                                    libtcod.FONT_LAYOUT_TCOD)
    print('creating screen.')
    libtcod.console_init_root(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, 
                              'TopDog -- v%s' % (C.VERSION), C.FULLSCREEN)
    print('running at %s fps.' % (C.LIMIT_FPS))
    libtcod.sys_set_fps(C.LIMIT_FPS)
    # set color control codes for inline string formatting
    libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.black, libtcod.white)
    libtcod.console_set_color_control(libtcod.COLCTRL_2, libtcod.white, libtcod.black)
#    libtcod.console_set_color_control(libtcod.COLCTRL_3, libtcod., libtcod.)
#    libtcod.console_set_color_control(libtcod.COLCTRL_4, libtcod., libtcod.)
#    libtcod.console_set_color_control(libtcod.COLCTRL_5, libtcod., libtcod.)
    return libtcod.console_new(C.MAP_WIDTH, C.MAP_HEIGHT)

#=============================================================[[ Unit Test ]]
if __name__ == "__main__":
    # unit test
    pass
