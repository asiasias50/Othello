import pickle


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
        self.__number_of_players = None
        self.__quit = False
        self.__Game = None
        self.__run()

    def __run(self):
        while not self.__quit:
            game_decision = input("Enter q to quit, l to load most recent game, or any other character to play. ")
            if game_decision == "q":
                self.__quit = True
            else:
                if game_decision == "l":
                    self.__load_game_state()
                    if self.__Game is None:
                        print("Game cannot be loaded.")
                        continue
                else:
                    self.__Game = GameMode(self.__initialise_names())
                colours = self.__Game.get_colours()
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
                        else:
                            self.__Game.print_state(possible_moves)
                            move = self.__get_move_from_player(player, possible_moves)
                            if move is None:
                                self.__Game.set_player_order([player, opponents[player]])
                                self.__store_game_state()
                                game_finished = True
                                break
                            self.__Game.play(possible_moves[move], player)
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
        self.__number_of_players = None
        player_names = []
        while self.__number_of_players is None:
            try:
                self.__number_of_players = int(input("Enter number of players(1 or 2): "))
            except ValueError:
                print("Input should be an integer 1 or 2.")
                print()
                continue
            if self.__number_of_players not in [1, 2]:
                print("Input should be an integer 1 or 2.")
                print()
                self.__number_of_players = None
        for _ in range(1, self.__number_of_players + 1):
            player_names.append(input(f"Enter a name of player {_}. "))
        return player_names

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
            pickle.dump(self.__Game, f)

    def __load_game_state(self):
        try:
            f = open("Last_Game_Save.txt", "rb")
            self.__Game = pickle.load(f)
        except IOError:
            self.__Game = None


class GameMode:
    def __init__(self, player_names):
        self.__player_names = player_names
        self.__Board = Board(player_names)

    def get_names(self):
        return self.__player_names

    def play(self, move, player):
        self.__Board.make_a_move(move[0], move[1], move[2], player)

    def possible_player_moves(self, player, opponent):
        return self.__Board.get_possible_moves(player, opponent)

    def print_state(self, possible_moves):
        board = self.__Board.get_board()
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

    def get_colours(self):
        if self.__Board.get_colours()[self.__player_names[0]] == self.__Board.BLACK:
            return ["black", "white"]
        else:
            return ["white", "black"]


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

    def get_colours(self):
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
