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
        self.__player_names = []
        self.__quit = False
        self.__Game = None
        self.__run()

    def __run(self):
        while not self.__quit:
            if input("Enter q to quit or any other character to play. ") == "q":
                self.__quit = True
            else:
                self.__initialise_names()
                self.__Game = GameMode(self.__player_names)
                print(f"{self.__player_names[0]} will play with black pieces, {self.__player_names[1]} will play with white pieces."
                      f" {self.__player_names[0]} starts.")
                print()
                game_finished = False
                opponents = {self.__player_names[0]: self.__player_names[1], self.__player_names[1]: self.__player_names[0]}
                while not game_finished:
                    for player in self.__player_names:
                        self.__Game.print_state(player, opponents[player])
                        move = self.get_move_from_player(player)
                        self.__Game.play(move[0], move[1], player)

    def __initialise_names(self):
        self.__number_of_players = None
        self.__player_names = []
        while self.__number_of_players is None:
            try:
                self.__number_of_players = int(input("Enter number of players(1 or 2): "))
            except InputError:
                print("Input should be an integer 1 or 2.")
                print()
        for _ in range(1, self.__number_of_players + 1):
            self.__player_names.append(input(f"Enter a name of player {_}. "))

    def get_move_from_player(self, player):
        move = [-1, -1]
        while move[0] == -1 or move[1] == -1:
            try:
                values = input(f"{player}, please enter row and column of your move(eg. 4 5). ")
                for _ in range(0, len(values.split())):
                    move[_] = int(values.split()[_])
            except InputError:
                print("You should enter two numbers, each in range from 1 to 8.")
                print()
        return move


class InputError(Exception):
    """User input is incorrect"""
    pass


class GameMode:
    def __init__(self, player_names):
        self.__Board = Board(player_names)

    def play(self, row, col, move_effects, player):
        self.__Board.make_a_move(row, col, move_effects, player)

    def possible_player_moves(self, player, opponent):
        return self.__Board.get_possible_moves(player, opponent)

    def print_state(self, player, opponent):
        board = self.__Board.get_board()
        for move in self.__Board.get_possible_moves(player, opponent):
            board[move[0]][move[1]] = self.__Board.POSSIBLE
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
                move_effects = []
                for row_change in [-1, 0, 1]:
                    for col_change in [-1, 0, 1]:
                        if not (row_change == 0 and col_change == 0):
                            if 0 <= row + row_change < 8 and 0 <= col + col_change < 8 and self.__grid[row + row_change][col + col_change].get_character() == self.__pieces[opponent]:
                                scale = 2
                                same_piece_found = False
                                while 0 <= row + row_change * scale < 8 and 0 <= col + col_change * scale < 8 and not same_piece_found:
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
        for effect in move_effects:
            for scale in range(0, effect[2]):
                self.__grid[row + effect[0] * scale][col + effect[1] * scale].flip_to(self.__pieces[player])

    def get_board(self):
        board = []
        for _ in range(8):
            board.append([0 for _ in range(8)])
        for row in range(0, 8):
            for col in range(0, 8):
                board[row][col] = self.__grid[row][col].get_character()
        return board


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
