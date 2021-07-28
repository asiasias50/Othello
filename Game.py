from pickle import dump, load
from copy import deepcopy


class UI:
    def __init__(self):
        self.__UI_mode = None
        self.__UI = None

    def initialize_ui(self):
        while self.__UI_mode not in ["t", "g"]:
            self.__UI_mode = input("Enter \'t\' to use terminal or \'g\' to use GUI. ")
        if self.__UI_mode == "t":
            self.__UI = Terminal()


class Terminal:
    def __init__(self):
        self.__Game = None
        self.__run()

    def __run(self):
        quit_game = False
        while not quit_game:
            game_decision = input("Enter q to quit, l to load most recent game, or any other character to play. ")
            if game_decision == "q":
                quit_game = True
            else:
                if game_decision == "l":
                    self.__load_game_state()
                    if self.__Game is None:
                        print("Game cannot be loaded.")
                        continue
                else:
                    self.__Game = GameMode(self.__initialise_names())
                colours = self.__Game.get_piece_relation()
                print(f"{self.__Game.get_names()[0]} will play with {colours[0]} pieces, {self.__Game.get_names()[1]} will play with {colours[1]} pieces."
                      f" {self.__Game.get_names()[0]} starts.")
                game_finished = False
                win_status = None
                opponents = {self.__Game.get_names()[0]: self.__Game.get_names()[1], self.__Game.get_names()[1]: self.__Game.get_names()[0]}
                while not game_finished:
                    for player in self.__Game.get_names():
                        possible_moves = self.__Game.possible_player_moves(player, opponents[player])
                        if len(possible_moves) == 0:
                            print(f"{player} has no possible moves.")
                            input()
                        else:
                            if not self.__Game.get_ai_status()[self.__Game.get_names().index(player)]:
                                self.__Game.print_state(possible_moves, False)
                                move = self.__get_move_from_player(player, possible_moves)
                                if move is None:
                                    self.__Game.set_player_order([player, opponents[player]])
                                    self.__store_game_state()
                                    game_finished = True
                                    break
                                self.__Game.play(possible_moves[move], player)
                            else:
                                self.__Game.print_state([], True)
                                input(f"{player} is thinking.\nPress Enter to continue. ")
                                self.__Game.play(possible_moves[self.__Game.get_ai_move(possible_moves, player, opponents[player])], player)
                            win_status = self.__Game.win_status(player, opponents[player])
                        if win_status in self.__Game.get_names() or win_status == "Draw":
                            game_finished = True
                            break
                    if win_status == "Draw":
                        print("Game is finished in a draw.")
                    elif win_status in self.__Game.get_names():
                        print(f"Game is finished, {win_status} won.")
                    else:
                        print(f"Game is saved.")

    def __initialise_names(self):
        number_of_players = None
        player_names = []
        while number_of_players is None:
            try:
                number_of_players = int(input("Enter number of players(1 or 2): "))
            except ValueError:
                print("Input should be an integer 1 or 2.")
                print()
                continue
            if number_of_players not in [1, 2]:
                print("Input should be an integer 1 or 2.")
                print()
                number_of_players = None
        if number_of_players == 2:
            for _ in range(1, number_of_players + 1):
                player_names.append(input(f"Enter name of player {_}. "))
            return [player_names, -1]
        else:
            player_names.append(input(f"Enter your name. "))
            player_names.append(input(f"Enter the name your AI should be called. "))
            order = 0
            while order == 0:
                try:
                    order = int(input("Enter 1 if you want to play black pieces and go first,"
                                      " enter 2 if you want to play white pieces and go second.  "))
                except ValueError:
                    print("Input should be an integer 1 or 2.")
                    print()
                    continue
                if order not in [1, 2]:
                    print("Input should be an integer 1 or 2.")
                    print()
                    order = 0
            if order == 2:
                player_names[0], player_names[1] = player_names[1], player_names[0]
                return [player_names, 0]
            else:
                return [player_names, 1]

    def __get_move_from_player(self, player, possible_moves):
        move = [-1, -1]
        possible_coordinates = []
        for coordinate in possible_moves:
            possible_coordinates.append([coordinate[0], coordinate[1]])
        move_set = False
        while not move_set:
            try:
                values = input(f"{player}, please enter row and column of your move(eg. 4 5), or q to quit. ")
                if values == "q":
                    return None
                for _ in range(0, len(values.split())):
                    move[_] = int(values.split()[_])
                if [move[0] - 1, move[1] - 1] not in possible_coordinates:
                    print("Your move must be in possible moves category.")
                    print()
                else:
                    move_set = True
            except ValueError:
                print("You should enter two numbers, each in range from 1 to 8.")
                print()
        return possible_coordinates.index([move[0] - 1, move[1] - 1])

    def __store_game_state(self):
        with open("Last_Game_Save.txt", "wb") as f:
            dump(self.__Game, f)

    def __load_game_state(self):
        try:
            f = open("Last_Game_Save.txt", "rb")
            self.__Game = load(f)
        except IOError:
            self.__Game = None


