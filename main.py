import koden
import pygame

koden.pygame.init()

while not koden.action_quit:
    koden.clock.tick(60)  # 60 frames per second
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            koden.action_quit = True
        if koden.game_state["state"] == koden.MENU:
            # Handle menu interactions
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Check username input box
                input_width = 200
                input_height = 30
                input_x = koden.SCREEN_WIDTH // 2 - 50
                input_y = koden.SCREEN_HEIGHT - 140
                if (input_x <= mouse_x <= input_x + input_width and 
                    input_y <= mouse_y <= input_y + input_height):
                    koden.input_active = True
                else:
                    koden.input_active = False
                
                # Check Start Game button
                button_width = 150
                button_height = 40
                button_x1 = koden.SCREEN_WIDTH // 2 - 160
                button_x2 = koden.SCREEN_WIDTH // 2 + 10
                button_y = koden.SCREEN_HEIGHT - 80
                if (button_x1 <= mouse_x <= button_x1 + button_width and 
                    button_y <= mouse_y <= button_y + button_height):
                    # Start new game
                    koden.PLAYER["HP"] = koden.PLAYER["MAX_HP"]
                    koden.projectiles = []
                    koden.difficulty = 1
                    koden.enemies_defeated = 0  # Reset counter
                    koden.inventory = []
                    koden.enemies = [koden.spawn_enemy_random()]
                    koden.enemy_attack_delay = 0
                    koden.game_state["state"] = koden.EXPLORATION
                elif (button_x2 <= mouse_x <= button_x2 + button_width and 
                      button_y <= mouse_y <= button_y + button_height):
                    # Load game
                    if koden.load_game():
                        koden.PLAYER["HP"] = max(koden.PLAYER["HP"], 1)  # Ensure player is alive
                        koden.projectiles = []
                        koden.inventory = []
                        koden.enemies = [koden.spawn_enemy_random()]
                        koden.enemy_attack_delay = 0
                        koden.game_state["state"] = koden.EXPLORATION
                    else:
                        koden.message = "No save file found!"
            
            # Handle text input for username
            elif event.type == pygame.KEYDOWN and koden.input_active:
                if event.key == pygame.K_RETURN:
                    koden.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    koden.PLAYER["NAME"] = koden.PLAYER["NAME"][:-1]
                else:
                    if len(koden.PLAYER["NAME"]) < 15:  # Limit username length
                        koden.PLAYER["NAME"] += event.unicode
        elif koden.game_state["state"] == koden.BATTLE and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            # Check if aiming is active
            if koden.aim_active:
                # Player clicked during aiming - check accuracy
                damage_multiplier, accuracy_text = koden.check_aim_accuracy()
                koden.finish_player_attack(damage_multiplier, accuracy_text)
            elif koden.player_turn:
                # Normal button clicks
                button_y = koden.BORDER["Y"] + koden.BORDER["HEIGHT"] + 10
                button_width = 80
                button_height = 30
                button_x1 = koden.BORDER["X"]
                button_x2 = button_x1 + button_width + 10
                button_x3 = button_x2 + button_width + 10
                if button_x1 <= mx <= button_x1 + button_width and button_y <= my <= button_y + button_height:
                    # FIGHT
                    koden.player_attack()
                elif button_x2 <= mx <= button_x2 + button_width and button_y <= my <= button_y + button_height:
                    # ITEMS
                    if koden.inventory:
                        koden.use_item(koden.inventory[0])
                        koden.player_turn = False
                        koden.enemy_turn = True
                        koden.enemy_attack_delay = koden.enemy_attack_max_delay
                    else:
                        koden.message = "No items!"
                elif button_x3 <= mx <= button_x3 + button_width and button_y <= my <= button_y + button_height:
                    # ACT - spare
                    koden.message = f"Spared {koden.enemies[0].name}!"
                    koden.enemies.pop(0)
                    koden.enemies.append(koden.spawn_enemy_random())
                    koden.player_turn = False
                    koden.enemy_turn = True
                    koden.enemy_attack_delay = koden.enemy_attack_max_delay
    
    if koden.game_state["state"] == koden.MENU:
        result = koden.draw_menu()
        if result == "quit":
            koden.action_quit = True
    elif koden.game_state["state"] == koden.GAME_OVER:
        result = koden.draw_game_over()
        if result == "quit":
            koden.action_quit = True
        elif result:
            # Save score to leaderboard and go to menu
            koden.save_to_leaderboard(koden.enemies_defeated)
            koden.PLAYER["HP"] = koden.PLAYER["MAX_HP"]
            koden.projectiles = []
            koden.difficulty = 1
            koden.enemies_defeated = 0  # Reset counter
            koden.inventory = []
            koden.enemies = [koden.spawn_enemy_random()]
            koden.enemy_attack_delay = 0
            koden.game_state["state"] = koden.MENU
    else:
        koden.update()
        koden.draw()
        koden.action_dead = koden.game_over()

koden.pygame.quit()
