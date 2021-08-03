from pickle import dump, load
from Game import GameMode
import pygame
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
        #pygame.init()
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

    def __resume_game(self):
        print("Hey")

    def __two_player_game(self):
        # Constants
        initial_pos_xy = 100
        board_side = 600
        step_in_pixels = 75
        piece_radius = 34
        green_board = (0, 118, 7)
        black = (0, 0, 0)
        white = (255, 255, 255)

        # Game initialisation
        game = GameMode()
        board = game.get_board()
        possible_moves = game.possible_player_moves()

        while True:
            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pass

            # Update cycle
            pygame.draw.rect(self.__screen, green_board, (initial_pos_xy, initial_pos_xy, board_side, board_side))
            for index in range(0, 9):
                pygame.draw.line(self.__screen, black, (initial_pos_xy, initial_pos_xy + step_in_pixels * index), (initial_pos_xy + board_side, initial_pos_xy + step_in_pixels * index))
                pygame.draw.line(self.__screen, black, (initial_pos_xy + step_in_pixels * index, initial_pos_xy), (initial_pos_xy + step_in_pixels * index, initial_pos_xy + board_side))
            for row in range(0, 8):
                for col in range(0, 8):
                    if board[row][col] == game.black_character():
                        pygame.draw.circle(self.__screen, black, (initial_pos_xy + (step_in_pixels / 2) + step_in_pixels * row, initial_pos_xy + (step_in_pixels / 2) + step_in_pixels * col), piece_radius)
                    elif board[row][col] == game.white_character():
                        pygame.draw.circle(self.__screen, white, (initial_pos_xy + (step_in_pixels / 2) + step_in_pixels * row, initial_pos_xy + (step_in_pixels / 2) + step_in_pixels * col), piece_radius)
            for move in possible_moves:
                pygame.draw.circle(self.__screen, black, (initial_pos_xy + (step_in_pixels / 2) + step_in_pixels * move[0], initial_pos_xy + (step_in_pixels / 2) + step_in_pixels * move[1]), piece_radius, 1)
            pygame.display.update()

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