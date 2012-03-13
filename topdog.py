import os
import random
import lib.libtcodpy as libtcod
import constants as C
import factory
import classes as cls

def setup_keyhandler():
    """
        Setup our key handler for each state.
    """
    handler = cls.KeyHandler()
    handler.add_actions(C.STATE_MENU,
                            {
                            "q": "gamestate.pop()"
                            ,libtcod.KEY_SPACE: "gamestate.push(C.STATE_PLAYING)"
                            ,libtcod.KEY_ESCAPE: "gamestate.pop()"
                            })
    handler.add_actions(C.STATE_PLAYING,
                            {
                            "q": "gamestate.pop()"
                            ,libtcod.KEY_ESCAPE: "gamestate.pop()"
                            ,libtcod.KEY_KP1: "player.move(gamemap, -1, 1)"
                            ,libtcod.KEY_KP2: "player.move(gamemap, 0, 1)"
                            ,libtcod.KEY_KP3: "player.move(gamemap, 1, 1)"
                            ,libtcod.KEY_KP4: "player.move(gamemap, -1, 0)"
                            ,libtcod.KEY_KP5: "pass"
                            ,libtcod.KEY_KP6: "player.move(gamemap, 1, 0)"
                            ,libtcod.KEY_KP7: "player.move(gamemap, -1, -1)"
                            ,libtcod.KEY_KP8: "player.move(gamemap, 0, -1)"
                            ,libtcod.KEY_KP9: "player.move(gamemap, 1, -1)"
                            ,libtcod.KEY_SPACE: \
                                "if player.can_warp(gamemap): warp_level()"
                            ,"d": "player.quench_thirst(gamemap)"
                            })
    return handler

def blitscreens():
    libtcod.image_blit_rect(mullions, 0, 0, 0, -1, -1, libtcod.BKGND_SET)
    libtcod.console_blit(canvas, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, 2, 2)
    libtcod.console_flush()

def draw_map():
    """
        Draw the map tiles onto the canvas.
    """
    
    for y in range(C.MAP_HEIGHT):
        for x in range(C.MAP_WIDTH):
            tile = gamemap[x][y]
            if libtcod.map_is_in_fov(fovmap, x, y):
                tile.seen = True
                libtcod.console_put_char_ex(canvas, x, y, 
                                            tile.char, tile.fgcolor, tile.bgcolor)
            elif tile.seen:
                libtcod.console_put_char_ex(canvas, x, y, 
                                            tile.char, libtcod.darker_grey, libtcod.black)

def drawobjects():
    """
        Place all map objects on the canvas.
    """
    for obj in gameobjects:
        if libtcod.map_is_in_fov(fovmap, obj.x, obj.y):
            libtcod.console_put_char_ex(canvas, obj.x, obj.y, 
                                        obj.char, obj.fgcolor, None)

def draw_player_stats():
    """
        Print player info and stats in the side panel.
    """
    tile = gamemap[player.x][player.y]
    if not tile.blanktile:
        libtcod.console_print_ex(0, 2 + (C.MAP_WIDTH / 2), 
                                C.MAP_TILE_DESC_TOP, 
                                libtcod.BKGND_NONE, libtcod.CENTER, 
                                "%c%s%c" % (libtcod.COLCTRL_5
                                            ,tile.name
                                            ,libtcod.COLCTRL_STOP))
    # player stats
    texts = [
             "level: %c%s%c" % (libtcod.COLCTRL_5
                                ,player.level,libtcod.COLCTRL_STOP)
            ,"score: %c%s%c" % (libtcod.COLCTRL_5
                                ,player.score, libtcod.COLCTRL_STOP)
            ,"moves: %c%s%c" % (libtcod.COLCTRL_5
                                ,player.moves, libtcod.COLCTRL_STOP)
            ,"You are carrying a %c%s%c" % (libtcod.COLCTRL_3
                                ,"kitten", libtcod.COLCTRL_STOP)
            ]
    if player.thirsty:
        texts.append("You are %c%s%c. You need water." % (libtcod.COLCTRL_2
                                ,"thirsty", libtcod.COLCTRL_STOP))
    if player.weak:
        texts.append("You feel %cvery weak%c." % (libtcod.COLCTRL_1
                                , libtcod.COLCTRL_STOP))
    libtcod.console_print_ex(0, C.MESSAGES_LEFT
                            ,C.STATS_TOP
                            ,libtcod.BKGND_NONE, libtcod.LEFT
                            ,"\n".join(texts))
    
def draw_messages():
    messages = list(player.messages)
    messages.reverse()
    if messages:
        libtcod.console_print_ex(0
                                ,C.MESSAGES_LEFT
                                ,C.MESSAGES_TOP
                                ,libtcod.BKGND_NONE, libtcod.LEFT
                                ,"\n".join(messages))

def warp_level():
    """
        Warp to the next game level.
    """
    global gamemap
    global fovmap
    global gameobjects
    global player
    player.warp_prep()
    gamemap, fovmap = factory.generate_map()
    #TODO: add game objects here
    gameobjects = [player]
    libtcod.console_set_default_foreground(0, libtcod.light_grey)


if __name__ == "__main__":
    """
        Entry point.
    """
    canvas = factory.init_libtcod()
    mullions = libtcod.image_load(
                                os.path.join('data', 'images'
                                ,'background.png'))
    kb_handler = setup_keyhandler()
    gamestate = cls.GameState()
    gamemap = None
    fovmap = None
    gameobjects = None
    player = None
    
    while not libtcod.console_is_window_closed():
        state = gamestate.peek()
        if state == C.STATE_MENU:
            pass
        if state == C.STATE_PLAYING:
            if not player:
                player = cls.Player()
                warp_level()
            libtcod.console_clear(0)
            libtcod.console_clear(canvas)
            libtcod.map_compute_fov(fovmap, player.x, player.y
                                    ,player.fov_radius
                                    ,C.FOV_LIGHT_WALLS, C.FOV_ALGO)
            draw_map()
            drawobjects()
            draw_messages()
            draw_player_stats()
            blitscreens()
        if gamestate.is_empty():
            break
        cmd = kb_handler.handle_stroke(gamestate.peek())
        if cmd:
            exec cmd
    # shut down
    libtcod.console_delete(canvas)
    libtcod.console_clear(0)