class GameMode:
    def __init__(self, player_data):
        self.__player_names = player_data[0]
        self.__player_ai_status = [False, False]
        if player_data[1] in [0, 1]:
            self.__player_ai_status[player_data[1]] = True
        self.__Board = Board(self.__player_names)

    def get_names(self):
        return self.__player_names

    def get_ai_status(self):
        return self.__player_ai_status

    def play(self, move, player):
        self.__Board.make_a_move(move[0], move[1], move[2], player)

    def possible_player_moves(self, player, opponent):
        return self.__Board.get_possible_moves(player, opponent)

    def print_state(self, possible_moves, ai_enabled):
        board = self.__Board.get_board()
        if not ai_enabled:
            for move in possible_moves:
                board[move[0]][move[1]] = self.__Board.POSSIBLE
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

    def win_status(self, player, opponent):
        return self.__Board.win_status(player, opponent)

    def set_player_order(self, new_order):
        self.__player_names = new_order

    def get_piece_relation(self):
        if self.__Board.get_piece_relation()[self.__player_names[0]] == self.__Board.BLACK:
            return ["black", "white"]
        else:
            return ["white", "black"]

    def get_ai_move(self, possible_moves, current_player, opponent):
        scores = []
        for move in possible_moves:
            board = deepcopy(self.__Board)
            board.make_a_move(move[0], move[1], move[2], current_player)
            scores.append(self.__alpha_beta(board, current_player, opponent, 4, current_player, float("-inf"), float("inf")))
        return scores.index(min(scores))

    def __alpha_beta(self, game_state, player, opponent, depth, minimising_player, alpha, beta):
        if depth == 0 or (len(game_state.get_possible_moves(player, opponent)) == 0 and len(game_state.get_possible_moves(opponent, player)) == 0):
            return self.__heuristic(game_state, minimising_player)
        else:
            possible_moves = game_state.get_possible_moves(player, opponent)
            if player == minimising_player:
                result = float("inf")
                for move in possible_moves:
                    board = deepcopy(game_state)
                    board.make_a_move(move[0], move[1], move[2], player)
                    result = min(result, self.__alpha_beta(board, opponent, player, depth - 1, minimising_player, alpha, beta))
                    if result <= alpha:
                        break
                    beta = min(beta, result)
                return result
            else:
                result = float("-inf")
                for move in possible_moves:
                    board = deepcopy(game_state)
                    board.make_a_move(move[0], move[1], move[2], player)
                    result = max(result, self.__alpha_beta(board, opponent, player, depth - 1, minimising_player, alpha, beta))
                    if result >= beta:
                        break
                    alpha = max(alpha, result)
                return result


    def __heuristic(self, game_state, minimising_player):
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
        for row in range(0, 8):
            for col in range(0, 8):
                if game_state.get_board()[row][col] == game_state.get_piece_relation()[minimising_player]:
                    min_value += heuristic_values[row][col]
                else:
                    max_value += heuristic_values[row][col]
        return max_value - min_value


class Board:
    ALTERNATIVE = "○●＿◎"
    WHITE = "W"
    BLACK = "B"
    EMPTY = "_"
    POSSIBLE = "+"

    def __init__(self, player_names):
        self.__pieces = {player_names[0]: self.BLACK, player_names[1]: self.WHITE}
        self.__grid = []
        for _ in range(8):
            self.__grid.append([Piece(self.EMPTY) for _ in range(8)])
        self.__grid[3][3].flip_to(self.WHITE)
        self.__grid[4][4].flip_to(self.WHITE)
        self.__grid[3][4].flip_to(self.BLACK)
        self.__grid[4][3].flip_to(self.BLACK)

    def get_possible_moves(self, player, opponent):
        possible_moves = []
        for row in range(0, 8):
            for col in range(0, 8):
                if self.__grid[row][col].get_character() == self.EMPTY:
                    move_effects = []
                    for row_change in [-1, 0, 1]:
                        for col_change in [-1, 0, 1]:
                            if not (row_change == 0 and col_change == 0):
                                if 0 <= row + row_change < 8 and 0 <= col + col_change < 8 and self.__grid[row + row_change][col + col_change].get_character() == self.__pieces[opponent]:
                                    scale = 2
                                    same_piece_found = False
                                    while 0 <= row + row_change * scale < 8 and 0 <= col + col_change * scale < 8 and self.__grid[row + row_change * scale][col + col_change * scale].get_character() != self.EMPTY and not same_piece_found:
                                        if self.__grid[row + row_change * scale][col + col_change * scale].get_character() == self.__pieces[player]:
                                            same_piece_found = True
                                            break
                                        scale += 1
                                    if same_piece_found:
                                        move_effects.append([row_change, col_change, scale])
                    if len(move_effects) != 0:
                        possible_moves.append([row, col, move_effects])
        return possible_moves

    def make_a_move(self, row, col, move_effects, player):
        self.__grid[row][col].flip_to(self.__pieces[player])
        for effect in move_effects:
            for scale in range(1, effect[2]):
                self.__grid[row + effect[0] * scale][col + effect[1] * scale].flip_to(self.__pieces[player])

    def get_board(self):
        board = []
        for _ in range(8):
            board.append([0 for _ in range(8)])
        for row in range(0, 8):
            for col in range(0, 8):
                board[row][col] = self.__grid[row][col].get_character()
        return board

    def win_status(self, player, opponent):
        if len(self.get_possible_moves(player, opponent)) == 0 and len(self.get_possible_moves(opponent, player)) == 0:
            player_counter = 0
            opponent_counter = 0
            for row in range(0, 8):
                for col in range(0, 8):
                    if self.__grid[row][col].get_character() == self.__pieces[player]:
                        player_counter += 1
                    elif self.__grid[row][col].get_character() == self.__pieces[opponent]:
                        opponent_counter += 1
            if player_counter > opponent_counter:
                return player
            elif player_counter == opponent_counter:
                return "Draw"
            else:
                return opponent
        else:
            return None

    def get_piece_relation(self):
        return self.__pieces


class Piece:
    def __init__(self, character):
        self.__character = character

    def flip_to(self, character):
        self.__character = character

    def get_character(self):
        return self.__character


def main():
    interface = UI()
    interface.initialize_ui()


if __name__ == "__main__":
    main()
