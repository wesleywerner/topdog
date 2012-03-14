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
                ,libtcod.KEY_KP1: "game_turn(-1, 1)"
                ,libtcod.KEY_KP2: "game_turn(0, 1)"
                ,libtcod.KEY_KP3: "game_turn(1, 1)"
                ,libtcod.KEY_KP4: "game_turn(-1, 0)"
                ,libtcod.KEY_KP5: "pass"
                ,libtcod.KEY_KP6: "game_turn(1, 0)"
                ,libtcod.KEY_KP7: "game_turn(-1, -1)"
                ,libtcod.KEY_KP8: "game_turn(0, -1)"
                ,libtcod.KEY_KP9: "game_turn(1, -1)"
                ,libtcod.KEY_SPACE: \
                                    "if player.can_warp(game_map): warp_level()"
                ,"d": "player.quench_thirst(game_map)"
                ,libtcod.KEY_F5: "warp_level()"
                })
    return handler


def game_turn(player_move_x, player_move_y):
    """
        Call all game turn actions.
    """
    player.move(game_map, game_objects, player_move_x, player_move_y)
    for npc in game_objects:
        if isinstance(npc, cls.AnimalBase):
            if npc.move_ai:
                npc.move_ai.take_turn(game_map, game_objects)

def blitscreens():
    """
        Draw canvas and screens onto the display.
    """
    libtcod.image_blit_rect(mullions, 0, 0, 0, -1, -1, libtcod.BKGND_SET)
    libtcod.console_blit(canvas, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, 2, 8)
    libtcod.console_flush()


def draw_map():
    """
        Draw the map t2iles onto the canvas.
    """
    for y in range(C.MAP_HEIGHT - 0):
        for x in range(C.MAP_WIDTH - 0):
            tile = game_map[x][y]
            if libtcod.map_is_in_fov(fov_map, x, y) or player.wizard:
                tile.seen = True
                libtcod.console_put_char_ex(canvas, x, y, 
                                            tile.char, tile.fgcolor, tile.bgcolor)
            elif tile.seen:
                libtcod.console_put_char_ex(canvas, x, y, tile.char
                                        ,libtcod.darkest_grey, libtcod.black)

def draw_objects():
    """
        Place all map objects on the canvas.
    """
    for obj in game_objects:
        if not obj is player.carrying:
            if libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
                if not obj.seen:
                    obj.seen = True
                    player.add_message("You see a %c%s%c!" % \
                                        (C.COL3, obj.name, C.COLS))
                libtcod.console_put_char_ex(canvas, obj.x, obj.y, 
                                        obj.char, obj.fgcolor, None)
    # draw player
    libtcod.console_put_char_ex(canvas, player.x, player.y, 
                                player.char, player.fgcolor, None)


def draw_player_stats():
    """
        Print player info and stats in the side panel.
    """
    tile = game_map[player.x][player.y]
    # the tile name player is standing on
    if not tile.blanktile:
        libtcod.console_print_ex(0, 2 + (C.MAP_WIDTH / 2), 
                                C.SCREEN_HEIGHT - 2, 
                                libtcod.BKGND_NONE, libtcod.CENTER, 
                                "%c%s%c" % (C.COL5, tile.name, C.COLS))
    # player hearts
    heart_colors = (libtcod.red, libtcod.red, libtcod.orange, libtcod.orange
                    , libtcod.amber, libtcod.amber, libtcod.lime, libtcod.lime
                    , libtcod.chartreuse, libtcod.chartreuse)
    for heart in range(player.get_hearts()):
        libtcod.console_put_char_ex(
                        0, heart + C.STATS_LEFT, C.STATS_TOP
                        ,chr(3), heart_colors[heart], None)
    texts = []
    # player inventory
    if player.carrying:
        libtcod.console_print_ex(
                        0, C.MESSAGES_LEFT + 10, C.STATS_TOP
                        ,libtcod.BKGND_NONE, libtcod.LEFT
                        ,player.carrying.name)
    if player.weak:
        libtcod.console_print_ex(0, C.MAP_WIDTH, C.STATS_TOP
                            ,libtcod.BKGND_NONE, libtcod.RIGHT
                            ,"%c*weak*%c" % (C.COL1, C.COLS))
    elif player.thirsty:
        libtcod.console_print_ex(0, C.MAP_WIDTH, C.STATS_TOP
                            ,libtcod.BKGND_NONE, libtcod.RIGHT
                            ,"%c*thirsty*%c" % (C.COL2, C.COLS))
    elif player.hungry:
        libtcod.console_print_ex(0, C.MAP_WIDTH, C.STATS_TOP
                            ,libtcod.BKGND_NONE, libtcod.RIGHT
                            ,"%c*hungry*%c" % (C.COL2, C.COLS))

def draw_messages():
    """
        Display the last x messages in-game.
    """
    messages = list(player.messages)[-4:]
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
    global game_map
    global fov_map
    global game_objects
    global player
    global maps_avail
    player.warp_prep()
    game_map, fov_map = factory.generate_map(maps_avail)
    game_objects = [player]
    game_objects.extend(factory.spawn_toys(game_map))
    game_objects.extend(factory.spawn_npcs(game_map))
    # carry our inventory item into this new level
    if player.carrying:
        game_objects.append(player.carrying)

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
    maps_avail = factory.count_available_maps()
    game_map = None
    fov_map = None
    game_objects = None
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
            libtcod.map_compute_fov(fov_map, player.x, player.y
                                    ,player.fov_radius
                                    ,C.FOV_LIGHT_WALLS, C.FOV_ALGO)
            draw_map()
            draw_player_stats()
            draw_objects()
            draw_messages()
            blitscreens()
        if gamestate.is_empty():
            break
        cmd = kb_handler.handle_stroke(gamestate.peek())
        if cmd:
            exec cmd
    # shut down
    libtcod.console_delete(canvas)
    libtcod.console_clear(0)
