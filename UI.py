from pickle import dump, load
from Game import GameMode
from client import Client
import pygame
from time import time
from cProfile import run


class UI:  # Class asks user to choose preferred UI and initialises it
    def __init__(self):
        self.__UI_mode = None
        self.__initialize_ui()

    def __initialize_ui(self):
        while self.__UI_mode not in ["t", "g"]:
            self.__UI_mode = input("Enter \'t\' to use terminal or \'g\' to use GUI. ")
        if self.__UI_mode == "t":
            Terminal()
        elif self.__UI_mode == "g":
            GUI()


class Terminal:  # Class implements terminal version of the UI
    def __init__(self):
        self.__Game = None
        self.__players = {"B": "Black", "W": "White"}
        self.__run()

    def __run(self):  # Main game loop
        quit_game = False
        while not quit_game:  # Game is run unless user wants to quit
            game_decision = input("Enter q to quit, l to load most recent game, or any other character to play. ")
            if game_decision == "q":
                quit_game = True
            else:
                ai_flip_flag = False
                if game_decision == "l":  # Loading game from a file
                    self.__load_game_state()
                    if self.__Game is None:
                        print("Game cannot be loaded.")
                        continue
                else:
                    self.__Game = GameMode()  # Group A skill, OOP Composition
                    ai_status = self.__get_ai_status()
                    if ai_status:
                        if ai_status == 2:
                            ai_flip_flag = True
                print()
                print("Player with black pieces goes first.")
                no_moves_flag = False
                while True:  # Main game loop, escape when winner determined or game saved
                    possible_moves = self.__Game.possible_player_moves()
                    if len(possible_moves) == 0:
                        input(f"{self.__players[self.__Game.get_current_player()]} has no moves to make.")
                        if no_moves_flag:
                            win_status = self.__Game.win_status()
                            if win_status == "Draw":
                                print("Game is finished in a draw.")
                            else:
                                print(f"Game is finished, {self.__players[win_status]} won.")
                            break
                        else:
                            no_moves_flag = True
                            self.__Game.play(None)
                    else:
                        no_moves_flag = False
                        if not ai_flip_flag:
                            self.__print_state(possible_moves)
                            move = self.__get_move_from_player(possible_moves)
                            if move is None:
                                self.__store_game_state()
                                print("Game is saved.")
                                break
                            else:
                                self.__Game.play(move)
                        else:
                            self.__print_state(possible_moves)
                            input("AI is thinking. Press Enter to continue. ")
                            move = self.__Game.get_ai_move(possible_moves, 4, float("inf"))
                            self.__Game.play(move)
                        if ai_status:
                            ai_flip_flag = not ai_flip_flag

    def __get_ai_status(self):  # Asks user to decide how many player will play
        number_of_players = -1
        while number_of_players not in [1, 2]:
            try:
                number_of_players = int(input("Enter number of players(1 or 2). "))
            except ValueError:
                print("Value must be an integer, 1 or 2.")
        if number_of_players == 1:
            first_turn = 0
            while first_turn not in [1, 2]:
                try:
                    first_turn = int(input("Enter 1 if you want to go first, enter 2 if you want AI to go first. "))
                except ValueError:
                    print("Value must be an integer, 1 or 2.")
            return first_turn
        else:
            return False

    def __get_move_from_player(self, possible_moves):  # Asks user to input a desired move and checks its validity
        move = [-1, -1]
        move_set = False
        while not move_set:
            try:
                values = input(f"{self.__players[self.__Game.get_current_player()]}, please enter row and column of "
                               f"your move(eg. 4 5), or q to quit. ")
                if values == "q":
                    return None
                for _ in range(0, len(values.split())):
                    move[_] = int(values.split()[_])
                if [move[0] - 1, move[1] - 1] not in possible_moves:
                    print("Your move must be in possible moves category.")
                    print()
                else:
                    move_set = True
            except ValueError:
                print("You should enter two numbers, each in range from 1 to 8.")
                print()
        return possible_moves.index([move[0] - 1, move[1] - 1])

    def __store_game_state(self):  # Stores game state to a text file
        with open("Last_Game_Save.txt", "wb") as f:
            dump(self.__Game, f)

    def __load_game_state(self):  # Loads game from a text file
        try:
            f = open("Last_Game_Save.txt", "rb")
            self.__Game = load(f)
        except IOError:
            self.__Game = None

    def __print_state(self, possible_moves):  # Prints out a board with pieces into a terminal
        board = self.__Game.get_board()
        print()
        print("  ", end='')
        for col in range(0, 8):
            print(col + 1, end=" ")
        print("\b")
        for row in range(0, 8):
            print(f"{row + 1} ", end='')
            for col in range(0, 8):
                if [row, col] in possible_moves:
                    print(self.__Game.possible_character(), end='|')
                else:
                    print(board[row][col], end='|')
            print("\b")
        print()


