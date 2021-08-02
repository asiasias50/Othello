from pickle import dump, load
from copy import deepcopy


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
        for move in possible_moves:
            board[move[0]][move[1]] = self.__Game.possible_character()
        print()
        print("  ", end='')
        for col in range(0, 8):
            print(col + 1, end=" ")
        print("\b")
        for row in range(0, 8):
            print(f"{row + 1} ", end='')
            for col in range(0, 8):
                print(board[row][col], end='|')
            print("\b")
        print()


class GameMode:
    def __init__(self):
        self.__Board = Board()

    def play(self, move):
        self.__Board.make_a_move(move)

    def possible_player_moves(self):
        return self.__Board.get_possible_moves()

    def possible_character(self):
        return self.__Board.POSSIBLE

    def win_status(self):
        return self.__Board.win_status()

    def get_board(self):
        return self.__Board.get_board()

    def get_current_player(self):
        return self.__Board.get_current_player()

    def get_ai_move(self, possible_moves):
        scores = []
        for move in range(0, len(possible_moves)):
            board = deepcopy(self.__Board)
            board.make_a_move(move)
            scores.append(self.__alpha_beta(board, False, 3, True, float("-inf"), float("inf")))
        return scores.index(min(scores))

    def __alpha_beta(self, game_state, no_moves_flag, depth, minimising_player, alpha, beta):
        new_flag = (len(game_state.get_possible_moves()) == 0)
        if depth == 0 or (new_flag and no_moves_flag):
            return self.__heuristic(game_state, minimising_player)
        else:
            possible_moves = game_state.get_possible_moves()
            if minimising_player:
                result = float("inf")
                for move in range(0, len(possible_moves)):
                    board = deepcopy(game_state)
                    board.make_a_move(move)
                    result = min(result, self.__alpha_beta(board, new_flag, depth - 1, not minimising_player, alpha, beta))
                    if result <= alpha:
                        break
                    beta = min(beta, result)
                return result
            else:
                result = float("-inf")
                for move in range(0, len(possible_moves)):
                    board = deepcopy(game_state)
                    board.make_a_move(move)
                    result = max(result, self.__alpha_beta(board, new_flag, depth - 1, not minimising_player, alpha, beta))
                    if result >= beta:
                        break
                    alpha = max(alpha, result)
                return result


    def __heuristic(self, game_state, minimizing_player):
        heuristic_values = [[4, -3, 2, 2, 2, 2, -3, 4],
                            [-3, -4, -1, -1, -1, -1, -4, -3],
                            [2, -1, 1, 0, 0, 1, -1, 2],
                            [2, -1, 0, 1, 1, 0, -1, 2],
                            [2, -1, 0, 1, 1, 0, -1, 2],
                            [2, -1, 1, 0, 0, 1, -1, 2],
                            [-3, -4, -1, -1, -1, -1, -4, -3],
                            [4, -3, 2, 2, 2, 2, -3, 4]]
        max_value = 0
        min_value = 0
        if minimizing_player:
            min_player = game_state.get_current_player()
            max_player = game_state.opposite()
        else:
            max_player = game_state.get_current_player()
            min_player = game_state.opposite()
        for row in range(0, 8):
            for col in range(0, 8):
                if game_state.get_board()[row][col] == min_player:
                    min_value += heuristic_values[row][col]
                elif game_state.get_board()[row][col] == max_player:
                    max_value += heuristic_values[row][col]
        return max_value - min_value


class Board:
    ALTERNATIVE = "○●＿◎"
    WHITE = "W"
    BLACK = "B"
    EMPTY = "_"
    POSSIBLE = "+"

    def __init__(self):
        self.__grid = []
        for _ in range(8):
            self.__grid.append([Piece(self.EMPTY) for _ in range(8)])
        self.__grid[3][3].flip_to(self.WHITE)
        self.__grid[4][4].flip_to(self.WHITE)
        self.__grid[3][4].flip_to(self.BLACK)
        self.__grid[4][3].flip_to(self.BLACK)
        self.__current_player = self.BLACK
        self.__possible_moves = []
        self.__moves_meta_data = {}

    def get_possible_moves(self):
        self.__moves_meta_data = []
        self.__possible_moves = []
        for row in range(0, 8):
            for col in range(0, 8):
                if self.__grid[row][col].get_character() == self.EMPTY:
                    move_effects = []
                    for row_change in [-1, 0, 1]:
                        for col_change in [-1, 0, 1]:
                            if not (row_change == 0 and col_change == 0):
                                if 0 <= row + row_change < 8 and 0 <= col + col_change < 8 and self.__grid[row + row_change][col + col_change].get_character() == self.opposite():
                                    scale = 2
                                    same_piece_found = False
                                    while 0 <= row + row_change * scale < 8 and 0 <= col + col_change * scale < 8 and self.__grid[row + row_change * scale][col + col_change * scale].get_character() != self.EMPTY and not same_piece_found:
                                        if self.__grid[row + row_change * scale][col + col_change * scale].get_character() == self.__current_player:
                                            same_piece_found = True
                                            break
                                        scale += 1
                                    if same_piece_found:
                                        move_effects.append([row_change, col_change, scale])
                    if len(move_effects) != 0:
                        self.__possible_moves.append([row, col])
                        self.__moves_meta_data.append(move_effects)
        return self.__possible_moves

    def opposite(self):
        if self.__current_player == self.WHITE:
            return self.BLACK
        else:
            return self.WHITE

    def get_current_player(self):
        return self.__current_player

    def make_a_move(self, move):
        if move is not None:
            row = self.__possible_moves[move][0]
            col = self.__possible_moves[move][1]
            self.__grid[row][col].flip_to(self.__current_player)
            for effect in self.__moves_meta_data[move]:
                for scale in range(1, effect[2]):
                    self.__grid[row + effect[0] * scale][col + effect[1] * scale].flip_to(self.__current_player)
        self.__current_player = self.opposite()

    def get_board(self):
        board = []
        for _ in range(8):
            board.append([0 for _ in range(8)])
        for row in range(0, 8):
            for col in range(0, 8):
                board[row][col] = self.__grid[row][col].get_character()
        return board

    def win_status(self):
        black_counter = 0
        white_counter = 0
        for row in range(0, 8):
            for col in range(0, 8):
                if self.__grid[row][col].get_character() == self.BLACK:
                    black_counter += 1
                elif self.__grid[row][col].get_character() == self.WHITE:
                    white_counter += 1
        if black_counter > white_counter:
            return self.BLACK
        elif black_counter == white_counter:
            return "Draw"
        else:
            return self.WHITE


class Piece:
    def __init__(self, character):
        self.__character = character

    def flip_to(self, character):
        self.__character = character

    def get_character(self):
        return self.__character


def main():
    UI()


if __name__ == "__main__":
    main()
