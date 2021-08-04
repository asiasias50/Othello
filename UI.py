from pickle import dump, load
from Game import GameMode
import pygame
from time import sleep
from cProfile import run


class UI:
    def __init__(self):
        self.__UI_mode = None
        self.__UI = None
        self.__initialize_ui()

    def __initialize_ui(self):
        while self.__UI_mode not in ["t", "g"]:
            self.__UI_mode = input("Enter \'t\' to use terminal or \'g\' to use GUI. ")
        if self.__UI_mode == "t":
            self.__UI = Terminal()
        elif self.__UI_mode == "g":
            self.__UI = GUI()


class Terminal:
    def __init__(self):
        self.__Game = None
        self.__players = {"B": "Black", "W": "White"}
        self.__run()

    def __run(self):
        quit_game = False
        while not quit_game:
            game_decision = input("Enter q to quit, l to load most recent game, or any other character to play. ")
            if game_decision == "q":
                quit_game = True
            else:
                ai_flip_flag = False
                if game_decision == "l":
                    self.__load_game_state()
                    if self.__Game is None:
                        print("Game cannot be loaded.")
                        continue
                else:
                    self.__Game = GameMode()
                    ai_status = self.__get_ai_status()
                    if ai_status:
                        if ai_status == 2:
                            ai_flip_flag = True
                print()
                print("Player with black pieces goes first.")
                no_moves_flag = False
                while True:
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
                            move = self.__Game.get_ai_move(possible_moves)
                            self.__Game.play(move)
                        if ai_status:
                            ai_flip_flag = not ai_flip_flag

    def __get_ai_status(self):
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

    def __get_move_from_player(self, possible_moves):
        move = [-1, -1]
        move_set = False
        while not move_set:
            try:
                values = input(f"{self.__players[self.__Game.get_current_player()]}, please enter row and column of your move(eg. 4 5), or q to quit. ")
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

    def __store_game_state(self):
        with open("Last_Game_Save.txt", "wb") as f:
            dump(self.__Game, f)

    def __load_game_state(self):
        try:
            f = open("Last_Game_Save.txt", "rb")
            self.__Game = load(f)
        except IOError:
            self.__Game = None

    def __print_state(self, possible_moves):
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