class GUI:  # Class provides Graphical User Interface for the game
    # Size and Colour constants
    WINDOW_SIZE = (800, 800)
    DEFAULT_SIZE = 800
    BUTTON_WIDTH = 300
    BUTTON_HEIGHT = 50
    RESIZE_COEFFICIENT = (1, 1)
    BACKGROUND = (165, 0, 7)
    BUTTONS = (100, 0, 7)
    BUTTONS_HOVER = (20, 0, 0)
    TEXT_COLOUR = (0, 165, 158)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Board colours
    GREEN_BOARD = (0, 118, 7)
    FIRST_PLAYER = (0, 0, 0)
    FIRST_PLAYER_PALE = (39, 39, 39)
    SECOND_PLAYER = (255, 255, 255)
    SECOND_PLAYER_PALE = (180, 180, 180)

    QUIT = "Q"
    pygame.font.init()
    USERNAME_FONT = pygame.font.SysFont("Open Sans", 40)
    LOGO_SURFACE = pygame.font.SysFont("Open Sans", 200).render("Othello", False, TEXT_COLOUR)
    BUTTON_FONT = pygame.font.SysFont("Open Sans", 80)

    def __init__(self):  # Initialising PyGame window
        pygame.init()
        self.__screen = pygame.display.set_mode((self.WINDOW_SIZE[0], self.WINDOW_SIZE[1]), pygame.RESIZABLE)
        self.__username_1 = None
        self.__username_2 = None
        self.__run_gui()

    def __run_gui(self):  # Main menu
        # Captions
        pygame.display.set_caption("Othello")
        try:
            icon = pygame.image.load("Othello.png")
            pygame.display.set_icon(icon)
        except FileNotFoundError:
            pass

        # Labels
        labels = ["PLAY", "SIGN IN", "REGISTER", "SETTINGS"]


        # Game Loop
        while True:
            # Update cycle
            mouse_pos = pygame.mouse.get_pos()
            center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            self.__screen.fill(self.BACKGROUND)
            # Logo and button drawing, including hovering
            self.__screen.blit(self.LOGO_SURFACE, ((self.WINDOW_SIZE[0] - self.LOGO_SURFACE.get_rect().width) // 2, 0))
            for index in range(0, len(labels)):
                if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                        initial_y_pos + index * step <= mouse_pos[1] <= initial_y_pos + index * step + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + index * step,
                                                                         self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + index * step,
                                                                   self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                self.__screen.blit(button_surface, ((self.WINDOW_SIZE[0] - button_surface.get_rect().width) // 2,
                                                    initial_y_pos + index * step))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Clicking button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(labels)):
                        if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and initial_y_pos + index * step <= \
                                mouse_pos[1] <= initial_y_pos + index * step + self.BUTTON_HEIGHT:
                            if index == 0:
                                self.__run_play_menu()
                            elif index == 1:
                                self.__sign_in_menu(False)
                            elif index == 2:
                                self.__sign_in_menu(True)
                            else:
                                self.__settings()
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __sign_in_menu(self, register):
        try:
            client = Client()
        except Exception:
            self.__show_message("Server Unavailable", True)
            return None
        labels = ["Username", "Password"]
        select_labels = ["Player 1", "Player 2"]
        active_input_field_flag = -1
        user_input = ["", ""]
        inner_square = 40
        outer_square = 50
        black = (0, 0, 0)
        green = (0, 246, 22)
        pale_green = (0, 123, 11)
        chosen_player = 0

        while True:
            # Update cycle
            mouse_pos = pygame.mouse.get_pos()
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = 2 * self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
            back_pos = [center - self.BUTTON_WIDTH * 0.55, initial_y_pos + 2.7 * step]
            confirm_pos = [center + self.BUTTON_WIDTH * 0.55, initial_y_pos + 2.7 * step]
            player_select_pos = [[center - self.BUTTON_WIDTH * 0.55, initial_y_pos + 2.2 * step],
                                 [center + self.BUTTON_WIDTH * 0.55, initial_y_pos + 2.2 * step]]
            self.__screen.fill(self.BACKGROUND)
            # Logo and button drawing, including hovering
            self.__screen.blit(self.LOGO_SURFACE, ((self.WINDOW_SIZE[0] - self.LOGO_SURFACE.get_rect().width) // 2, 0))
            for index in range(0, len(labels)):
                text_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                self.__screen.blit(text_surface, ((self.WINDOW_SIZE[0] - text_surface.get_rect().width) // 2,
                                                  initial_y_pos + step * index))
                text_surface = self.BUTTON_FONT.render(user_input[index], False, self.TEXT_COLOUR)
                if text_surface.get_width() > self.BUTTON_WIDTH:
                    button_width_new = text_surface.get_width()
                    center = (self.WINDOW_SIZE[0] - button_width_new) // 2
                else:
                    button_width_new = self.BUTTON_WIDTH
                    center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
                if (center <= mouse_pos[0] <= center + button_width_new and \
                        initial_y_pos + index * step + step // 2 <= mouse_pos[1] \
                        <= initial_y_pos + index * step + step // 2 + self.BUTTON_HEIGHT) or \
                        index == active_input_field_flag:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center,
                                                                         initial_y_pos + index * step + step // 2,
                                                                         button_width_new, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + index * step + step // 2,
                                                                   button_width_new, self.BUTTON_HEIGHT))
                self.__screen.blit(text_surface, ((self.WINDOW_SIZE[0] - text_surface.get_rect().width) // 2,
                                                  initial_y_pos + step * index + step // 2))

            text_surface = self.BUTTON_FONT.render("Back", False, self.TEXT_COLOUR)
            if back_pos[0] <= mouse_pos[0] <= back_pos[0] + self.BUTTON_WIDTH and \
                    back_pos[1]  <= mouse_pos[1] <= back_pos[1] + self.BUTTON_HEIGHT:
                pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                 (back_pos[0], back_pos[1], self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
            else:
                pygame.draw.rect(self.__screen, self.BUTTONS, (back_pos[0], back_pos[1],
                                                               self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
            self.__screen.blit(text_surface,
                               (back_pos[0] + (self.BUTTON_WIDTH - text_surface.get_width()) // 2, back_pos[1]))

            text_surface = self.BUTTON_FONT.render("Confirm", False, self.TEXT_COLOUR)
            if confirm_pos[0] <= mouse_pos[0] <= confirm_pos[0] + self.BUTTON_WIDTH and \
                    confirm_pos[1] <= mouse_pos[1] <= confirm_pos[1] + self.BUTTON_HEIGHT:
                pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                 (confirm_pos[0], confirm_pos[1], self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
            else:
                pygame.draw.rect(self.__screen, self.BUTTONS, (confirm_pos[0], confirm_pos[1],
                                                               self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
            self.__screen.blit(text_surface,
                               (confirm_pos[0] + (self.BUTTON_WIDTH - text_surface.get_width()) // 2, confirm_pos[1]))

            if not register:
                for position in player_select_pos:
                    pygame.draw.rect(self.__screen, black, (position[0], position[1], outer_square, outer_square))
                    player_select_surface = self.BUTTON_FONT.render(select_labels[player_select_pos.index(position)],
                                                                    False, self.TEXT_COLOUR)
                    self.__screen.blit(player_select_surface,
                                       (position[0] + outer_square + 10, position[1]))
                    if position[0] <= mouse_pos[0] <= position[0] + outer_square and \
                            position[1] <= mouse_pos[1] <= position[1] + outer_square:
                        pygame.draw.rect(self.__screen, pale_green, (position[0] + 5, position[1] + 5,
                                                                     inner_square, inner_square))
                pygame.draw.rect(self.__screen, green, (player_select_pos[chosen_player][0] + 5,
                                                        player_select_pos[chosen_player][1] + 5,
                                                        inner_square, inner_square))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Clicking button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(labels)):
                        if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                                initial_y_pos + index * step + step // 2 <= mouse_pos[1] \
                                <= initial_y_pos + index * step + step // 2 + self.BUTTON_HEIGHT:
                            active_input_field_flag = index
                            break
                        else:
                            active_input_field_flag = -1
                    for position in player_select_pos:
                        if position[0] <= mouse_pos[0] <= position[0] + outer_square and \
                        position[1] <= mouse_pos[1] <= position[1] + outer_square:
                            chosen_player = player_select_pos.index(position)
                    if back_pos[0] <= mouse_pos[0] <= back_pos[0] + self.BUTTON_WIDTH and \
                            back_pos[1] <= mouse_pos[1] <= back_pos[1] + self.BUTTON_HEIGHT:
                        return None
                    if confirm_pos[0] <= mouse_pos[0] <= confirm_pos[0] + self.BUTTON_WIDTH and \
                            confirm_pos[1] <= mouse_pos[1] <= confirm_pos[1] + self.BUTTON_HEIGHT:
                        try:
                            client = Client()
                        except Exception:
                            self.__show_message("Server Unavailable", True)
                        if not register:
                            request_result = client.sign_in(user_input[0], user_input[1])
                            if request_result == 1:
                                client = Client()
                                if chosen_player == 1:
                                    self.__username_2 = user_input[0]
                                else:
                                    self.__username_1 = user_input[0]
                                    colours = client.send_colours(self.__username_1)
                                    self.FIRST_PLAYER = colours[0]
                                    self.FIRST_PLAYER_PALE = (colours[0][0] // 2,
                                                              colours[0][1] // 2,
                                                              colours[0][2] // 2)
                                    self.SECOND_PLAYER = colours[1]
                                    self.SECOND_PLAYER_PALE = (colours[1][0] // 2,
                                                               colours[1][1] // 2,
                                                               colours[1][2] // 2)
                                    self.GREEN_BOARD = colours[2]
                                self.__show_message("Success", False)
                                return None
                            elif request_result == 0:
                                self.__show_message("Wrong Password", False)
                                del client
                            elif request_result == -1:
                                self.__show_message("Username Not Found", False)
                                del client
                        else:
                            request_result = client.create_account(user_input[0], user_input[1],
                                                                   (self.FIRST_PLAYER,
                                                                    self.SECOND_PLAYER,
                                                                    self.GREEN_BOARD))
                            if request_result:
                                self.__show_message("Account Created", False)
                                return None
                            else:
                                self.__show_message("Username already exists", False)
                                del client
                elif event.type == pygame.KEYDOWN and active_input_field_flag != -1:
                    if event.key == pygame.K_BACKSPACE:
                        user_input[active_input_field_flag] = user_input[active_input_field_flag][:-1]
                    else:
                        if len(user_input[active_input_field_flag]) < 20:
                            user_input[active_input_field_flag] += event.unicode
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __run_play_menu(self):
        # Menu providing game mode options

        # Update loop
        while True:
            center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            self.__screen.blit(self.LOGO_SURFACE, ((self.WINDOW_SIZE[0] - self.LOGO_SURFACE.get_rect().width) // 2, 0))
            labels = ["Resume", "PvP", "PvAI", "Load", "Back"]
            for index in range(0, len(labels)):
                if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                        initial_y_pos + index * step <= mouse_pos[1] <= initial_y_pos + index * step + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + index * step,
                                                                         self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + index * step,
                                                                   self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                self.__screen.blit(button_surface, ((self.WINDOW_SIZE[0] - button_surface.get_rect().width) // 2,
                                                    initial_y_pos + index * step))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            event_functions = [self.__resume_game, self.__two_player_game, self.__one_player_game,
                               self.__load_database_game]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(labels)):
                        if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and initial_y_pos + index * step <= \
                                mouse_pos[1] <= initial_y_pos + index * step + self.BUTTON_HEIGHT:
                            if index == len(labels) - 1:
                                return None
                            else:
                                event_functions[index]()
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __settings(self):
        labels = ["PLAYER 1 COLOUR", "PLAYER 2 COLOUR", "BOARD COLOUR", "BACK"]

        # Update loop
        while True:
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            button_surface = self.BUTTON_FONT.render(labels[1], False, self.TEXT_COLOUR)
            button_width = button_surface.get_rect().width
            center = (self.WINDOW_SIZE[0] - button_width) // 2

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            self.__screen.blit(self.LOGO_SURFACE, ((self.WINDOW_SIZE[0] - self.LOGO_SURFACE.get_rect().width) // 2, 0))
            for index in range(0, len(labels)):
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                        initial_y_pos + index * step <= mouse_pos[1] <=\
                        initial_y_pos + index * step + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + index * step,
                                                                         button_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + index * step,
                                                                   button_width, self.BUTTON_HEIGHT))
                self.__screen.blit(button_surface, ((self.WINDOW_SIZE[0] - button_surface.get_rect().width) // 2,
                                                    initial_y_pos + index * step))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(labels)):
                        if center <= mouse_pos[0] <= center + button_width and initial_y_pos + index * step <= \
                                mouse_pos[1] <= initial_y_pos + index * step + self.BUTTON_HEIGHT:
                            if index == len(labels) - 1:
                                if self.__username_1 is not None:
                                    try:
                                        client = Client()
                                        client.update_colours(self.__username_1,
                                                              (self.FIRST_PLAYER, self.SECOND_PLAYER, self.GREEN_BOARD))
                                    except Exception:
                                        pass
                                return None
                            else:
                                self.__colour_picker(index)
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __colour_picker(self, player_or_board):
        labels = ["RED", "GREEN", "BLUE", "BACK"]
        input_position = 0
        if player_or_board == 0:
            new_colour = [self.FIRST_PLAYER[0], self.FIRST_PLAYER[1], self.FIRST_PLAYER[2]]
        elif player_or_board == 1:
            new_colour = [self.SECOND_PLAYER[0], self.SECOND_PLAYER[1], self.SECOND_PLAYER[2]]
        else:
            new_colour = [self.GREEN_BOARD[0], self.GREEN_BOARD[1], self.GREEN_BOARD[2]]

        for index in range(0, len(new_colour)):
            new_colour[index] = str(new_colour[index])

        # Update loop
        while True:
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + 1.5 * self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
            piece_radius = 50

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            converted_colour = [0, 0, 0]
            for index in range(0, len(new_colour)):
                if new_colour[index] != "":
                    converted_colour[index] = min(255, int(new_colour[index]))
            converted_colour = (converted_colour[0], converted_colour[1], converted_colour[2])
            pygame.draw.circle(self.__screen, converted_colour,
                               (self.WINDOW_SIZE[0] // 2, initial_y_pos - step * 0.6), piece_radius)

            for index in range(0, len(labels)):
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                        initial_y_pos + index * step + step * 0.5 <= mouse_pos[1] <= \
                        initial_y_pos + index * step + step * 0.5 + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + index * step + step * 0.5,
                                                                         self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + index * step + step * 0.5,
                                                                   self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
                if index < len(labels) - 1:
                    value_surface = self.BUTTON_FONT.render(str(new_colour[index]), False, self.TEXT_COLOUR)
                    self.__screen.blit(value_surface, ((self.WINDOW_SIZE[0] - value_surface.get_rect().width) // 2,
                                                        initial_y_pos + index * step + step * 0.5))
                if index < len(labels) - 1:
                    self.__screen.blit(button_surface, ((self.WINDOW_SIZE[0] - button_surface.get_rect().width) // 2,
                                                        initial_y_pos + index * step))
                else:
                    self.__screen.blit(button_surface, ((self.WINDOW_SIZE[0] - button_surface.get_rect().width) // 2,
                                                        initial_y_pos + index * step + step * 0.5))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(labels)):
                        if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and initial_y_pos + index * step + \
                                step * 0.5 <= mouse_pos[1] <= initial_y_pos + index * step \
                                + step  * 0.5 + self.BUTTON_HEIGHT:
                            if index == len(labels) - 1:
                                if player_or_board == 0:
                                    self.FIRST_PLAYER = converted_colour
                                    self.FIRST_PLAYER_PALE = (converted_colour[0] // 2,
                                                              converted_colour[1] // 2,
                                                              converted_colour[2] // 2)
                                elif player_or_board == 1:
                                    self.SECOND_PLAYER = converted_colour
                                    self.SECOND_PLAYER_PALE = (converted_colour[0] // 2,
                                                               converted_colour[1] // 2,
                                                               converted_colour[2] // 2)
                                else:
                                    self.GREEN_BOARD = converted_colour
                                return None
                            else:
                                input_position = index
                # Key input
                elif event.type == pygame.KEYDOWN:
                    try:
                        if event.key == pygame.K_BACKSPACE:
                            new_colour[input_position] = ""
                        else:
                            if len(str(new_colour[input_position])) < 3:
                                new_colour[input_position] += str(int(event.unicode))
                    except Exception:
                        pass
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __display_game_board(self, board, possible_moves, current_player, characters, counters, timers,
                             win_status, ai_status, ai_turn):  # Displaying game board and retrieving user input

        # Main loop
        while True:
            board_side = 600 * min(self.RESIZE_COEFFICIENT)
            initial_pos_x = (self.WINDOW_SIZE[0] - board_side) // 2
            initial_pos_y = (self.WINDOW_SIZE[1] - board_side) // 2
            step_in_pixels = 75 * min(self.RESIZE_COEFFICIENT)
            piece_radius = 34 * min(self.RESIZE_COEFFICIENT)
            offset_x = initial_pos_x + (step_in_pixels / 2)
            offset_y = initial_pos_y + (step_in_pixels / 2)

            # Counter constants
            counter_font = pygame.font.SysFont("Open Sans", int(50 * min(self.RESIZE_COEFFICIENT)))
            black_count_surface = counter_font.render(f"X{counters[0]}", False, self.FIRST_PLAYER)
            white_count_surface = counter_font.render(f"X{counters[1]}", False, self.SECOND_PLAYER)

            # AI constants
            ai_font = pygame.font.SysFont("Open Sans", int(80 * min(self.RESIZE_COEFFICIENT)))
            ai_message = ai_font.render("Calculating...", False, self.BLACK)
            ai_box_x = ai_message.get_rect().width + 100
            ai_box_y = ai_message.get_rect().height + 40
            ai_box_pos_x = (self.WINDOW_SIZE[0] - ai_box_x) / 2
            ai_box_pos_y = (self.WINDOW_SIZE[1] - ai_box_y) / 2

            # Undo constants
            undo_font = pygame.font.SysFont("Open Sans", 50)
            undo_image = undo_font.render("Undo", False, self.BLACK)
            undo_x = offset_x + step_in_pixels * 2 - 23 * min(self.RESIZE_COEFFICIENT)
            undo_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            # Quit constants
            quit_image = undo_font.render("Quit", False, self.BLACK)
            quit_x = offset_x + step_in_pixels * 5 - 23 * min(self.RESIZE_COEFFICIENT)
            quit_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            pygame.draw.rect(self.__screen, self.GREEN_BOARD, (initial_pos_x, initial_pos_y, board_side, board_side))
            for index in range(0, 9):
                pygame.draw.line(self.__screen, self.FIRST_PLAYER, (initial_pos_x, initial_pos_y + step_in_pixels * index),
                                 (initial_pos_x + board_side, initial_pos_y + step_in_pixels * index))
                pygame.draw.line(self.__screen, self.FIRST_PLAYER, (initial_pos_x + step_in_pixels * index, initial_pos_y),
                                 (initial_pos_x + step_in_pixels * index, initial_pos_y + board_side))
            for row in range(0, 8):
                for col in range(0, 8):
                    if board[row][col] == characters[0]:
                        pygame.draw.circle(self.__screen, self.FIRST_PLAYER, (offset_x + step_in_pixels * col, offset_y +
                                                                  step_in_pixels * row), piece_radius)
                    elif board[row][col] == characters[1]:
                        pygame.draw.circle(self.__screen, self.SECOND_PLAYER, (offset_x + step_in_pixels * col, offset_y +
                                                                  step_in_pixels * row), piece_radius)

            # Undo button
            if ai_status and timers[0] is None:
                try:
                    undo_image = pygame.image.load("Undo.svg")
                    undo_image = pygame.transform.scale(undo_image, (
                    int(65 * min(self.RESIZE_COEFFICIENT)), int(65 * min(self.RESIZE_COEFFICIENT))))
                except FileNotFoundError:
                    pass
                self.__screen.blit(undo_image, (undo_x, undo_y))

            # Qut button
            try:
                quit_image = pygame.image.load("Quit.svg")
                quit_image = pygame.transform.scale(quit_image, (
                int(50 * min(self.RESIZE_COEFFICIENT)), int(50 * min(self.RESIZE_COEFFICIENT))))
            except FileNotFoundError:
                pass
            self.__screen.blit(quit_image, (quit_x, quit_y))

            # Piece counters
            pygame.draw.circle(self.__screen, self.FIRST_PLAYER, (offset_x, offset_y + step_in_pixels * 8), piece_radius)
            self.__screen.blit(black_count_surface, (offset_x + step_in_pixels - 35 * min(self.RESIZE_COEFFICIENT),
                                                     offset_y + step_in_pixels * 8 - 15 * min(self.RESIZE_COEFFICIENT)))
            pygame.draw.circle(self.__screen, self.SECOND_PLAYER, (offset_x + step_in_pixels * 6, offset_y + step_in_pixels * 8),
                               piece_radius)
            self.__screen.blit(white_count_surface, (offset_x + step_in_pixels * 7 - 35 * min(self.RESIZE_COEFFICIENT),
                                                     offset_y + step_in_pixels * 8 - 15 * min(self.RESIZE_COEFFICIENT)))

            # Timers
            if timers[0] is not None:
                black_timer = timers[0]
                white_timer = timers[1]
                if current_player == characters[0]:
                    black_timer = timers[0] - (int(time()) - timers[2])
                else:
                    white_timer = timers[1] - (int(time()) - timers[2])
                if black_timer <= 0:
                    black_timer_text = f"0:00"
                else:
                    black_timer_text = f"{black_timer // 60}:"
                    if black_timer % 60 < 10:
                        black_timer_text += f"0"
                    black_timer_text += f"{black_timer % 60}"
                if white_timer <= 0:
                    white_timer_text = f"0:00"
                else:
                    white_timer_text = f"{white_timer // 60}:"
                    if white_timer % 60 < 10:
                        white_timer_text += f"0"
                    white_timer_text += f"{white_timer % 60}"
                black_timer_surface = counter_font.render(black_timer_text, False, self.FIRST_PLAYER)
                white_timer_surface = counter_font.render(white_timer_text, False, self.SECOND_PLAYER)
                pygame.draw.circle(self.__screen, self.FIRST_PLAYER, (offset_x, offset_y - step_in_pixels), piece_radius)
                self.__screen.blit(black_timer_surface, (offset_x + step_in_pixels - 35 * min(self.RESIZE_COEFFICIENT),
                                                         offset_y - step_in_pixels - 15 * min(self.RESIZE_COEFFICIENT)))
                pygame.draw.circle(self.__screen, self.SECOND_PLAYER, (offset_x + step_in_pixels * 6, offset_y - step_in_pixels),
                                   piece_radius)
                self.__screen.blit(white_timer_surface, (offset_x +
                                                         step_in_pixels * 7 - 35 * min(self.RESIZE_COEFFICIENT),
                                                         offset_y - step_in_pixels - 15 * min(self.RESIZE_COEFFICIENT)))

            if win_status is not None:
                if win_status == "Draw":
                    message = win_status
                else:
                    message = f"{win_status} won"
                self.__show_message(message, False)
                return None
            else:
                if len(possible_moves) == 0:
                    self.__show_message("No moves", False)
                    return None
                else:
                    for move in possible_moves:
                        if (mouse_pos[0] - (offset_x + step_in_pixels * move[1])) ** 2\
                                + (mouse_pos[1] - (offset_y + step_in_pixels * move[0])) ** 2 <= piece_radius ** 2:
                            if current_player == characters[0]:
                                pygame.draw.circle(self.__screen, self.FIRST_PLAYER_PALE,
                                                   (offset_x + step_in_pixels * move[1],
                                                    offset_y + step_in_pixels * move[0]), piece_radius)
                            else:
                                pygame.draw.circle(self.__screen, self.SECOND_PLAYER_PALE, (offset_x + step_in_pixels * move[1],
                                                                               offset_y + step_in_pixels * move[0]),
                                                   piece_radius)
                        else:
                            pygame.draw.circle(self.__screen, self.FIRST_PLAYER, (offset_x + step_in_pixels * move[1], offset_y +
                                                                      step_in_pixels * move[0]), piece_radius, 1)
                            pygame.draw.circle(self.__screen, self.FIRST_PLAYER, (offset_x + step_in_pixels * move[1], offset_y +
                                                                      step_in_pixels * move[0]), piece_radius - 5, 1)

            # AI message
            if ai_turn:
                pygame.draw.rect(self.__screen, self.BACKGROUND, (ai_box_pos_x, ai_box_pos_y, ai_box_x, ai_box_y))
                self.__screen.blit(ai_message, ((self.WINDOW_SIZE[0] - ai_message.get_rect().width) / 2,
                                                (self.WINDOW_SIZE[1] - ai_message.get_rect().height) / 2))
                pygame.display.update()
                return None

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for move in possible_moves:
                        if (mouse_pos[0] - (offset_x + step_in_pixels * move[1])) ** 2 + \
                                (mouse_pos[1] - (offset_y + step_in_pixels * move[0])) ** 2 <= piece_radius ** 2:
                            return possible_moves.index(move)
                    if ai_status and undo_x <= mouse_pos[0] <= undo_x + undo_image.get_rect().width and \
                            undo_y <= mouse_pos[1] <= undo_y + undo_image.get_rect().height and timers[0] is None:
                        return -1
                    elif quit_x <= mouse_pos[0] <= quit_x + quit_image.get_rect().width and \
                            quit_y <= mouse_pos[1] <= quit_y + quit_image.get_rect().height:
                        return self.QUIT
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

            # Timer check
            if timers[0] is not None and (black_timer <= 0 or white_timer <= 0):
                return None

    def __show_usernames(self):
        # Username display
        usernames = []
        for username in [self.__username_1, self.__username_2]:
            if username is None:
                usernames.append("Not signed in")
            else:
                usernames.append(username)

        for index in range(0, len(usernames)):
            username_surface = self.USERNAME_FONT.render(f"Player {index + 1}: {usernames[index]}",
                                                         False, self.TEXT_COLOUR)
            self.__screen.blit(username_surface, (0, self.WINDOW_SIZE[1] -
                                                  username_surface.get_rect().height * (len(usernames) - index)))

    def __show_message(self, text, fill):  # Shows a pop up message on the screen
        message_colour = (194, 0, 0)
        box_colour = (0, 0, 0)
        message_font = pygame.font.SysFont("Open Sans", 80)
        message_surface = message_font.render(text, False, message_colour)
        message_box_x = message_surface.get_rect().width + 70
        message_box_y = message_surface.get_rect().height + 40

        while True:
            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return None
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

            # Message
            if fill:
                self.__screen.fill(self.BACKGROUND)
            pygame.draw.rect(self.__screen, box_colour, (
            (self.WINDOW_SIZE[0] - message_box_x) / 2, (self.WINDOW_SIZE[1] - message_box_y) / 2, message_box_x,
            message_box_y))
            self.__screen.blit(message_surface, ((self.WINDOW_SIZE[0] - message_surface.get_rect().width) / 2,
                                                 (self.WINDOW_SIZE[1] - message_surface.get_rect().height) / 2))
            pygame.display.update()

    def __game_cycle(self, game, timer, ai_status, player_is_first, ai_difficulty):  # Main game cycle
        timers = [timer, timer]
        character_relation = {game.characters()[0]: "Black", game.characters()[1]: "White", "Draw": "Draw"}
        no_moves_flag = False
        ai_flip_flag = not player_is_first
        while True:
            possible_moves = game.possible_player_moves()
            if len(possible_moves) == 0:
                if no_moves_flag:
                    # No moves, game ends
                    self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(),
                                              game.characters(), game.get_number_of_pieces(),
                                              [timers[0], timers[1], start_time], character_relation[game.win_status()],
                                              ai_status, ai_flip_flag)
                    break
                else:
                    no_moves_flag = True
                    game.play(None)
            else:
                no_moves_flag = False
                # check for AI turn
                if not ai_flip_flag:
                    start_time = int(time())
                    move = self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(),
                                                     game.characters(), game.get_number_of_pieces(),
                                                     [timers[0], timers[1], start_time], None, ai_status, ai_flip_flag)
                    if timers[0] is not None:
                        if game.get_current_player() == game.characters()[0]:
                            timers[0] -= (int(time()) - start_time)
                        else:
                            timers[1] -= (int(time()) - start_time)
                        if timers[0] <= 0:
                            self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(),
                                                      game.characters(), game.get_number_of_pieces(),
                                                      [timers[0], timers[1], start_time],
                                                      character_relation[game.characters()[1]], ai_status, ai_flip_flag)
                            break
                        elif timers[1] <= 0:
                            self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(),
                                                      game.characters(), game.get_number_of_pieces(),
                                                      [timers[0], timers[1], start_time],
                                                      character_relation[game.characters()[0]], ai_status, ai_flip_flag)
                            break
                    if move == self.QUIT:
                        return None
                    elif move == -1:
                        # Undo move
                        game.undo_move()
                        game.undo_move()
                        ai_flip_flag = not ai_flip_flag
                    else:
                        game.play(move)
                else:
                    # AI move
                    start_time = int(time())
                    self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(),
                                              game.characters(), game.get_number_of_pieces(),
                                              [timers[0], timers[1], start_time], None, ai_status, ai_flip_flag)
                    if timers[0] is not None:
                        move = game.get_ai_move(possible_moves, ai_difficulty * 2 + 1, timers[player_is_first])
                        timers[player_is_first] -= (int(time()) - start_time)
                    else:
                        move = game.get_ai_move(possible_moves, ai_difficulty * 2 + 1, float("inf"))
                    game.play(move)
                if ai_status:
                    # Enabling change of terns between the player and AI
                    ai_flip_flag = not ai_flip_flag


    def __resume_game(self):  # Load game from file
        try:
            f = open("Last_Game_Save.txt", "rb")
            game = load(f)
            self.__game_cycle(game)
        except IOError:
            self.__show_message("Game cannot be loaded", True)

    def __two_player_game(self):  # 2 player game menu
        # Colours and Sizes
        timer = 300
        timer_flag = False
        black = (0, 0, 0)
        green = (0, 246, 22)
        pale_green = (0, 123, 11)
        time_text_font = pygame.font.SysFont("Open Sans", 90)
        check_box_surface = time_text_font.render("Timer Enabled", False, black)
        outer_box_size = 50
        inner_box_size = 40
        timer_font = pygame.font.SysFont("Open Sans", 150)
        start_font = pygame.font.SysFont("Open Sans", 100)
        start_colour = (0, 165, 158)
        start_surface = start_font.render("Start", False, start_colour, self.BACKGROUND)
        back_surface = start_font.render("Back", False, start_colour, self.BACKGROUND)

        while True:
            # Text setup
            text_pos_x = (self.WINDOW_SIZE[0] - check_box_surface.get_rect().width) / 2 + 50
            text_pos_y = (self.WINDOW_SIZE[1] - check_box_surface.get_rect().height) / 2 - 150
            box_pos_x = text_pos_x - 70
            box_pos_y = text_pos_y
            start_button_pos_x = text_pos_x + 300
            start_button_pos_y = text_pos_y + 300
            back_button_pos_x = start_button_pos_x - 430
            back_button_pos_y = start_button_pos_y

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            self.__screen.blit(check_box_surface, (text_pos_x, text_pos_y))
            pygame.draw.rect(self.__screen, black, (box_pos_x, box_pos_y, outer_box_size, outer_box_size))
            pygame.draw.rect(self.__screen, black, (start_button_pos_x, start_button_pos_y,
                                                    start_surface.get_rect().width, start_surface.get_rect().height))
            self.__screen.blit(start_surface, (start_button_pos_x, start_button_pos_y))
            pygame.draw.rect(self.__screen, black, (back_button_pos_x, back_button_pos_y,
                                                    back_surface.get_rect().width, back_surface.get_rect().height))
            self.__screen.blit(back_surface, (back_button_pos_x, back_button_pos_y))
            # Timer setup
            if timer_flag:
                pygame.draw.rect(self.__screen, green, (box_pos_x + 5, box_pos_y + 5, inner_box_size, inner_box_size))
                timer_text = f""
                if timer // 60 < 10:
                    timer_text = f"0"
                timer_text += f"{timer // 60}:"
                if timer % 60 < 10:
                    timer_text += f"0"
                timer_text += f"{timer % 60}"
                timer_surface = timer_font.render(timer_text, False, black)
                self.__screen.blit(timer_surface, ((self.WINDOW_SIZE[0] - timer_surface.get_rect().width) // 2,
                                                   (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 10))
                initial_triangle_x = (self.WINDOW_SIZE[0] - timer_surface.get_rect().width) // 2
                initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 5
                step = 68
                offset = 150
                # Timer buttons
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index, initial_triangle_y),
                                        (initial_triangle_x + step * index + 52, initial_triangle_y),
                                         (initial_triangle_x + step * index + 26, initial_triangle_y - 45)))
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index + offset, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 52, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 26, initial_triangle_y - 45)))
                initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 117
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index, initial_triangle_y),
                                         (initial_triangle_x + step * index + 52, initial_triangle_y),
                                         (initial_triangle_x + step * index + 26, initial_triangle_y + 45)))
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index + offset, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 52, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 26, initial_triangle_y + 45)))
            else:
                if box_pos_x <= mouse_pos[0] <= box_pos_x + outer_box_size and \
                        box_pos_y <= mouse_pos[1] <= box_pos_y + outer_box_size:
                    pygame.draw.rect(self.__screen, pale_green, (box_pos_x + 5, box_pos_y + 5,
                                                                 inner_box_size, inner_box_size))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if box_pos_x <= mouse_pos[0] <= box_pos_x + outer_box_size and \
                            box_pos_y <= mouse_pos[1] <= box_pos_y + outer_box_size:
                        timer_flag = not timer_flag
                    elif back_button_pos_x <= mouse_pos[0] <= back_button_pos_x + back_surface.get_rect().width and\
                            back_button_pos_y <= mouse_pos[1] <= back_button_pos_y + back_surface.get_rect().height:
                        return None
                    elif start_button_pos_x <= mouse_pos[0] <= start_button_pos_x + start_surface.get_rect().width and\
                            start_button_pos_y <= mouse_pos[1] <= start_button_pos_y + start_surface.get_rect().height:
                        game = GameMode()
                        if timer_flag:
                            self.__game_cycle(game, timer, False, True, None)
                        else:
                            self.__game_cycle(game, None, False, True, None)
                        return None
                    # Timer buttons
                    elif timer_flag and self.__screen.get_at(mouse_pos) == (black[0], black[1], black[2], 255):
                        initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 5
                        for index in range(0, 2):
                            if initial_triangle_x + step * index <= mouse_pos[0] <= \
                                    initial_triangle_x + step * index + 52 and \
                                    initial_triangle_y - 45 <= mouse_pos[1] <= initial_triangle_y:
                                timer += 60 * 10 ** (1 - index)
                        for index in range(0, 2):
                            if initial_triangle_x + step * index + offset <= mouse_pos[0] <= \
                                    initial_triangle_x + step * index + offset + 52 and \
                                    initial_triangle_y - 45 <= mouse_pos[1] <= initial_triangle_y:
                                timer += 10 ** (1 - index)
                        initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 117
                        for index in range(0, 2):
                            if initial_triangle_x + step * index <= mouse_pos[0] <= \
                                    initial_triangle_x + step * index + 52 and \
                                    initial_triangle_y <= mouse_pos[1] <= initial_triangle_y + 45:
                                timer -= 60 * 10 ** (1 - index)
                        for index in range(0, 2):
                            if initial_triangle_x + step * index + offset <= mouse_pos[0] <=\
                                    initial_triangle_x + step * index + offset + 52 and \
                                    initial_triangle_y <= mouse_pos[1] <= initial_triangle_y + 45:
                                timer -= 10 ** (1 - index)
                        timer %= 3600
                # Window Resize
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __one_player_game(self):
        # Sizes and Colours
        timer = 300
        timer_flag = False
        player_starts_flag = True
        black = (0, 0, 0)
        green = (0, 246, 22)
        pale_green = (0, 123, 11)
        time_text_font = pygame.font.SysFont("Open Sans", 90)
        timer_check_box_surface = time_text_font.render("Timer Enabled", False, black)
        ai_check_box_surface = time_text_font.render("AI", False, black)
        player_check_box_surface = time_text_font.render("Player", False, black)
        who_starts_surface = time_text_font.render("Who starts?", False, black)
        difficulty_surface = time_text_font.render("Difficulty:", False, black)
        difficulties = ["Easy", "Normal", "Hard"]
        difficulty_value = 1
        outer_box_size = 50
        inner_box_size = 40
        timer_font = pygame.font.SysFont("Open Sans", 150)
        start_font = pygame.font.SysFont("Open Sans", 100)
        start_colour = (0, 165, 158)
        start_surface = start_font.render("Start", False, start_colour, self.BACKGROUND)
        back_surface = start_font.render("Back", False, start_colour, self.BACKGROUND)

        while True:
            # Text and box setup
            timer_text_pos_x = (self.WINDOW_SIZE[0] - timer_check_box_surface.get_rect().width) / 2 + 50
            timer_text_pos_y = (self.WINDOW_SIZE[1] - timer_check_box_surface.get_rect().height) / 2 + 50
            ai_text_pos_x = timer_text_pos_x + 371
            ai_text_pos_y = timer_text_pos_y - 100
            player_text_pos_x = timer_text_pos_x
            player_text_pos_y = timer_text_pos_y - 100
            timer_box_x = timer_text_pos_x - 70
            timer_box_y = timer_text_pos_y
            player_box_x = timer_box_x
            player_box_y = timer_box_y - 100
            ai_box_x = timer_box_x + 371
            ai_box_y = timer_box_y - 100
            who_starts_x = player_box_x
            who_starts_y = player_box_y - 90
            difficulty_x = who_starts_x
            difficulty_y = who_starts_y - 200
            difficulty_labels_x = [difficulty_x - 120, difficulty_x + 100, difficulty_x + 400]
            start_button_pos_x = self.WINDOW_SIZE[0] // 2 + 150
            start_button_pos_y = self.WINDOW_SIZE[1] // 2 + 220
            back_button_pos_x = start_button_pos_x - 465
            back_button_pos_y = start_button_pos_y

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            # Buttons and Checkboxes
            self.__screen.blit(player_check_box_surface, (player_text_pos_x, player_text_pos_y))
            pygame.draw.rect(self.__screen, black, (player_box_x, player_box_y, outer_box_size, outer_box_size))
            self.__screen.blit(ai_check_box_surface, (ai_text_pos_x, ai_text_pos_y))
            pygame.draw.rect(self.__screen, black, (ai_box_x, ai_box_y, outer_box_size, outer_box_size))
            self.__screen.blit(timer_check_box_surface, (timer_text_pos_x, timer_text_pos_y))
            pygame.draw.rect(self.__screen, black, (timer_box_x, timer_box_y, outer_box_size, outer_box_size))
            pygame.draw.rect(self.__screen, black, (start_button_pos_x, start_button_pos_y,
                                                    start_surface.get_rect().width, start_surface.get_rect().height))
            self.__screen.blit(start_surface, (start_button_pos_x, start_button_pos_y))
            pygame.draw.rect(self.__screen, black, (back_button_pos_x, back_button_pos_y,
                                                    back_surface.get_rect().width, back_surface.get_rect().height))
            self.__screen.blit(back_surface, (back_button_pos_x, back_button_pos_y))
            self.__screen.blit(who_starts_surface, (who_starts_x, who_starts_y))
            self.__screen.blit(difficulty_surface, (difficulty_x, difficulty_y))
            for index in range(0, 3):
                # Difficulty setting
                pygame.draw.rect(self.__screen, black, (difficulty_labels_x[index],
                                                        difficulty_y + 100, outer_box_size, outer_box_size))
                self.__screen.blit(time_text_font.render(difficulties[index], False, black),
                                   (difficulty_labels_x[index] + outer_box_size * 1.1, difficulty_y + 100,
                                    outer_box_size, outer_box_size))
                if index == difficulty_value:
                    pygame.draw.rect(self.__screen, green, (difficulty_labels_x[index] + 5, difficulty_y + 100 + 5,
                                                            inner_box_size, inner_box_size))
                if difficulty_labels_x[index] <= mouse_pos[0] <= difficulty_labels_x[index] + outer_box_size and \
                        difficulty_y + 100 <= mouse_pos[1] <= difficulty_y + 100 + outer_box_size and\
                        index != difficulty_value:
                    pygame.draw.rect(self.__screen, pale_green, (difficulty_labels_x[index] + 5, difficulty_y + 100 + 5,
                                                                 inner_box_size, inner_box_size))
            if timer_flag:
                # Timer setup
                pygame.draw.rect(self.__screen, green, (timer_box_x + 5, timer_box_y + 5,
                                                        inner_box_size, inner_box_size))
                timer_text = f""
                if timer // 60 < 10:
                    timer_text = f"0"
                timer_text += f"{timer // 60}:"
                if timer % 60 < 10:
                    timer_text += f"0"
                timer_text += f"{timer % 60}"
                timer_surface = timer_font.render(timer_text, False, black)
                self.__screen.blit(timer_surface, ((self.WINDOW_SIZE[0] - timer_surface.get_rect().width) // 2,
                                                   (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 185))
                initial_triangle_x = (self.WINDOW_SIZE[0] - timer_surface.get_rect().width) // 2
                initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 180
                step = 68
                offset = 150
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index, initial_triangle_y),
                                        (initial_triangle_x + step * index + 52, initial_triangle_y),
                                         (initial_triangle_x + step * index + 26, initial_triangle_y - 45)))
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index + offset, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 52, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 26, initial_triangle_y - 45)))
                initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 292
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index, initial_triangle_y),
                                         (initial_triangle_x + step * index + 52,initial_triangle_y),
                                         (initial_triangle_x + step * index + 26, initial_triangle_y + 45)))
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black,
                                        ((initial_triangle_x + step * index + offset, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 52, initial_triangle_y),
                                         (initial_triangle_x + step * index + offset + 26, initial_triangle_y + 45)))
            else:
                if timer_box_x <= mouse_pos[0] <= timer_box_x + outer_box_size and\
                        timer_box_y <= mouse_pos[1] <= timer_box_y + outer_box_size:
                    pygame.draw.rect(self.__screen, pale_green, (timer_box_x + 5,
                                                                 timer_box_y + 5, inner_box_size, inner_box_size))

            if player_starts_flag:
                pygame.draw.rect(self.__screen, green, (player_box_x + 5, player_box_y + 5,
                                                        inner_box_size, inner_box_size))
                if ai_box_x <= mouse_pos[0] <= ai_box_x + outer_box_size and\
                        ai_box_y <= mouse_pos[1] <= ai_box_y + outer_box_size:
                    pygame.draw.rect(self.__screen, pale_green, (ai_box_x + 5,
                                                                 ai_box_y + 5, inner_box_size, inner_box_size))
            else:
                pygame.draw.rect(self.__screen, green, (ai_box_x + 5, ai_box_y + 5,
                                                        inner_box_size, inner_box_size))
                if player_box_x <= mouse_pos[0] <= player_box_x + outer_box_size and \
                        player_box_y <= mouse_pos[1] <= player_box_y + outer_box_size:
                    pygame.draw.rect(self.__screen, pale_green, (player_box_x + 5,
                                                                 player_box_y + 5, inner_box_size, inner_box_size))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if timer_box_x <= mouse_pos[0] <= timer_box_x + outer_box_size and \
                            timer_box_y <= mouse_pos[1] <= timer_box_y + outer_box_size:
                        timer_flag = not timer_flag
                    elif back_button_pos_x <= mouse_pos[0] <= back_button_pos_x + back_surface.get_rect().width and\
                            back_button_pos_y <= mouse_pos[1] <= back_button_pos_y + back_surface.get_rect().height:
                        return None
                    elif start_button_pos_x <= mouse_pos[0] <= start_button_pos_x + start_surface.get_rect().width and\
                            start_button_pos_y <= mouse_pos[1] <= start_button_pos_y + start_surface.get_rect().height:
                        game = GameMode()
                        if timer_flag:
                            self.__game_cycle(game, timer, True, player_starts_flag, difficulty_value)
                        else:
                            self.__game_cycle(game, None, True, player_starts_flag, difficulty_value)
                        return None
                    elif timer_flag and self.__screen.get_at(mouse_pos) == (black[0], black[1], black[2], 255):
                        # Timer buttons
                        initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 185
                        for index in range(0, 2):
                            if initial_triangle_x + step * index <= mouse_pos[0] <= \
                                    initial_triangle_x + step * index + 52 and initial_triangle_y - 45 <= \
                                    mouse_pos[1] <= initial_triangle_y:
                                timer += 60 * 10 ** (1 - index)
                        for index in range(0, 2):
                            if initial_triangle_x + step * index + offset <= mouse_pos[0] <= \
                                    initial_triangle_x + step * index + offset + 52 and initial_triangle_y - 45 <= \
                                    mouse_pos[1] <= initial_triangle_y:
                                timer += 10 ** (1 - index)
                        initial_triangle_y = (self.WINDOW_SIZE[1] - timer_surface.get_rect().height) // 2 + 292
                        for index in range(0, 2):
                            if initial_triangle_x + step * index <= mouse_pos[0] <= \
                                    initial_triangle_x + step * index + 52 and initial_triangle_y <= \
                                    mouse_pos[1] <= initial_triangle_y + 45:
                                timer -= 60 * 10 ** (1 - index)
                        for index in range(0, 2):
                            if initial_triangle_x + step * index + offset <= \
                                    mouse_pos[0] <= initial_triangle_x + step * index + offset + 52 and \
                                    initial_triangle_y <= mouse_pos[1] <= initial_triangle_y + 45:
                                timer -= 10 ** (1 - index)
                        timer %= 3600
                    if player_starts_flag:
                        if ai_box_x <= mouse_pos[0] <= ai_box_x + outer_box_size and\
                                ai_box_y <= mouse_pos[1] <= ai_box_y + outer_box_size:
                            player_starts_flag = not player_starts_flag
                    else:
                        if player_box_x <= mouse_pos[0] <= player_box_x + outer_box_size and\
                                player_box_y <= mouse_pos[1] <= player_box_y + outer_box_size:
                            player_starts_flag = not player_starts_flag
                    for index in range(0, 3):
                        if difficulty_labels_x[index] <= mouse_pos[0] <=\
                                difficulty_labels_x[index] + outer_box_size and \
                                difficulty_y + 100 <= mouse_pos[1] <= difficulty_y + 100 + outer_box_size and\
                                index != difficulty_value:
                            difficulty_value = index
                # Window Resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __load_database_game(self):
        pass


def main():
    UI()


if __name__ == "__main__":
    main()
    #g = GameMode()
    #run("g.get_ai_move(g.possible_player_moves(), 6, float(\'inf\'