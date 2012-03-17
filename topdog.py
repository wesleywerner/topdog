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
    handler.add_actions(C.STATE_DIALOGUE,
            {
            libtcod.KEY_SPACE: "player.dialogues.pop()"
            ,libtcod.KEY_ESCAPE: "player.dialogues.pop()"
            ,libtcod.KEY_KPENTER: "player.dialogues.pop()"
            })
    handler.add_actions(C.STATE_STATS or C.STATE_HELP,
            {
            libtcod.KEY_SPACE: "gamestate.pop()"
            ,libtcod.KEY_ESCAPE: "gamestate.pop()"
            ,libtcod.KEY_KPENTER: "gamestate.pop()"
            ,libtcod.KEY_KP5: "gamestate.pop()"
            })
    handler.add_actions(C.STATE_PLAYING,
            {
            "q": "gamestate.pop()"
            ,libtcod.KEY_ESCAPE: "gamestate.pop()"
            ,libtcod.KEY_KP1: "game_turn(-1, 1)"
            ,libtcod.KEY_KP2: "game_turn(0, 1)"
            ,libtcod.KEY_KP3: "game_turn(1, 1)"
            ,libtcod.KEY_KP4: "game_turn(-1, 0)"
            ,libtcod.KEY_KP5: "gamestate.push(C.STATE_STATS)"
            ,libtcod.KEY_KP6: "game_turn(1, 0)"
            ,libtcod.KEY_KP7: "game_turn(-1, -1)"
            ,libtcod.KEY_KP8: "game_turn(0, -1)"
            ,libtcod.KEY_KP9: "game_turn(1, -1)"
            ,libtcod.KEY_SPACE: "if player.can_warp(game_map): warp_level()"

            ,libtcod.KEY_UP: "game_turn(0, -1)"
            ,libtcod.KEY_DOWN: "game_turn(0, 1)"
            ,libtcod.KEY_LEFT: "game_turn(-1, 0)"
            ,libtcod.KEY_RIGHT: "game_turn(1, 0)"
            ,libtcod.KEY_F11: "player.wizard = True"
            ,"d": "player.quench_thirst(game_map)"
            ,libtcod.KEY_KPDIV: "player.quench_thirst(game_map)"
            ,"e": "player.eat_item()"
            ,libtcod.KEY_KPMUL: "player.eat_item()"
            ,"p": "player.piddle(game_map)"
            ,libtcod.KEY_KPSUB: "player.piddle(game_map)"
            ,"i": "gamestate.push(C.STATE_STATS)"
            ,"?": "blit_help()"
            })
    return handler


def game_turn(player_move_x, player_move_y):
    """
        Call all game turn actions.
    """
    if player.move(game_map, game_objects, player_move_x, player_move_y):
        # move NPC's
        for npc in game_objects:
            if isinstance(npc, cls.AnimalBase):
                if npc.move_ai:
                    npc.move_ai.take_turn(game_map, fov_map, path_map
                                        ,game_objects, (player.x, player.y))
        # recompute field of vision since we moved
        libtcod.map_compute_fov(fov_map, player.x, player.y
                                ,player.fov_radius
                                ,C.FOV_LIGHT_WALLS, C.FOV_ALGO)
    # check game state for NPC dialogues
    if len(player.dialogues) > 0:
        gamestate.push(C.STATE_DIALOGUE)

def blit_playtime():
    """
        Draw canvas and screens onto the display.
    """
    libtcod.image_blit_rect(mullions, 0, 0, 0, -1, -1, libtcod.BKGND_SET)
    libtcod.console_blit(canvas, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, C.MAP_LEFT, C.MAP_TOP)


def blit_dialogues():
    """
        Draw dialogues onto the screen.
    """
    if len(player.dialogues) > 0:
        libtcod.console_clear(0)
        dlg = player.dialogues[-1]
        if dlg.npc_picture:
            icon = libtcod.image_load(os.path.join('data', 'images', dlg.npc_picture))
        else:
            icon = libtcod.image_load(os.path.join('data', 'images', 'icon-%s.png' % (dlg.npc_name)))
        libtcod.image_blit_rect(icon, 0, C.MAP_LEFT, C.MAP_TOP, -1, -1, libtcod.BKGND_SET)
        # title
        libtcod.console_print_ex(0, 2 + (C.MAP_WIDTH / 2), 2,
                            libtcod.BKGND_NONE, libtcod.CENTER, 
                            "%c%s says:%c" % (C.COL4, dlg.npc_name, C.COLS))
