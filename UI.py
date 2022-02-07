from pickle import dump, load
from Game import GameMode, PuzzleMode, CreatorMode
from client import Client
import pygame
from time import time


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
        ##########################
        # Function performs the main control of the game flow
        # providing user will all required information, e.g. game boards,
        # and allows user to input required values
        ##########################
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
                            piece_count = self.__Game.get_number_of_pieces()
                            self.__print_state([], piece_count)
                            win_status = self.__Game.win_status()
                            if win_status == "Draw":
                                print("Game is finished in a draw.")
                            else:
                                print(f"Game is finished, {self.__players[win_status]} won.")
                                print(f"Black has {piece_count[0]} pieces, White has {piece_count[1]} pieces.")
                            break
                        else:
                            no_moves_flag = True
                            self.__Game.play(None)
                    else:
                        no_moves_flag = False
                        if not ai_flip_flag:
                            self.__print_state(possible_moves, self.__Game.get_number_of_pieces())
                            move = self.__get_move_from_player(possible_moves)
                            if move is None:
                                self.__store_game_state()
                                print("Game is saved.")
                                break
                            else:
                                self.__Game.play(move)
                        else:
                            self.__print_state(possible_moves, self.__Game.get_number_of_pieces())
                            input("AI is thinking. Press Enter to continue. ")
                            move = self.__Game.get_ai_move(possible_moves, 4, float("inf"))
                            self.__Game.play(move)
                        if ai_status:
                            ai_flip_flag = not ai_flip_flag

    def __get_ai_status(self):
        ##########################
        # Function asks a user to input a numbers to indicate in which, one or two, player mode will the user play,
        # in addition to indication of who goes first, computer or player. Also, functions verifies the input.
        ##########################
        number_of_players = -1
        while number_of_players not in [1, 2]:
            try:  # Defensive programing
                number_of_players = int(input("Enter number of players(1 or 2). "))
            except ValueError:
                print("Value must be an integer, 1 or 2.")
        if number_of_players == 1:
            first_turn = 0
            while first_turn not in [1, 2]:
                try:  # Defensive programing
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
            try:  # Defensive programing
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
        with open("Last_Game_Save.txt", "wb") as file:
            dump(self.__Game, file)
            ##########################
            # Group B Skills
            # ===========
            # Files, writing
            ##########################

    def __load_game_state(self):  # Loads game from a text file
        try:  # Defensive programing
            file = open("Last_Game_Save.txt", "rb")
            self.__Game = load(file)
            file.close()
        except IOError:
            self.__Game = None
        ##########################
        # Group B Skills
        # ===========
        # Files, reading
        ##########################

    def __print_state(self, possible_moves, piece_count):
        ##########################
        # Function prints the board into the terminal,
        # along side with number of pieces each player has
        ##########################
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
        print(f"Black has {piece_count[0]} pieces, White has {piece_count[1]} pieces.")
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
    BOARD = (0, 118, 7)
    FIRST_PLAYER = (0, 0, 0)
    FIRST_PLAYER_PALE = (39, 39, 39)
    SECOND_PLAYER = (255, 255, 255)
    SECOND_PLAYER_PALE = (180, 180, 180)

    # Text constants
    QUIT = "Q"
    SEE_SOLUTION = "S"
    pygame.font.init()
    OPEN_SANS = "Open Sans"
    SERVER_UNAVAILABLE = "Server unavailable"
    USERNAME_FONT = pygame.font.SysFont(OPEN_SANS, 40)
    LOGO_SURFACE = pygame.font.SysFont(OPEN_SANS, 200).render("Othello", False, TEXT_COLOUR)
    BUTTON_FONT = pygame.font.SysFont(OPEN_SANS, 80)

    def __init__(self):  # Initialising PyGame window
        pygame.init()
        self.__screen = pygame.display.set_mode((self.WINDOW_SIZE[0], self.WINDOW_SIZE[1]), pygame.RESIZABLE)
        self.__username_1 = None
        self.__username_2 = None
        self.__run_gui()

    def __run_gui(self):
        ##########################
        # Function provides a main menu from which the user can navigate
        # to any part of the program, such as Play, Log In, Register, etc.
        ##########################

        # Captions
        pygame.display.set_caption("Othello")
        try:
            icon = pygame.image.load("Othello.png")
            pygame.display.set_icon(icon)
        except FileNotFoundError:
            pass

        # Labels
        labels = ["Play", "Sign In", "Register", "Archive", "Rating", "Settings"]
        ##########################
        # Group C Skills
        # ===========
        # One-dimensional array
        ##########################

        # Main Loop
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
                            elif index == 3:
                                self.__archive()
                            elif index == 4:
                                self.__rating()
                            else:
                                self.__settings()
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __sign_in_menu(self, register):
        ##########################
        # Function allows user to enter their account details and log in,
        # any relevant messages, such as "Incorrect password", etc. are presented by the menu
        ##########################

        try:  # Defensive programing
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
                        try:  # Deffensive programming
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
                                    self.BOARD = colours[2]
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
                                                                    self.BOARD))
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
        ##########################
        # Function provides a game menu, allowing the user
        # to choose in which mode to play, or to solve or create puzzles
        ##########################

        # Update loop
        while True:
            center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            self.__screen.blit(self.LOGO_SURFACE, ((self.WINDOW_SIZE[0] - self.LOGO_SURFACE.get_rect().width) // 2, 0))
            labels = ["PvP", "PvAI", "Load", "Tutorial", "Puzzles", "Back"]
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
            event_functions = [self.__two_player_game, self.__one_player_game,
                               self.__load_database_game, self.__tutorial, self.__puzzle_menu]
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
        ##########################
        # Function provides a menu to choose a piece or a board, the colour of which will be changed.
        ##########################

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
                                    try:  # Defensive programming
                                        client = Client()
                                        client.update_colours(self.__username_1,
                                                              (self.FIRST_PLAYER, self.SECOND_PLAYER, self.BOARD))
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
        ##########################
        # Function allows user to enter 3 values for Red, Green and Blue,
        # to modify the color of previously chosen piece or board. It also displace
        # a piece dynamically to show the user exactly what colour user applying.
        ##########################

        labels = ["RED", "GREEN", "BLUE", "BACK"]
        input_position = 0
        if player_or_board == 0:
            new_colour = [self.FIRST_PLAYER[0], self.FIRST_PLAYER[1], self.FIRST_PLAYER[2]]
        elif player_or_board == 1:
            new_colour = [self.SECOND_PLAYER[0], self.SECOND_PLAYER[1], self.SECOND_PLAYER[2]]
        else:
            new_colour = [self.BOARD[0], self.BOARD[1], self.BOARD[2]]

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
                                    self.BOARD = converted_colour
                                return None
                            else:
                                input_position = index
                # Key input
                elif event.type == pygame.KEYDOWN:
                    try:  # Defensive programming
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
                             win_status, ai_status, ai_turn):
        ##########################
        # Function displays a game board, an 8x8 grid and pieces along with possible moves.
        # Function returns a move chosen by the player. It also displays timers and
        # counters which are updated dynamically.
        ##########################

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
            counter_font = pygame.font.SysFont(self.OPEN_SANS, int(50 * min(self.RESIZE_COEFFICIENT)))
            black_count_surface = counter_font.render(f"X{counters[0]}", False, self.FIRST_PLAYER)
            white_count_surface = counter_font.render(f"X{counters[1]}", False, self.SECOND_PLAYER)

            # AI constants
            ai_font = pygame.font.SysFont(self.OPEN_SANS, int(80 * min(self.RESIZE_COEFFICIENT)))
            ai_message = ai_font.render("Calculating...", False, self.BLACK)
            ai_box_x = ai_message.get_rect().width + 100
            ai_box_y = ai_message.get_rect().height + 40
            ai_box_pos_x = (self.WINDOW_SIZE[0] - ai_box_x) / 2
            ai_box_pos_y = (self.WINDOW_SIZE[1] - ai_box_y) / 2

            # Undo constants
            undo_font = pygame.font.SysFont(self.OPEN_SANS, 50)
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
            pygame.draw.rect(self.__screen, self.BOARD, (initial_pos_x, initial_pos_y, board_side, board_side))
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
        ##########################
        # Function dynamically displays player usernames in left bottom corner of the board.
        ##########################

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

    def __show_message(self, text, fill):
        ##########################
        # Function displays a message on the screen.
        # It can either fill the background or leave it unchanged from the previous action.
        ##########################

        message_colour = (194, 0, 0)
        box_colour = (0, 0, 0)
        message_font = pygame.font.SysFont(self.OPEN_SANS, 80)
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

    def __create_game_name(self):
        ##########################
        # Function allows user to create a game or puzzle name and input it.
        # Created name will be used later on to save the puzzle or game.
        ##########################

        create_name_surface = self.BUTTON_FONT.render("Create name", False, self.TEXT_COLOUR)
        game_name = ""

        while True:
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + 1.6 * self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            self.__screen.blit(create_name_surface,
                               ((self.WINDOW_SIZE[0] - create_name_surface.get_rect().width) // 2,
                                initial_y_pos - step * 0.5))

            button_surface = self.BUTTON_FONT.render(game_name, False, self.TEXT_COLOUR)
            input_width = max(self.BUTTON_WIDTH, button_surface.get_rect().width)
            center = (self.WINDOW_SIZE[0] - input_width) // 2
            if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                    initial_y_pos + step * 0.3 <= mouse_pos[1] <= initial_y_pos + step * 0.3 + self.BUTTON_HEIGHT:
                pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + step * 0.3,
                                                                     input_width, self.BUTTON_HEIGHT))
            else:
                pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + step * 0.3,
                                                               input_width, self.BUTTON_HEIGHT))
            self.__screen.blit(button_surface, ((self.WINDOW_SIZE[0] - button_surface.get_rect().width) // 2,
                                                initial_y_pos + step * 0.3))

            center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
            if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                    initial_y_pos + step <= mouse_pos[1] <= initial_y_pos + step + self.BUTTON_HEIGHT:
                pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + step,
                                                                     self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
            else:
                pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + step,
                                                               self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
            button_surface = self.BUTTON_FONT.render("CONFIRM", False, self.TEXT_COLOUR)
            self.__screen.blit(button_surface, ((self.WINDOW_SIZE[0] - button_surface.get_rect().width) // 2,
                                                initial_y_pos + step))

            self.__show_usernames()

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                            initial_y_pos + step <= mouse_pos[1] <= initial_y_pos + step + self.BUTTON_HEIGHT:
                        if 0 < len(game_name):
                            return game_name
                        else:
                            self.__show_message("Name is too short", False)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        game_name = game_name[:-1]
                    else:
                        if len(game_name) < 20:
                            game_name += event.unicode
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __game_cycle(self, game, timer, ai_status, player_is_first, ai_difficulty, loading="NULL"):  # Main game cycle
        ##########################
        # Function controls the flow of normal game, including decisions on whens to stop the game,
        # updating the game board, requesting input, retrieving AI move, etc. Game can be both created
        # and given to the function or loaded from the database.
        ##########################

        if loading == "NULL":
            timers = [timer, timer]
            no_moves_flag = False
            ai_flip_flag = not player_is_first
        else:
            timers, no_moves_flag, ai_flip_flag, ai_status, ai_difficulty = loading[2]
            game = GameMode()
            game.load(loading[1])
        character_relation = {game.characters()[0]: "Player 1", game.characters()[1]: "Player 2", "Draw": "Draw"}
        while True:
            possible_moves = game.possible_player_moves()
            if len(possible_moves) == 0:
                if no_moves_flag:
                    # No moves, game ends
                    win_status = game.win_status()
                    self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(),
                                              game.characters(), game.get_number_of_pieces(),
                                              [timers[0], timers[1], start_time], character_relation[win_status],
                                              ai_status, ai_flip_flag)
                    win_indexes = {game.characters()[0]: 1, game.characters()[1]: 2, "Draw": 3}
                    try:
                        if loading == "NULL":
                            if (self.__username_1 is not None) and (self.__username_2 is not None or ai_status):
                                client = Client()
                                game_name = self.__create_game_name()
                                if ai_status:
                                    player_2 = "NULL"
                                else:
                                    player_2 = self.__username_2
                                client.save_game(loading, game_name, win_indexes[win_status], self.__username_1,
                                                 player_2, game.get_move_history(),
                                                 (timers, no_moves_flag, ai_flip_flag, ai_status, ai_difficulty))
                                self.__show_message("Game is saved", True)
                                del client
                        else:
                            client = Client()
                            client.save_game(loading[0], None, win_indexes[win_status], None, None,
                                             game.get_move_history(),
                                             (timers, no_moves_flag, ai_flip_flag, ai_status, ai_difficulty))
                            self.__show_message("Game is saved", True)
                            del client
                    except Exception:
                        self.__show_message(self.SERVER_UNAVAILABLE, True)
                    break
                else:
                    no_moves_flag = True
                    self.__show_message(f"{character_relation[game.get_current_player()]} has no moves", False)
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
                        if loading == "NULL":
                            if (self.__username_1 is not None) and (self.__username_2 is not None or ai_status):
                                try:
                                    client = Client()
                                    game_name = self.__create_game_name()
                                    if ai_status:
                                        player_2 = "NULL"
                                    else:
                                        player_2 = self.__username_2
                                    client.save_game(loading, game_name, False, self.__username_1, player_2,
                                                     game.get_move_history(),
                                                     (timers, no_moves_flag, ai_flip_flag, ai_status, ai_difficulty))
                                    self.__show_message("Game is saved", True)
                                except Exception:
                                    self.__show_message(self.SERVER_UNAVAILABLE, True)
                        else:
                            try:
                                client = Client()
                                client.save_game(loading[0], None, False, None, None,
                                                 game.get_move_history(),
                                                 (timers, no_moves_flag, ai_flip_flag, ai_status, ai_difficulty))
                                self.__show_message("Game is saved", True)
                            except Exception:
                                self.__show_message(self.SERVER_UNAVAILABLE, True)
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

    def __two_player_game(self):  # 2 player game menu
        ##########################
        # Function displays a menu, allowing user to enable the
        # timer and specify the time each player has total to make the moves.
        ##########################

        # Colours and Sizes
        timer = 300
        timer_flag = False
        black = (0, 0, 0)
        green = (0, 246, 22)
        pale_green = (0, 123, 11)
        time_text_font = pygame.font.SysFont(self.OPEN_SANS, 90)
        check_box_surface = time_text_font.render("Timer Enabled", False, black)
        outer_box_size = 50
        inner_box_size = 40
        timer_font = pygame.font.SysFont(self.OPEN_SANS, 150)
        start_font = pygame.font.SysFont(self.OPEN_SANS, 100)
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
        ##########################
        # Function displays a menu which allows user to specify the difficulty of the AI player
        # wants to play against, choose who starts player or a computer and enable timer if needed.
        ##########################

        # Sizes and Colours
        timer = 300
        timer_flag = False
        player_starts_flag = True
        black = (0, 0, 0)
        green = (0, 246, 22)
        pale_green = (0, 123, 11)
        time_text_font = pygame.font.SysFont(self.OPEN_SANS, 90)
        timer_check_box_surface = time_text_font.render("Timer Enabled", False, black)
        ai_check_box_surface = time_text_font.render("AI", False, black)
        player_check_box_surface = time_text_font.render("Player", False, black)
        who_starts_surface = time_text_font.render("Who starts?", False, black)
        difficulty_surface = time_text_font.render("Difficulty:", False, black)
        difficulties = ["Easy", "Normal", "Hard"]
        difficulty_value = 1
        outer_box_size = 50
        inner_box_size = 40
        timer_font = pygame.font.SysFont(self.OPEN_SANS, 150)
        start_font = pygame.font.SysFont(self.OPEN_SANS, 100)
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

    def __load_database_game(self, set_of_records=0):
        ##########################
        # Function displays a menu of unfinished games player started,
        # allowing user to chose and click on the game player wants to continue.
        # Each page contains 5 records at most, navigation through pages are done via the buttons
        # Back and Next
        ##########################

        if self.__username_1 is not None:
            try:  # Defensive programming
                client = Client()
                records = client.game_list(self.__username_1, set_of_records, False)
                del client
            except Exception:
                self.__show_message(self.SERVER_UNAVAILABLE, True)
                return None
        else:
            self.__show_message("Log in or Register", True)
            return None

        # Update loop
        columns = ["Game", "Opponent"]
        labels = ["BACK", "MENU", "NEXT"]

        while True:
            initial_y_pos = 100 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            button_width = self.WINDOW_SIZE[0] - 50
            center = (self.WINDOW_SIZE[0] - button_width) // 2

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            button_surface = self.BUTTON_FONT.render(columns[0], False, self.TEXT_COLOUR)
            self.__screen.blit(button_surface, (center, initial_y_pos // 2))
            button_surface = self.BUTTON_FONT.render(columns[1], False, self.TEXT_COLOUR)
            self.__screen.blit(button_surface, (center + button_width // 2, initial_y_pos // 2))
            for index in range(0, len(records)):
                if center <= mouse_pos[0] <= center + button_width and \
                        initial_y_pos + step * index <= mouse_pos[1] <= \
                        initial_y_pos + step * index + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                button_surface = self.BUTTON_FONT.render(records[index][2], False, self.TEXT_COLOUR)
                self.__screen.blit(button_surface, (center, initial_y_pos + step * index))
                button_surface = self.BUTTON_FONT.render(records[index][1], False, self.TEXT_COLOUR)
                self.__screen.blit(button_surface, (center + button_width // 2, initial_y_pos + step * index))
            last_y_pos = initial_y_pos + step * 5

            for index in range(0, len(labels)):
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                extra_buttons_width = button_surface.get_rect().width
                if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                        (button_width // 3) * index + extra_buttons_width and \
                        last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                self.__screen.blit(button_surface, (center + (button_width // 3) * index, last_y_pos))

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(records)):
                        if center <= mouse_pos[0] <= center + button_width and \
                                initial_y_pos + step * index <= mouse_pos[1] <= \
                                initial_y_pos + step * index + self.BUTTON_HEIGHT:
                            if self.__username_2 == records[index][1] or records[index][1] == "AI":
                                client = Client()
                                response = client.retrieve_game(records[index][0])
                                del client
                                response = [records[index][0], response[0], response[1]]
                                self.__game_cycle(None, None, None, None, None, response)
                                return None

                    for index in range(0, len(labels)):
                        button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                        extra_buttons_width = button_surface.get_rect().width
                        if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                                (button_width // 3) * index + extra_buttons_width and \
                                last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                            if index == 0:
                                if set_of_records > 0:
                                    self.__load_database_game(set_of_records - 1)
                                    return None
                            elif index == 2:
                                if len(records) > 0:
                                    self.__load_database_game(set_of_records + 1)
                                    return None
                            elif index == 1:
                                return None
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __archive(self, set_of_records=0, username=None):
        ##########################
        # Function displays a menu of finished games, along with the information whi played these games and who won.
        # By clicking on the particular game, user can review it.
        ##########################

        if self.__username_1 is not None:
            try:  # Defensive programming
                client = Client()
                records = client.archive(set_of_records, username)
                del client
            except Exception:
                self.__show_message(self.SERVER_UNAVAILABLE, True)
                return None
        else:
            self.__show_message("Log in or Register", True)
            return None

        # Update loop
        columns = ["Game", "Player", "Opponent", "Winner"]
        labels = ["BACK", "MENU", "NEXT"]

        while True:
            initial_y_pos = 100 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            button_width = self.WINDOW_SIZE[0] - 50
            center = (self.WINDOW_SIZE[0] - button_width) // 2

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            for index in range(0, len(columns)):
                button_surface = self.BUTTON_FONT.render(columns[index], False, self.TEXT_COLOUR)
                self.__screen.blit(button_surface, (center + index * (button_width // len(columns)),
                                                    initial_y_pos // 2))

            for index in range(0, len(records)):
                if center <= mouse_pos[0] <= center + button_width and \
                        initial_y_pos + step * index <= mouse_pos[1] <= \
                        initial_y_pos + step * index + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                for record_pos in range(0, len(records[index]) - 1):
                    if record_pos == len(records[index]) - 2:
                        message = {1: str(records[index][1]),
                                   2: str(records[index][2]),
                                   3: "Draw"}[records[index][record_pos]]
                    else:
                        message = str(records[index][record_pos])
                    button_surface = self.BUTTON_FONT.render(message, False, self.TEXT_COLOUR)
                    self.__screen.blit(button_surface, (center + record_pos * (button_width // len(columns)),
                                                        initial_y_pos + step * index))
            last_y_pos = initial_y_pos + step * 5

            for index in range(0, len(labels)):
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                extra_buttons_width = button_surface.get_rect().width
                if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                        (button_width // 3) * index + extra_buttons_width and \
                        last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                self.__screen.blit(button_surface, (center + (button_width // 3) * index, last_y_pos))

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(records)):
                        if center <= mouse_pos[0] <= center + button_width and \
                                initial_y_pos + step * index <= mouse_pos[1] <= \
                                initial_y_pos + step * index + self.BUTTON_HEIGHT:
                            try:
                                client = Client()
                                game = client.retrieve_game(records[index][-1])
                                del client
                            except Exception:
                                self.__show_message(self.SERVER_UNAVAILABLE, True)
                            self.__watch_game(game[0])

                    for index in range(0, len(labels)):
                        button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                        extra_buttons_width = button_surface.get_rect().width
                        if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                                (button_width // 3) * index + extra_buttons_width and \
                                last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                            if index == 0:
                                if set_of_records > 0:
                                    self.__archive(set_of_records - 1)
                                    return None
                            elif index == 2:
                                if len(records) > 0:
                                    self.__archive(set_of_records + 1)
                                    return None
                            elif index == 1:
                                return None
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __rating(self, set_of_records=0):
        ##########################
        # Function displays a menu of all registered players along with their statistic of win,
        # loses and total number of played games. The win rate (rating) is also displayed.
        # Player on any record an it will lead to archive page with games only played by chosen user.
        ##########################

        if self.__username_1 is not None:
            try:  # Defensive programming
                client = Client()
                records = client.rating(set_of_records)
                del client
            except Exception:
                self.__show_message(self.SERVER_UNAVAILABLE, True)
                return None
        else:
            self.__show_message("Log in or Register", True)
            return None

        # Update loop
        columns = ["Player", "Wins", "Loses", "Total", "Rating"]
        labels = ["BACK", "MENU", "NEXT"]

        while True:
            initial_y_pos = 100 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            button_width = self.WINDOW_SIZE[0] - 50
            center = (self.WINDOW_SIZE[0] - button_width) // 2

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            for index in range(0, len(columns)):
                button_surface = self.BUTTON_FONT.render(columns[index], False, self.TEXT_COLOUR)
                self.__screen.blit(button_surface, (center + index * (button_width // len(columns)),
                                                    initial_y_pos // 2 - 10))

            for index in range(0, len(records)):
                if center <= mouse_pos[0] <= center + button_width and \
                        initial_y_pos + step * index <= mouse_pos[1] <= \
                        initial_y_pos + step * index + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                values_to_display = [records[index][0], records[index][1], records[index][2] - records[index][1],
                                     records[index][2], records[index][3]]
                for record_pos in range(0, len(values_to_display)):
                    message = str(values_to_display[record_pos])
                    button_surface = self.BUTTON_FONT.render(message, False, self.TEXT_COLOUR)
                    self.__screen.blit(button_surface, (center + record_pos * (button_width // len(columns)),
                                                        initial_y_pos + step * index))
            last_y_pos = initial_y_pos + step * 5

            for index in range(0, len(labels)):
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                extra_buttons_width = button_surface.get_rect().width
                if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                        (button_width // 3) * index + extra_buttons_width and \
                        last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                self.__screen.blit(button_surface, (center + (button_width // 3) * index, last_y_pos))

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(records)):
                        if center <= mouse_pos[0] <= center + button_width and \
                                initial_y_pos + step * index <= mouse_pos[1] <= \
                                initial_y_pos + step * index + self.BUTTON_HEIGHT:
                            self.__archive(username=records[index][0])

                    for index in range(0, len(labels)):
                        button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                        extra_buttons_width = button_surface.get_rect().width
                        if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                                (button_width // 3) * index + extra_buttons_width and \
                                last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                            if index == 0:
                                if set_of_records > 0:
                                    self.__rating(set_of_records - 1)
                                    return None
                            elif index == 2:
                                if len(records) > 0:
                                    self.__rating(set_of_records + 1)
                                    return None
                            elif index == 1:
                                return None
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __watch_game(self, game_sequence):
        ##########################
        # Function controls the flow of game review, by receiving input from the user
        # to either progress to the next move, uno the last move or stop review by quitting.
        ##########################

        move = 0
        game = GameMode()

        response = self.__watch_board_display(game.get_board(), game.get_number_of_pieces(), game.characters())
        while response != self.QUIT:
            if response == -1:
                game.undo_move()
                if move > 0:
                    move -= 1
            elif response == 1:
                if move < len(game_sequence):
                    game.possible_player_moves()
                    game.play(int(game_sequence[move]))
                    move += 1
            response = self.__watch_board_display(game.get_board(), game.get_number_of_pieces(), game.characters())
        return None

    def __watch_board_display(self, board, counters, characters):
        ##########################
        # Function displays a game board, an 8x8 grid and pieces. It allows only to use buttons
        # Undo, Next and Quit, because it is a review of already completed game, and hence it cannot be modified.
        ##########################

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
            counter_font = pygame.font.SysFont(self.OPEN_SANS, int(50 * min(self.RESIZE_COEFFICIENT)))
            black_count_surface = counter_font.render(f"X{counters[0]}", False, self.FIRST_PLAYER)
            white_count_surface = counter_font.render(f"X{counters[1]}", False, self.SECOND_PLAYER)

            # Undo constants
            undo_font = pygame.font.SysFont(self.OPEN_SANS, 50)
            undo_image = undo_font.render("Undo", False, self.BLACK)
            undo_x = offset_x + step_in_pixels * 2 - 23 * min(self.RESIZE_COEFFICIENT)
            undo_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            # Quit constants
            quit_image = undo_font.render("Quit", False, self.BLACK)
            quit_x = offset_x + step_in_pixels * 4 - 23 * min(self.RESIZE_COEFFICIENT)
            quit_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            # Next constants
            next_image = undo_font.render("Next", False, self.BLACK)
            next_x = offset_x + step_in_pixels * 5 - 23 * min(self.RESIZE_COEFFICIENT)
            next_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            pygame.draw.rect(self.__screen, self.BOARD, (initial_pos_x, initial_pos_y, board_side, board_side))
            for index in range(0, 9):
                pygame.draw.line(self.__screen, self.FIRST_PLAYER,
                                 (initial_pos_x, initial_pos_y + step_in_pixels * index),
                                 (initial_pos_x + board_side, initial_pos_y + step_in_pixels * index))
                pygame.draw.line(self.__screen, self.FIRST_PLAYER,
                                 (initial_pos_x + step_in_pixels * index, initial_pos_y),
                                 (initial_pos_x + step_in_pixels * index, initial_pos_y + board_side))
            for row in range(0, 8):
                for col in range(0, 8):
                    if board[row][col] == characters[0]:
                        pygame.draw.circle(self.__screen, self.FIRST_PLAYER,
                                           (offset_x + step_in_pixels * col, offset_y +
                                            step_in_pixels * row), piece_radius)
                    elif board[row][col] == characters[1]:
                        pygame.draw.circle(self.__screen, self.SECOND_PLAYER,
                                           (offset_x + step_in_pixels * col, offset_y +
                                            step_in_pixels * row), piece_radius)

            # Undo button
            try:
                undo_image = pygame.image.load("Undo.svg")
                undo_image = pygame.transform.scale(undo_image, (
                    int(65 * min(self.RESIZE_COEFFICIENT)), int(65 * min(self.RESIZE_COEFFICIENT))))
            except FileNotFoundError:
                pass
            self.__screen.blit(undo_image, (undo_x, undo_y))

            # Quit button
            try:
                quit_image = pygame.image.load("Quit.svg")
                quit_image = pygame.transform.scale(quit_image, (
                    int(50 * min(self.RESIZE_COEFFICIENT)), int(50 * min(self.RESIZE_COEFFICIENT))))
            except FileNotFoundError:
                pass
            self.__screen.blit(quit_image, (quit_x, quit_y))

            # Next button
            try:
                next_image = pygame.image.load("Next.svg")
                next_image = pygame.transform.scale(next_image, (
                    int(50 * min(self.RESIZE_COEFFICIENT)), int(50 * min(self.RESIZE_COEFFICIENT))))
            except FileNotFoundError:
                pass
            self.__screen.blit(next_image, (next_x, next_y))

            # Piece counters
            pygame.draw.circle(self.__screen, self.FIRST_PLAYER, (offset_x, offset_y + step_in_pixels * 8),
                               piece_radius)
            self.__screen.blit(black_count_surface, (offset_x + step_in_pixels - 35 * min(self.RESIZE_COEFFICIENT),
                                                     offset_y + step_in_pixels * 8 - 15 * min(self.RESIZE_COEFFICIENT)))
            pygame.draw.circle(self.__screen, self.SECOND_PLAYER,
                               (offset_x + step_in_pixels * 6, offset_y + step_in_pixels * 8),
                               piece_radius)
            self.__screen.blit(white_count_surface, (offset_x + step_in_pixels * 7 - 35 * min(self.RESIZE_COEFFICIENT),
                                                     offset_y + step_in_pixels * 8 - 15 * min(self.RESIZE_COEFFICIENT)))


            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if quit_x <= mouse_pos[0] <= quit_x + quit_image.get_rect().width and \
                            quit_y <= mouse_pos[1] <= quit_y + quit_image.get_rect().height:
                        return self.QUIT
                    if undo_x <= mouse_pos[0] <= undo_x + undo_image.get_rect().width and \
                            undo_y <= mouse_pos[1] <= undo_y + undo_image.get_rect().height:
                        return -1
                    if next_x <= mouse_pos[0] <= next_x + next_image.get_rect().width and \
                            next_y <= mouse_pos[1] <= next_y + next_image.get_rect().height:
                        return 1
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __tutorial(self):
        ##########################
        # Function provides a simple way for player to learn the game, telling user what to do,
        # and providing some tips to play the game successfully.
        ##########################

        game = GameMode()
        tips = ["Place a piece in available space",
                "Now its opponents go",
                "Game continues until board is filled",
                "Try to capture corners, it is optimal",
                "Good Luck"]

        for index in range(0, len(tips)):
            self.__show_message(tips[index], True)
            if index < len(tips) - 1:
                move = self.__display_game_board(game.get_board(), game.possible_player_moves(),
                                                 game.get_current_player(),
                                                 game.characters(), game.get_number_of_pieces(), [None, None], None,
                                                 False,
                                                 False)
                if move == self.QUIT:
                    return None
                game.play(move)
        return None

    def __puzzle_menu(self):
        ##########################
        # Function displays a menu, allowing user to either select puzzles and start
        # to play a chosen puzzle or select create to create a new puzzle.
        ##########################

        # Update loop
        while True:
            center = (self.WINDOW_SIZE[0] - self.BUTTON_WIDTH) // 2
            initial_y_pos = 110 + 50 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            self.__screen.blit(self.LOGO_SURFACE, ((self.WINDOW_SIZE[0] - self.LOGO_SURFACE.get_rect().width) // 2, 0))
            labels = ["Play", "Create", "Back"]
            for index in range(0, len(labels)):
                if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and \
                        initial_y_pos + index * step <= mouse_pos[1]\
                        <= initial_y_pos + index * step + self.BUTTON_HEIGHT:
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
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(labels)):
                        if center <= mouse_pos[0] <= center + self.BUTTON_WIDTH and initial_y_pos + index * step <= \
                                mouse_pos[1] <= initial_y_pos + index * step + self.BUTTON_HEIGHT:
                            if index == len(labels) - 1:
                                return None
                            else:
                                if index == 0:
                                    self.__puzzle_archive()
                                else:
                                    self.__creator_cycle()
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __puzzle_archive(self, set_of_records=0):
        ##########################
        # Function displays a menu similar to archive, presenting a records
        # of puzzles from the database, user can chose and click on puzzle presented to start playing it
        ##########################

        if self.__username_1 is not None:
            try:  # Defensive programming
                client = Client()
                records = client.retrieve_puzzles(set_of_records)
                del client
            except Exception:
                self.__show_message(self.SERVER_UNAVAILABLE, True)
                return None
        else:
            self.__show_message("Log in or Register", True)
            return None

        # Update loop
        columns = ["Puzzle", "Creator"]
        labels = ["BACK", "MENU", "NEXT"]

        while True:
            initial_y_pos = 100 * self.RESIZE_COEFFICIENT[1]
            step = self.BUTTON_HEIGHT + self.BUTTON_HEIGHT * self.RESIZE_COEFFICIENT[1]
            button_width = self.WINDOW_SIZE[0] - 50
            center = (self.WINDOW_SIZE[0] - button_width) // 2

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            for index in range(0, len(columns)):
                button_surface = self.BUTTON_FONT.render(columns[index], False, self.TEXT_COLOUR)
                self.__screen.blit(button_surface, (center + index * (button_width // len(columns)),
                                                    initial_y_pos // 2))

            for index in range(0, len(records)):
                if center <= mouse_pos[0] <= center + button_width and \
                        initial_y_pos + step * index <= mouse_pos[1] <= \
                        initial_y_pos + step * index + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center, initial_y_pos + step * index, button_width, self.BUTTON_HEIGHT))
                for record_pos in range(0, len(records[index]) - 1):
                    message = str(records[index][record_pos])
                    button_surface = self.BUTTON_FONT.render(message, False, self.TEXT_COLOUR)
                    self.__screen.blit(button_surface, (center + record_pos * (button_width // len(columns)),
                                                        initial_y_pos + step * index))
            last_y_pos = initial_y_pos + step * 5

            for index in range(0, len(labels)):
                button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                extra_buttons_width = button_surface.get_rect().width
                if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                        (button_width // 3) * index + extra_buttons_width and \
                        last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (center + (button_width // 3) * index, last_y_pos,
                                      extra_buttons_width, self.BUTTON_HEIGHT))
                self.__screen.blit(button_surface, (center + (button_width // 3) * index, last_y_pos))

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, len(records)):
                        if center <= mouse_pos[0] <= center + button_width and \
                                initial_y_pos + step * index <= mouse_pos[1] <= \
                                initial_y_pos + step * index + self.BUTTON_HEIGHT:
                            self.__puzzle_cycle(records[index][-1])

                    for index in range(0, len(labels)):
                        button_surface = self.BUTTON_FONT.render(labels[index], False, self.TEXT_COLOUR)
                        extra_buttons_width = button_surface.get_rect().width
                        if center + (button_width // 3) * index <= mouse_pos[0] <= center + \
                                (button_width // 3) * index + extra_buttons_width and \
                                last_y_pos <= mouse_pos[1] <= last_y_pos + self.BUTTON_HEIGHT:
                            if index == 0:
                                if set_of_records > 0:
                                    self.__archive(set_of_records - 1)
                                    return None
                            elif index == 2:
                                if len(records) > 0:
                                    self.__archive(set_of_records + 1)
                                    return None
                            elif index == 1:
                                return None
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __display_puzzle_board(self, board, characters, possible_moves, current_player, creator):
        ##########################
        # Function displays a game board, an 8x8 grid and pieces.
        # It allows user to make a move if player solves a puzzle,
        # and as many moves as needed if user creates the puzzle,
        # with additional access to undo button and See Solution button.
        ##########################

        # Main loop
        while True:
            board_side = 600 * min(self.RESIZE_COEFFICIENT)
            initial_pos_x = (self.WINDOW_SIZE[0] - board_side) // 2
            initial_pos_y = (self.WINDOW_SIZE[1] - board_side) // 2
            step_in_pixels = 75 * min(self.RESIZE_COEFFICIENT)
            piece_radius = 34 * min(self.RESIZE_COEFFICIENT)
            offset_x = initial_pos_x + (step_in_pixels / 2)
            offset_y = initial_pos_y + (step_in_pixels / 2)

            # Undo constants
            undo_font = pygame.font.SysFont(self.OPEN_SANS, 50)
            undo_image = undo_font.render("Undo", False, self.BLACK)
            undo_x = offset_x + step_in_pixels * 0 - 23 * min(self.RESIZE_COEFFICIENT)
            undo_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            # Quit constants
            quit_image = undo_font.render("Quit", False, self.BLACK)
            quit_x = offset_x + step_in_pixels * 7 - 23 * min(self.RESIZE_COEFFICIENT)
            quit_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            # See Solution Button
            see_text = self.BUTTON_FONT.render("See Solution", False, self.TEXT_COLOUR)
            button_width = see_text.get_rect().width
            see_x = (self.WINDOW_SIZE[0] - button_width) // 2
            see_y = offset_y + step_in_pixels * 8 - 23 * min(self.RESIZE_COEFFICIENT)

            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            pygame.draw.rect(self.__screen, self.BOARD, (initial_pos_x, initial_pos_y, board_side, board_side))
            for index in range(0, 9):
                pygame.draw.line(self.__screen, self.FIRST_PLAYER,
                                 (initial_pos_x, initial_pos_y + step_in_pixels * index),
                                 (initial_pos_x + board_side, initial_pos_y + step_in_pixels * index))
                pygame.draw.line(self.__screen, self.FIRST_PLAYER,
                                 (initial_pos_x + step_in_pixels * index, initial_pos_y),
                                 (initial_pos_x + step_in_pixels * index, initial_pos_y + board_side))
            for row in range(0, 8):
                for col in range(0, 8):
                    if board[row][col] == characters[0]:
                        pygame.draw.circle(self.__screen, self.FIRST_PLAYER,
                                           (offset_x + step_in_pixels * col, offset_y +
                                            step_in_pixels * row), piece_radius)
                    elif board[row][col] == characters[1]:
                        pygame.draw.circle(self.__screen, self.SECOND_PLAYER,
                                           (offset_x + step_in_pixels * col, offset_y +
                                            step_in_pixels * row), piece_radius)
            for move in possible_moves:
                if (mouse_pos[0] - (offset_x + step_in_pixels * move[1])) ** 2 \
                        + (mouse_pos[1] - (offset_y + step_in_pixels * move[0])) ** 2 <= piece_radius ** 2:
                    if current_player == characters[0]:
                        pygame.draw.circle(self.__screen, self.FIRST_PLAYER_PALE,
                                           (offset_x + step_in_pixels * move[1],
                                            offset_y + step_in_pixels * move[0]), piece_radius)
                    else:
                        pygame.draw.circle(self.__screen, self.SECOND_PLAYER_PALE, (offset_x + step_in_pixels * move[1],
                                                                                    offset_y + step_in_pixels * move[
                                                                                        0]),
                                           piece_radius)
                else:
                    pygame.draw.circle(self.__screen, self.FIRST_PLAYER,
                                       (offset_x + step_in_pixels * move[1], offset_y +
                                        step_in_pixels * move[0]), piece_radius, 1)
                    pygame.draw.circle(self.__screen, self.FIRST_PLAYER,
                                       (offset_x + step_in_pixels * move[1], offset_y +
                                        step_in_pixels * move[0]), piece_radius - 5, 1)

            # Undo button
            if creator:
                try:
                    undo_image = pygame.image.load("Undo.svg")
                    undo_image = pygame.transform.scale(undo_image, (
                        int(65 * min(self.RESIZE_COEFFICIENT)), int(65 * min(self.RESIZE_COEFFICIENT))))
                except FileNotFoundError:
                    pass
                self.__screen.blit(undo_image, (undo_x, undo_y))

            # Quit button
            try:
                quit_image = pygame.image.load("Quit.svg")
                quit_image = pygame.transform.scale(quit_image, (
                    int(50 * min(self.RESIZE_COEFFICIENT)), int(50 * min(self.RESIZE_COEFFICIENT))))
            except FileNotFoundError:
                pass
            self.__screen.blit(quit_image, (quit_x, quit_y))

            # See Solution Button
            if creator:
                if see_x <= mouse_pos[0] <= see_x + self.BUTTON_WIDTH and \
                        see_y <= mouse_pos[1] <= see_y + self.BUTTON_HEIGHT:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER,
                                     (see_x, see_y, button_width, self.BUTTON_HEIGHT))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS,
                                     (see_x, see_y, button_width, self.BUTTON_HEIGHT))
                self.__screen.blit(see_text, ((self.WINDOW_SIZE[0] - see_text.get_rect().width) // 2, see_y))

            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # Mouse clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if quit_x <= mouse_pos[0] <= quit_x + quit_image.get_rect().width and \
                            quit_y <= mouse_pos[1] <= quit_y + quit_image.get_rect().height:
                        return self.QUIT
                    for move in possible_moves:
                        if (mouse_pos[0] - (offset_x + step_in_pixels * move[1])) ** 2 \
                                + (mouse_pos[1] - (offset_y + step_in_pixels * move[0])) ** 2 <= piece_radius ** 2:
                            return possible_moves.index(move)
                    if creator:
                        if see_x <= mouse_pos[0] <= see_x + self.BUTTON_WIDTH and \
                                see_y <= mouse_pos[1] <= see_y + self.BUTTON_HEIGHT:
                            return self.SEE_SOLUTION
                        if undo_x <= mouse_pos[0] <= undo_x + undo_image.get_rect().width and \
                                undo_y <= mouse_pos[1] <= undo_y + undo_image.get_rect().height:
                            return -1
                # Window resizing
                elif event.type == pygame.VIDEORESIZE:
                    self.WINDOW_SIZE = pygame.display.get_surface().get_size()
                    self.RESIZE_COEFFICIENT = (self.WINDOW_SIZE[0] / self.DEFAULT_SIZE,
                                               self.WINDOW_SIZE[1] / self.DEFAULT_SIZE)

    def __puzzle_cycle(self, sequence):
        ##########################
        # Function controls the flow of the puzzle, allowing user to make one move,
        # presenting them with calculated score and giving them the optimal solution to the puzzle
        ##########################

        puzzle = PuzzleMode(sequence)
        response = self.__display_puzzle_board(puzzle.get_board(), puzzle.get_characters(),
                                               puzzle.possible_moves(), puzzle.get_current_player(), False)
        if response != self.QUIT:
            puzzle.make_move(response)
            self.__show_message(f"Your score is {puzzle.get_score(sequence[-1])}", False)
            self.__show_message(f"Optimal move is", False)
            self.__display_puzzle_board(puzzle.get_board(), puzzle.get_characters(),
                                               [], puzzle.get_current_player(), False)
        return None

    def __creator_cycle(self):
        ##########################
        # Function controls the flow of puzzle creation,
        # allowing user to place as many pieces as needed,
        # undo moves and see optimal solution given by the
        # computer by pressing See Solution
        ##########################

        if self.__username_1 is None:
            self.__show_message("Log in or Register", True)
            return None

        creator = CreatorMode()
        response = 0
        while True:
            response = self.__display_puzzle_board(creator.get_board(), creator.get_characters(),
                                               creator.possible_moves(), creator.get_current_player(), True)
            if response == self.QUIT:
                if len(creator.possible_moves()) == 0:
                    self.__show_message("Puzzle must have a move", False)
                    continue
                try:  # Defensive programming
                    puzzle_name = self.__create_game_name()
                    client = Client()
                    client.create_puzzle(creator.see_solution(), puzzle_name, self.__username_1)
                    del client
                    self.__show_message("Puzzle saved", True)
                except Exception:
                    self.__show_message(self.SERVER_UNAVAILABLE, True)
                break
            elif response == self.SEE_SOLUTION:
                creator.see_solution()
            elif response == -1:
                creator.undo_move()
            else:
                creator.make_move(response)
        return None


def main():
    UI()


if __name__ == "__main__":
    main()
