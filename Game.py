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
                game_finished = False
                win_status = None
                opponents = {self.__player_names[0]: self.__player_names[1], self.__player_names[1]: self.__player_names[0]}
                while not game_finished:
                    for player in self.__player_names:
                        possible_moves = self.__Game.possible_player_moves(player, opponents[player])
                        self.__Game.print_state(possible_moves)
                        move = self.get_move_from_player(player, possible_moves)
                        self.__Game.play(possible_moves[move], player)
                        win_status = self.__Game.win_status(player, opponents[player])
                        if win_status in self.__player_names or win_status == "Draw":
                            game_finished = True
                            break
                if win_status == "Draw":
                    print("Game is finished in a draw.")
                else:
                    print(f"Game is finished, {win_status} won.")

    def __initialise_names(self):
        self.__number_of_players = None
        self.__player_names = []
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
            self.__player_names.append(input(f"Enter a name of player {_}. "))

    def get_move_from_player(self, player, possible_moves):
        move = [-1, -1]
        possible_coordinates = []
        for coordinate in possible_moves:
            possible_coordinates.append([coordinate[0], coordinate[1]])
        while [move[0] - 1, move[1] - 1] not in possible_coordinates:
            try:
                values = input(f"{player}, please enter row and column of your move(eg. 4 5). ")
                for _ in range(0, len(values.split())):
                    move[_] = int(values.split()[_])
            except InputError:
                print("You should enter two numbers, each in range from 1 to 8.")
                print()
        return possible_coordinates.index([move[0] - 1, move[1] - 1])


class InputError(Exception):
    """User input is incorrect"""
    pass


class GameMode:
    def __init__(self, player_names):
        self.__Board = Board(player_names)

    def play(self, move, player):
        self.__Board.make_a_move(move[0], move[1], move[2], player)

    def possible_player_moves(self, player, opponent):
        return self.__Board.get_possible_moves(player, opponent)

    def print_state(self, possible_moves):
        if len(possible_moves) == 0:
            input("You have no possible moves, turn is passed.")
        else:
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
