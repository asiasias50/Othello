from time import time


class GameMode:  # Class provides relevant interface for fluent game flow and Artificial Intelligence algorithm
    def __init__(self):  # Initialises a game board on which all further manipulations will take place
        self.__Board = Board()

    def play(self, move):
        # Further block of functions filters only relevant to game flow functions provided by Board class
        self.__Board.make_a_move(move)

    def possible_player_moves(self):
        return self.__Board.get_possible_moves()

    def possible_character(self):
        return self.__Board.POSSIBLE

    def characters(self):
        return [self.__Board.BLACK, self.__Board.WHITE]

    def win_status(self):
        return self.__Board.win_status()

    def get_board(self):
        return self.__Board.get_board()

    def get_current_player(self):
        return self.__Board.get_current_player()

    def get_number_of_pieces(self):
        return self.__Board.get_number_of_pieces()

    def undo_move(self):
        self.__Board.undo_move()

    def get_move_history(self):
        return self.__Board.get_move_history()

    def load(self, memory):
        self.__Board.load(memory)

    def get_ai_move(self, possible_moves, depth, timer):
        # Minimax Algorithm with alpha beta pruning is used to find an optimal move for given board
        scores = []
        for move in range(0, len(possible_moves)):
            board = self.__Board.copy(move)
            board.make_a_move(0)
            scores.append(self.__alpha_beta(board, False, depth, False, float("-inf"), float("inf"),
                                            timer, board.opposite()))
        return scores.index(min(scores))  # Algorithm returns an index of best move to make

    def __alpha_beta(self, game_state, no_moves_flag, depth, minimising_player, alpha, beta, timer, AI_piece):
        # Group A skill, Optimisation algorithm
        start_time = time()
        new_flag = (len(game_state.get_possible_moves()) == 0)
        if depth == 0 or timer <= 1 or (new_flag and no_moves_flag):
            return self.__heuristic(game_state, AI_piece)
        else:
            possible_moves = game_state.get_possible_moves()
            if minimising_player:
                result = float("inf")
                for move in range(0, len(possible_moves)):  # Group A skill, Tree Traversal
                    board = game_state.copy(move)  # Group A skill, Dynamic generation of OOP object
                    board.make_a_move(0)
                    result = min(result, self.__alpha_beta(board, new_flag, depth - 1, not minimising_player, alpha,
                                                           beta, timer - (time() - start_time), AI_piece))
                    # Group A skill, Recursive algorithm
                    if result <= alpha:
                        break
                    beta = min(beta, result)
                return result
            else:
                result = float("-inf")
                for move in range(0, len(possible_moves)):  # Group A skill, Tree Traversal
                    board = game_state.copy(move)  # Group A skill, Dynamic generation of OOP object
                    board.make_a_move(0)
                    result = max(result, self.__alpha_beta(board, new_flag, depth - 1, not minimising_player, alpha,
                                                           beta, timer - (time() - start_time), AI_piece))
                    # Group A skill, Recursive algorithm
                    if result >= beta:
                        break
                    alpha = max(alpha, result)
                return result

    def __heuristic_corners(self, game_state, minimizing_player):
        max_value = 0
        min_value = 0
        max_player = game_state.WHITE if game_state.BLACK == minimizing_player else game_state.BLACK
        board = game_state.get_board()
        for corner in [[0,0], [0,7], [7,0], [7,7]]:
            if board[corner[0]][corner[1]] == minimizing_player:
                min_value += 1
            elif board[corner[0]][corner[1]] == max_player:
                max_value += 1
        if max_value + min_value == 0:
            return 0
        return (max_value - min_value) / (max_value + min_value)

    def __heuristic_mobility(self, game_state, minimizing_player):
        max_value = 0
        min_value = 0
        if game_state.get_current_player() == minimizing_player:
            min_value += len(game_state.get_possible_moves())
        else:
            max_value += len(game_state.get_possible_moves())

        game_state.undo_move()

        if game_state.get_current_player() == minimizing_player:
            min_value += len(game_state.get_possible_moves())
        else:
            max_value += len(game_state.get_possible_moves())

        if max_value + min_value == 0:
            return 0
        return (max_value - min_value) / (max_value + min_value)

    def __heuristic(self, game_state, minimizing_player):
        return 2 * self.__heuristic_corners(game_state, minimizing_player)\
               + self.__heuristic_mobility(game_state, minimizing_player)