class GUI:
    WINDOW_SIZE = 800
    BACKGROUND = (165, 0, 7)
    BUTTONS = (100, 0, 7)
    BUTTONS_HOVER = (20, 0, 0)

    def __init__(self):
        pygame.init()
        self.__screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE))
        self.__run_gui()

    def __run_gui(self):
        # Initialization
        self.__screen.fill(self.BACKGROUND)

        # Captions
        pygame.display.set_caption("Othello")
        try:
            icon = pygame.image.load("Othello.png")
            pygame.display.set_icon(icon)
        except FileNotFoundError:
            pass
        pygame.font.init()
        logo_font = pygame.font.SysFont("Open Sans", 200)
        text_colour = (0, 165, 158)
        logo_surface = logo_font.render("Othello", False, text_colour)
        self.__screen.blit(logo_surface, ((self.WINDOW_SIZE - logo_surface.get_rect().width) // 2, 0))

        # Buttons
        button_font = pygame.font.SysFont("Open Sans", 80)
        button_surface = button_font.render("PLAY", False, text_colour)
        button_width = 300
        button_height = 50
        play_button_pos_x = (self.WINDOW_SIZE - button_width) // 2
        play_button_pos_y = logo_surface.get_rect().height + 50

        # Game Loop
        while True:
            # Events handling
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_pos_x <= mouse_pos[0] <= play_button_pos_x + button_width and play_button_pos_y <= mouse_pos[1] <= play_button_pos_y + button_height:
                        self.__run_play_menu(button_width, button_height, button_font, text_colour)

            # Update cycle
            if play_button_pos_x <= mouse_pos[0] <= play_button_pos_x + button_width and play_button_pos_y <= mouse_pos[1] <= play_button_pos_y + button_height:
                pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (play_button_pos_x, play_button_pos_y, button_width, button_height))
            else:
                pygame.draw.rect(self.__screen, self.BUTTONS, (play_button_pos_x, play_button_pos_y, button_width, button_height))
            self.__screen.blit(button_surface, ((self.WINDOW_SIZE - button_surface.get_rect().width) // 2, play_button_pos_y))
            pygame.display.update()

    def __run_play_menu(self, button_width, button_height, button_font, text_colour):
        center = (self.WINDOW_SIZE - button_width) // 2
        initial_y_pos = 50
        step = 2 * button_height

        while True:
            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Events handling
            event_functions = [self.__resume_game, self.__two_player_game, self.__one_player_game, self.__load_database_game]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, 4):
                        if center <= mouse_pos[0] <= center + button_width and initial_y_pos + index * step <= mouse_pos[1] <= initial_y_pos + index * step + button_height:
                            event_functions[index]()

            # Update cycle
            lables = ["Resume", "PvP", "PvAI", "Load"]
            for index in range(0, 4):
                if center <= mouse_pos[0] <= center + button_width and initial_y_pos + index * step <= mouse_pos[1] <= initial_y_pos + index * step + button_height:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + index * step, button_width, button_height))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + index * step, button_width, button_height))
                button_surface = button_font.render(lables[index], False, text_colour)
                self.__screen.blit(button_surface, ((self.WINDOW_SIZE - button_surface.get_rect().width) // 2, initial_y_pos + index * step))
            pygame.display.update()

    def __display_game_board(self, board, possible_moves, current_player, characters, counters, win_status):
        # Constants
        initial_pos_xy = 100
        board_side = 600
        step_in_pixels = 75
        piece_radius = 34
        green_board = (0, 118, 7)
        black = (0, 0, 0)
        black_pale = (39, 39, 39)
        white = (255, 255, 255)
        white_pale = (180, 180, 180)
        offset = initial_pos_xy + (step_in_pixels / 2)

        # Counter constants
        counter_font = pygame.font.SysFont("Open Sans", 50)
        black_count_surface = counter_font.render(f"X{counters[0]}", False, black)
        white_count_surface = counter_font.render(f"X{counters[1]}", False, white)

        # Main loop
        while True:
            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for move in possible_moves:
                        if (mouse_pos[0] - (offset + step_in_pixels * move[1])) ** 2 + (mouse_pos[1] - (offset + step_in_pixels * move[0])) ** 2 <= piece_radius ** 2:
                            return possible_moves.index(move)

            # Update cycle
            pygame.draw.rect(self.__screen, green_board, (initial_pos_xy, initial_pos_xy, board_side, board_side))
            for index in range(0, 9):
                pygame.draw.line(self.__screen, black, (initial_pos_xy, initial_pos_xy + step_in_pixels * index), (initial_pos_xy + board_side, initial_pos_xy + step_in_pixels * index))
                pygame.draw.line(self.__screen, black, (initial_pos_xy + step_in_pixels * index, initial_pos_xy), (initial_pos_xy + step_in_pixels * index, initial_pos_xy + board_side))
            for row in range(0, 8):
                for col in range(0, 8):
                    if board[row][col] == characters[0]:
                        pygame.draw.circle(self.__screen, black, (offset + step_in_pixels * col, offset + step_in_pixels * row), piece_radius)
                    elif board[row][col] == characters[1]:
                        pygame.draw.circle(self.__screen, white, (offset + step_in_pixels * col, offset + step_in_pixels * row), piece_radius)

            # Piece counters
            pygame.draw.circle(self.__screen, black, (offset, offset + step_in_pixels * 8), piece_radius)
            self.__screen.blit(black_count_surface, (offset + step_in_pixels - 35, offset + step_in_pixels * 8 - 15))
            pygame.draw.circle(self.__screen, white, (offset + step_in_pixels * 6, offset + step_in_pixels * 8), piece_radius)
            self.__screen.blit(white_count_surface, (offset + step_in_pixels * 7 - 35, offset + step_in_pixels * 8 - 15))

            if win_status is not None:
                if win_status == "Draw":
                    message = win_status
                else:
                    message = f"{win_status} won"
                self.__show_message(message)
                return None
            else:
                if len(possible_moves) == 0:
                    self.__show_message("No moves")
                    return None
                else:
                    for move in possible_moves:
                        if (mouse_pos[0] - (offset + step_in_pixels * move[1])) ** 2 + (
                                mouse_pos[1] - (offset + step_in_pixels * move[0])) ** 2 <= piece_radius ** 2:
                            if current_player == characters[0]:
                                pygame.draw.circle(self.__screen, black_pale, (offset + step_in_pixels * move[1], offset + step_in_pixels * move[0]), piece_radius)
                            else:
                                pygame.draw.circle(self.__screen, white_pale, (offset + step_in_pixels * move[1], offset + step_in_pixels * move[0]), piece_radius)
                        else:
                            pygame.draw.circle(self.__screen, black, (offset + step_in_pixels * move[1], offset + step_in_pixels * move[0]), piece_radius, 1)
            pygame.display.update()

    def __show_message(self, text):
        message_colour = (194, 0, 0)
        box_colour = (0, 0, 0)
        message_font = pygame.font.SysFont("Open Sans", 80)
        message_surface = message_font.render(text, False, message_colour)
        message_box_x = message_surface.get_rect().width + 25
        message_box_y = message_surface.get_rect().height + 10

        while True:
            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return None

            # Message
            pygame.draw.rect(self.__screen, box_colour, (
            (self.WINDOW_SIZE - message_box_x) / 2, (self.WINDOW_SIZE - message_box_y) / 2, message_box_x, message_box_y))
            self.__screen.blit(message_surface, ((self.WINDOW_SIZE - message_surface.get_rect().width) / 2, (self.WINDOW_SIZE - message_surface.get_rect().height) / 2))
            pygame.display.update()

    def __game_cycle(self, game):
        no_moves_flag = False
        while True:
            possible_moves = game.possible_player_moves()
            if len(possible_moves) == 0:
                if no_moves_flag:
                    character_relation = {game.characters()[0]: "Black", game.characters()[1]: "White"}
                    self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(), game.characters(), game.get_number_of_pieces(), character_relation[game.win_status()])
                    break
                else:
                    no_moves_flag = True
                    game.play(None)
            else:
                no_moves_flag = False
                move = self.__display_game_board(game.get_board(), possible_moves, game.get_current_player(), game.characters(), game.get_number_of_pieces(), None)
                game.play(move)

    def __resume_game(self):
        try:
            f = open("Last_Game_Save.txt", "rb")
            game = load(f)
            self.__game_cycle(game)
        except IOError:
            self.__show_message("Game cannot be loaded")

    def __two_player_game(self):
        timer = 300
        timer_flag = False
        black = (0, 0, 0)
        green = (0, 246, 22)
        pale_green = (0, 123, 11)
        time_text_font = pygame.font.SysFont("Open Sans", 90)
        check_box_surface = time_text_font.render("Timer Enabled", False, black)
        text_pos_x = (self.WINDOW_SIZE - check_box_surface.get_rect().width) / 2 + 50
        text_pos_y = (self.WINDOW_SIZE - check_box_surface.get_rect().height) / 2 - 150
        box_pos_x = text_pos_x - 70
        box_pos_y = text_pos_y
        outer_box_size = 50
        inner_box_size = 40
        timer_font = pygame.font.SysFont("Open Sans", 150)
        start_font = pygame.font.SysFont("Open Sans", 100)
        start_colour = (0, 165, 158)
        start_surface = start_font.render("Start", False, start_colour)
        start_button_pos_x = 550
        start_button_pos_y = 550

        while True:
            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Update cycle
            self.__screen.blit(check_box_surface, (text_pos_x, text_pos_y))
            pygame.draw.rect(self.__screen, black, (box_pos_x, box_pos_y, outer_box_size, outer_box_size))
            pygame.draw.rect(self.__screen, black, (start_button_pos_x, start_button_pos_y, start_surface.get_rect().width, start_surface.get_rect().height))
            self.__screen.blit(start_surface, (start_button_pos_x, start_button_pos_y))
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
                self.__screen.blit(timer_surface, ((self.WINDOW_SIZE - timer_surface.get_rect().width) // 2, (self.WINDOW_SIZE - timer_surface.get_rect().height) // 2 + 10))
                initial_triangle_x = (self.WINDOW_SIZE - timer_surface.get_rect().width) // 2
                initial_triangle_y = (self.WINDOW_SIZE - timer_surface.get_rect().height) // 2 + 5
                step = 68
                offset = 150
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black, ((initial_triangle_x + step * index, initial_triangle_y), (initial_triangle_x + step * index + 52, initial_triangle_y), (initial_triangle_x + step * index + 26, initial_triangle_y - 45)))
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black, ((initial_triangle_x + step * index + offset, initial_triangle_y), (initial_triangle_x + step * index + offset + 52, initial_triangle_y), (initial_triangle_x + step * index + offset + 26, initial_triangle_y - 45)))
                initial_triangle_y = (self.WINDOW_SIZE - timer_surface.get_rect().height) // 2 + 117
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black, ((initial_triangle_x + step * index, initial_triangle_y), (initial_triangle_x + step * index + 52, initial_triangle_y), (initial_triangle_x + step * index + 26, initial_triangle_y + 45)))
                for index in range(0, 2):
                    pygame.draw.polygon(self.__screen, black, ((initial_triangle_x + step * index + offset, initial_triangle_y), (initial_triangle_x + step * index + offset + 52, initial_triangle_y), (initial_triangle_x + step * index + offset + 26, initial_triangle_y + 45)))
            else:
                if box_pos_x <= mouse_pos[0] <= box_pos_x + outer_box_size and box_pos_y <= mouse_pos[1] <= box_pos_y + outer_box_size:
                    pygame.draw.rect(self.__screen, pale_green, (box_pos_x + 5, box_pos_y + 5, inner_box_size, inner_box_size))
                pygame.draw.rect(self.__screen, pale_green, (box_pos_x + 5, box_pos_y + 5, inner_box_size, inner_box_size))
            pygame.display.update()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if box_pos_x <= mouse_pos[0] <= box_pos_x + outer_box_size and box_pos_y <= mouse_pos[1] <= box_pos_y + outer_box_size:
                        timer_flag = not timer_flag
                    elif start_button_pos_x <= mouse_pos[0] <= start_button_pos_x + start_surface.get_rect().width and start_button_pos_y <= mouse_pos[1] <= start_button_pos_y + start_surface.get_rect().height:
                        game = GameMode()
                        self.__game_cycle(game)
                        return None
                    elif timer_flag and self.__screen.get_at(mouse_pos) == (black[0], black[1], black[2], 255):
                        initial_triangle_y = (self.WINDOW_SIZE - timer_surface.get_rect().height) // 2 + 5
                        for index in range(0, 2):
                            if initial_triangle_x + step * index <= mouse_pos[0] <= initial_triangle_x + step * index + 52 and initial_triangle_y - 45 <= mouse_pos[1] <= initial_triangle_y:
                                timer += 60 * 10 ** (1 - index)
                        for index in range(0, 2):
                            if initial_triangle_x + step * index + offset <= mouse_pos[0] <= initial_triangle_x + step * index + offset + 52 and initial_triangle_y - 45 <= mouse_pos[1] <= initial_triangle_y:
                                timer += 10 ** (1 - index)
                        initial_triangle_y = (self.WINDOW_SIZE - timer_surface.get_rect().height) // 2 + 117
                        for index in range(0, 2):
                            if initial_triangle_x + step * index <= mouse_pos[0] <= initial_triangle_x + step * index + 52 and initial_triangle_y <= mouse_pos[1] <= initial_triangle_y + 45:
                                timer -= 60 * 10 ** (1 - index)
                        for index in range(0, 2):
                            if initial_triangle_x + step * index + offset <= mouse_pos[0] <= initial_triangle_x + step * index + offset + 52 and initial_triangle_y <= mouse_pos[1] <= initial_triangle_y + 45:
                                timer -= 10 ** (1 - index)
                        timer %= 3600

    def __one_player_game(self):
        pass

    def __load_database_game(self):
        pass


def main():
    GUI()


if __name__ == "__main__":
    main()
    # g = GameMode()
    # run("g.get_ai_move(g.possible_player_moves())")