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


class InputError(Exception):
    """User input is incorrect"""
    pass


class GameMode:
    def __init__(self, player_names):
        self.__player_names = player_names
        self.__Board = Board()
        self.__use_AI = False
        if len(self.__player_names) == 1:
            self.__use_AI = True


class Board:
    WHITE = "○"
    BLACK = "●"
    EMPTY = "＿"
    POSSIBLE = "◎"

    def __init__(self):
        self.__grid = []
        for _ in range(8):
            self.__grid.append([Piece(self.EMPTY) for _ in range(8)])
        self.__grid[3][3].flip_to(self.WHITE)
        self.__grid[4][4].flip_to(self.WHITE)
        self.__grid[3][4].flip_to(self.BLACK)
        self.__grid[4][3].flip_to(self.BLACK)

    def place_piece(self, row, col, player):
        self.__grid[row][col].flip_to(player)

    def resolve(self, last_row, last_col, player, opponent):
        for row_change in [-1, 0, 1]:
            for col_change in [-1, 0, 1]:
                if 0 <= last_row + row_change < 8 and 0 <= last_col + col_change < 8 and self.__grid[last_row + row_change][last_col + col_change].get_character() == opponent:
                    scale = 2
                    same_piece_found = False
                    while 0 <= last_row + row_change * scale < 8 and 0 <= last_col + col_change * scale < 8 and not same_piece_found:
                        if self.__grid[last_row + row_change * scale][last_col + col_change * scale].get_character() == player:
                            same_piece_found = True
                    if same_piece_found:
                        for step in range(1, scale):
                            self.__grid[last_row + row_change * step][last_col + col_change * step].flip_to(player)

    def print(self):
        print("  1＿2＿3＿4＿5＿6＿7＿8")
        for row in range(0, 8):
            print(f"{row + 1} ", end='')
            for col in range(0, 8):
                print(self.__grid[row][col].get_character(), end="|")
            print("\b")


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


'''if __name__ == "__main__":
    main()'''