class Board:  # Class contains a representation of game board and performs all board manipulations
    ALTERNATIVE = "○●＿◎"
    WHITE = "W"
    BLACK = "B"
    EMPTY = "_"
    POSSIBLE = "+"

    def __init__(self):
        # Initial board set up
        self.__grid = []
        for _ in range(8):
            self.__grid.append([self.EMPTY for _ in range(8)])
        self.__grid[3][3] = self.WHITE
        self.__grid[4][4] = self.WHITE
        self.__grid[3][4] = self.BLACK
        self.__grid[4][3] = self.BLACK
        # Initialisation of the boundary to optimise time to search for possible moves
        self.__boundary = {}
        self.__boundary_story = []
        self.__initialise_boundary()
        self.__current_player = self.BLACK
        self.__opponents = {self.BLACK: self.WHITE, self.WHITE: self.BLACK}
        self.__possible_moves = []
        self.__moves_meta_data = []
        # Stack in linked list implementation is used to store sequence of player moves
        self.__moves_story = []
        self.__moves_story_indexes = []

    def copy(self, move):  # User defined copy function optimising time complexity of Minimax algorithm
        new_board = Board()
        for row in range(0, 8):
            for col in range(0, 8):
                new_board.__grid[row][col] = self.__grid[row][col]
        for key in self.__boundary:
            new_board.__boundary[key] = self.__boundary[key]
        new_board.__current_player = self.__current_player
        new_board.__possible_moves.append(self.__possible_moves[move])
        new_board.__moves_meta_data.append(self.__moves_meta_data[move])
        return new_board

    def __initialise_boundary(self):  # Initialisation of boundary, area adjacent to existing pieces,
        # to optimise possible move search
        for row in range(2, 6):
            for col in range(2, 6):
                if (row, col) not in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    self.__boundary[(row, col)] = 0

    def get_possible_moves(self):
        # Function checks all available places from the boundary returning a set of moves that can be performed
        self.__moves_meta_data = []
        self.__possible_moves = []
        for row, col in self.__boundary:
            move_effects = []
            for row_change in [-1, 0, 1]:
                for col_change in [-1, 0, 1]:
                    if not (row_change == 0 and col_change == 0) and 0 <= row + row_change < 8 and \
                            0 <= col + col_change < 8:
                        if self.__grid[row + row_change][col + col_change] == self.__opponents[self.__current_player]:
                            scale = 2
                            same_piece_found = False
                            while 0 <= row + row_change * scale < 8 and 0 <= col + col_change * scale < 8 and \
                                    self.__grid[row + row_change * scale][col + col_change * scale] != self.EMPTY and \
                                    not same_piece_found:
                                if self.__grid[row + row_change * scale][col + col_change * scale] == \
                                        self.__current_player:
                                    same_piece_found = True
                                    break
                                scale += 1
                            if same_piece_found:
                                move_effects.append([row_change, col_change, scale])
            if len(move_effects) != 0:
                self.__possible_moves.append([row, col])
                self.__moves_meta_data.append(move_effects)
        return self.__possible_moves

    def opposite(self):   # Returns a symbol for opponent the player currently taking a turn
        return self.__opponents[self.__current_player]

    def get_current_player(self):  # Returns a symbol for player currently taking a turn
        return self.__current_player

    def make_a_move(self, move):
        # Places a piece of player's choice and performs corresponding update to the board and record
        if move is not None:
            # Move
            row = self.__possible_moves[move][0]
            col = self.__possible_moves[move][1]
            self.__grid[row][col] = self.__current_player
            for effect in self.__moves_meta_data[move]:
                for scale in range(1, effect[2]):
                    self.__grid[row + effect[0] * scale][col + effect[1] * scale] = self.__current_player

            # Saving into history
            self.__moves_story.append([row, col, self.__moves_meta_data[move]])  # Group A skill, Stack operation, push
            self.__moves_story_indexes.append(move)

            # Boundary update
            self.__boundary_story.append(self.__boundary.copy())
            del self.__boundary[(row, col)]
            for row_change in [-1, 0, 1]:
                for col_change in [-1, 0, 1]:
                    if 0 <= row + row_change < 8 and 0 <= col + col_change < 8:
                        if self.__grid[row + row_change][col + col_change] == self.EMPTY and \
                                (row + row_change, col + col_change) not in self.__boundary:
                            self.__boundary[(row + row_change, col + col_change)] = 0
        self.__current_player = self.__opponents[self.__current_player]

    def undo_move(self):
        # Function deletes the last move and performs corresponding
        # corrections to the board to restore it previous state
        if len(self.__moves_story) > 0:
            move = self.__moves_story.pop()  # Group A skill, Stack operation, pop
            self.__moves_story_indexes.pop()
            for effect in move[2][::-1]:
                for scale in range(1, effect[2]):
                    self.__grid[move[0] + effect[0] * scale][move[1] + effect[1] * scale] = self.__current_player
            self.__grid[move[0]][move[1]] = self.EMPTY
            self.__current_player = self.__opponents[self.__current_player]
            self.__boundary = self.__boundary_story.pop()

    def get_board(self):  # Returns board to be shown to user via UI
        return self.__grid

    def get_move_history(self):
        return self.__moves_story_indexes

    def win_status(self):  # Checks which player won or if its a draw
        black_counter = 0
        white_counter = 0
        for row in range(0, 8):
            for col in range(0, 8):
                if self.__grid[row][col] == self.BLACK:
                    black_counter += 1
                elif self.__grid[row][col] == self.WHITE:
                    white_counter += 1
        if black_counter > white_counter:
            return self.BLACK
        elif black_counter == white_counter:
            return "Draw"
        else:
            return self.WHITE

    def get_number_of_pieces(self):  # Returns a number of pieces each player has to be shown via UI
        black_count = 0
        while_count = 0
        for row in range(0, 8):
            for col in range(0, 8):
                if self.__grid[row][col] == self.BLACK:
                    black_count += 1
                elif self.__grid[row][col] == self.WHITE:
                    while_count += 1
        return [black_count, while_count]

    def load(self, memory):
        moves = memory
        while len(moves) > 0:
            move = int(moves[0])
            moves = moves[1:]
            self.get_possible_moves()
            self.make_a_move(move)