#        # the message
#        libtcod.console_print_ex(0, 2 + (C.MAP_WIDTH / 2), C.MAP_TOP + 4,
#                            libtcod.BKGND_NONE, libtcod.CENTER, 
#                            "\"%c%s%c\"" % (C.COL5, dlg.dialogue, C.COLS))

        libtcod.console_print_rect(0, 4, 6, C.MAP_WIDTH - 4, C.MAP_HEIGHT - 2,
                        "\"%s\"" % (dlg.dialogue))

        # press space
        libtcod.console_print_ex(0, 2 + (C.MAP_WIDTH / 2), 
                            C.SCREEN_HEIGHT - 2, 
                            libtcod.BKGND_NONE, libtcod.CENTER, 
                            "(spacebar or enter...)")


def blit_player_stats():
    """
        Draw player stats and quests screen.
    """
    libtcod.console_clear(0)
    icon = libtcod.image_load(os.path.join('data', 'images', 'stats-frame.png'))
    libtcod.image_blit_rect(icon, 0, C.MAP_LEFT, C.MAP_TOP, -1, -1, libtcod.BKGND_SET)
    
    if player.carrying:
        if player.carrying.quest_id:
            inv_item = "%c%s%c\n%c*quest item*%c" % \
                (C.COL3, player.carrying.name, C.COLS, C.COL4, C.COLS)
        else:
            inv_item = "%c%s%c" % (C.COL3, player.carrying.name, C.COLS)
    else:
        inv_item = ""
    
    labels = (
        ""
        ,""
        ,"%clevel%c:" % (C.COL5, C.COLS)
        ,"%cscore%c:" % (C.COL5, C.COLS)
        ,"%cmoves%c:" % (C.COL5, C.COLS)
        ,"%cinventory%c:" % (C.COL5, C.COLS)
        )
    values = [
        "%cTop Dog Stats%c" % (C.COL5, C.COLS)
        ,""
        ,str(player.level)
        ,str(player.score)
        ,str(player.moves)
        ,inv_item
    ]
    
    # name, score, inventory
    libtcod.console_print_ex(0, C.STATS_SCREEN_LEFT, C.STATS_SCREEN_TOP,
                        libtcod.BKGND_NONE, libtcod.RIGHT, 
                        "\n".join(labels))

    libtcod.console_print_ex(0, C.STATS_SCREEN_LEFT + 2, C.STATS_SCREEN_TOP,
                        libtcod.BKGND_NONE, libtcod.LEFT, 
                        "\n".join(values))
    
    # quests
    values = []
    if len(player.quests) > 0:
        values = ["%cQUESTS%c" % (C.COL5, C.COLS)]
    for q in player.quests:
        values.append("+ %s" % (q.title))
    
    # hungry, thirsty, piddle, inventory
    if player.weak:
        values.append("+ %cweak%c, [e]at food" % (C.COL1, C.COLS))
    if player.hungry:
        values.append("+ %chungry%c, [e]at *food*" % (C.COL2, C.COLS))
    if player.thirsty:
        values.append("+ %cthirsty%c, [d]rink water" % (C.COL2, C.COLS))
    libtcod.console_print_ex(0, 4, C.SCREEN_HEIGHT / 2,
                        libtcod.BKGND_NONE, libtcod.LEFT, 
                        "\n".join(values))

    
    
    # player hearts
    if player.weak:
        heart_colors = [libtcod.red]* 10
    else:
        heart_colors = (libtcod.red, libtcod.red, libtcod.orange, libtcod.orange
                        , libtcod.amber, libtcod.amber, libtcod.lime, libtcod.lime
                        , libtcod.chartreuse, libtcod.chartreuse)
    for heart in range(player.get_hearts()):
        libtcod.console_put_char_ex(
                        0, heart + C.STAT_HEART_LEFT, C.STAT_HEART_TOP
                        ,chr(3), heart_colors[heart], None)
                        



def blit_help():
    """
        Show help.
    """
    libtcod.console_clear(0)
    icon = libtcod.image_load(os.path.join('data', 'images', 'stats-frame.png'))
    libtcod.image_blit_rect(icon, 0, C.MAP_LEFT, C.MAP_TOP, -1, -1, libtcod.BKGND_SET)
    
    libtcod.console_print_ex(0, C.SCREEN_WIDTH / 2, 2,
                        libtcod.BKGND_NONE, libtcod.CENTER, 
                        "%cTop Dog%c\nv%s\n^_^" % (C.COL5, C.COLS, C.VERSION))
                            

#    helptext = ["%c%s%s" % (C.COL5, C.COLS, C.VERSION)]
    helptext = ["The %cPuppy%c has been kidnapped by the %cFat Cat Mafioso%c. You travel from yard to yard, searching for the crafty Cats!" % (C.COL4, C.COLS, C.COL1, C.COLS)]
    
    helptext.append("\nYou are the %c@%c sign. Walk into other animals to interact with them." % (C.COL3, C.COLS))
    helptext.append("\n%cKEYPAD%c" % (C.COL5, C.COLS))
    helptext.append("\nUse the %cKeypad%c to move, this is preferred as \
diagonals are the dog's bark. Keypad 5 shows your stats, as does [i]nfo. The %cARROW%c keys also move you." \
        % (C.COL4, C.COLS, C.COL4, C.COLS))

    helptext.append("\n%cACTIONS%c" % (C.COL5, C.COLS))
    helptext.append("\n[%cd%c]rink water" % (C.COL5, C.COLS))
    helptext.append("[%ce%c]at food" % (C.COL5, C.COLS))
    helptext.append("[%cp%c]piddle to find reflief" % (C.COL5, C.COLS))
    helptext.append("[%ci%c]nfo screen: stats and quests" % (C.COL5, C.COLS))

    helptext.append("\nThe keypad also map to actions, use this mnemonic to remember:")
    helptext.append("\n%cD%crink and %cD%civide\n%cE%cat and %cM%cultiply\n%cP%ciddling %cS%coothes ;)" % (C.COL1, C.COLS, C.COL1, C.COLS
                , C.COL2, C.COLS, C.COL2, C.COLS
                , C.COL3, C.COLS, C.COL3, C.COLS))

    helptext.append("\nNow go find that %cPuppy!%c" % (C.COL5, C.COLS))
    helptext.append("\nWOOF!")

    libtcod.console_print_rect(0, 4, 10, C.MAP_WIDTH - 4, C.MAP_HEIGHT - 2,
                        "\n".join(helptext))
    libtcod.console_flush()
    
    # wait for key press, ignore key-ups
    while True:
        key = libtcod.console_wait_for_keypress(True)
        if key.pressed:
            break


def draw_map():
    """
        Draw the map tiles onto the canvas.
    """
    for y in range(C.MAP_HEIGHT - 0):
        for x in range(C.MAP_WIDTH - 0):
            tile = game_map[x][y]
            if player.wizard or libtcod.map_is_in_fov(fov_map, x, y):
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
        if obj.x > 0:
            if player.wizard or libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
                if not obj.seen:
#                    obj.seen = True
                    if isinstance(obj, cls.AnimalBase):
                        player.msg("You see %c%s%c" % \
                                        (C.COL4, obj.name, C.COLS)
                                        , allow_duplicates=False)
                        if obj.see_message:
                            player.msg("%c%s%c" % \
                                    (C.COL2, obj.see_message, C.COLS)
                                    ,allow_duplicates=False)
                    else:
                        player.msg("You see %c%s%c" % \
                                            (C.COL3, obj.name, C.COLS)
                                            , allow_duplicates=False)
                libtcod.console_put_char_ex(canvas, obj.x, obj.y, 
                                        obj.char, obj.fgcolor, None)
    # draw player
    libtcod.console_put_char_ex(canvas, player.x, player.y, 
                                player.char, player.fgcolor, None)

def object_at(x, y):
    for obj in game_objects:
        if obj.x == x and obj.y == y and not obj is player:
            return obj

def draw_player_stats():
    """
        Print player info and stats in the side panel.
    """
    tile = object_at(player.x, player.y)
    if not tile:
        tile = game_map[player.x][player.y]
    # the object/tile name player is standing on
    libtcod.console_print_ex(0, 2 + (C.MAP_WIDTH / 2), 
                            C.SCREEN_HEIGHT - 2, 
                            libtcod.BKGND_NONE, libtcod.CENTER, 
                            "%c%s%c" % (C.COL5, tile.name, C.COLS))
    # player hearts
    if player.weak:
        heart_colors = [libtcod.red]* 10
    else:
        heart_colors = (libtcod.red, libtcod.red, libtcod.orange, libtcod.orange
                        , libtcod.amber, libtcod.amber, libtcod.lime, libtcod.lime
                        , libtcod.chartreuse, libtcod.chartreuse)

    for heart in range(player.get_hearts()):
        libtcod.console_put_char_ex(
                        0, heart + C.STAT_HEART_LEFT, C.STAT_HEART_TOP
                        ,chr(3), heart_colors[heart], None)
    texts = []
    # player inventory
    libtcod.console_print_ex(
                    0, C.MESSAGES_LEFT + 10, C.STAT_HEART_TOP
                    ,libtcod.BKGND_NONE, libtcod.LEFT
                    ,player.inventory_name())
    if player.weak:
        libtcod.console_print_ex(0, C.MAP_WIDTH, C.STAT_HEART_TOP
                            ,libtcod.BKGND_NONE, libtcod.RIGHT
                            ,"%c*weakness*%c" % (C.COL1, C.COLS))
    elif player.thirsty:
        libtcod.console_print_ex(0, C.MAP_WIDTH, C.STAT_HEART_TOP
                            ,libtcod.BKGND_NONE, libtcod.RIGHT
                            ,"%c*thirstys*%c" % (C.COL2, C.COLS))
    elif player.hungry:
        libtcod.console_print_ex(0, C.MAP_WIDTH, C.STAT_HEART_TOP
                            ,libtcod.BKGND_NONE, libtcod.RIGHT
                            ,"%c*hungrys*%c" % (C.COL2, C.COLS))
    elif player.mustpiddle:
        libtcod.console_print_ex(0, C.MAP_WIDTH, C.STAT_HEART_TOP
                            ,libtcod.BKGND_NONE, libtcod.RIGHT
                            ,"%c*piddles*%c" % (C.COL2, C.COLS))


def draw_messages():
    """
        Display the last x messages in-game.
    """
    messages = list(player.messages)[-5:]
    if messages:
        # move messages with our player
        y = player.y - 4
        if y < C.MESSAGES_TOP:
            y = C.MESSAGES_TOP
        libtcod.console_print_ex(0
                                ,C.MAP_WIDTH / 2, y
                                ,libtcod.BKGND_NONE, libtcod.CENTER
                                ,"\n".join(messages))
    

def warp_level():
    """
        Warp to the next game level.
    """
    global game_map
    global fov_map
    global path_map
    global game_objects
    global player
    global maps_avail
    
    #prepare ftl
    player.warp_prep()
    # init new maps
    game_map, fov_map, path_map = factory.generate_map(maps_avail)
    # add player, NPC's, foliage, food
    game_objects = [player]
    # add level npcs, food, items
    game_objects.extend(factory.spawn_level_objects(game_map, player.level))
    # add level quests and story
    factory.spawn_level_quests(game_map, game_objects, player.level)
    factory.spawn_level_storyline(game_map, game_objects, player)

    # compute field of vision
    libtcod.map_compute_fov(fov_map, player.x, player.y
                            ,player.fov_radius, C.FOV_LIGHT_WALLS, C.FOV_ALGO)
    # carry our inventory item into this new level
    if player.carrying:
        game_objects.append(player.carrying)



if __name__ == "__main__":
    """
        Entry point.
    """
    canvas = factory.init_libtcod()
    mullions = libtcod.image_load(os.path.join('data', 'images','background.png'))
    kb_handler = setup_keyhandler()
    gamestate = cls.GameState()
    maps_avail = factory.count_available_maps()
    game_map = None
    path_map = None
    fov_map = None
    game_objects = None
    player = None
    
    while not libtcod.console_is_window_closed():
        state = gamestate.peek()
        if state == C.STATE_MENU:
            pass
        elif state == C.STATE_PLAYING:
            if not player:
                player = cls.Player()
                aai = cls.ActionManual(player)
                aai.attack_rating = 10
                player.action_ai = aai
                warp_level()
            # clear our displays
            libtcod.console_clear(0)
            libtcod.console_clear(canvas)
            # draw screens
            draw_map()
            draw_player_stats()
            draw_objects()
            blit_playtime()
            draw_messages()
        elif state == C.STATE_DIALOGUE:
            blit_dialogues()
            if len(player.dialogues) > 0:
                dlg = player.dialogues[-1]
            else:
                gamestate.pop()
        elif state == C.STATE_STATS:
            blit_player_stats()
        elif state == C.STATE_HELP:
            blit_help()
        if gamestate.is_empty():
            break
        libtcod.console_flush()
        cmd = kb_handler.handle_stroke(gamestate.peek())
        if cmd:
            exec cmd
    # shut down
    libtcod.dijkstra_delete(path_map)
    libtcod.console_delete(canvas)
    libtcod.console_clear(0)
