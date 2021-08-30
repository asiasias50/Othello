from time import time


class GameMode:
    def __init__(self):
        self.__Board = Board()

    def play(self, move):
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

    def get_ai_move(self, possible_moves, depth, timer):
        scores = []
        for move in range(0, len(possible_moves)):
            board = self.__Board.copy(move)
            board.make_a_move(0)
            scores.append(self.__alpha_beta(board, False, depth, True, float("-inf"), float("inf"), timer))
        return scores.index(min(scores))

    def __alpha_beta(self, game_state, no_moves_flag, depth, minimising_player, alpha, beta, timer):
        start_time = time()
        new_flag = (len(game_state.get_possible_moves()) == 0)
        if depth == 0 or timer <= 1 or (new_flag and no_moves_flag):
            return self.__heuristic(game_state, minimising_player)
        else:
            possible_moves = game_state.get_possible_moves()
            if minimising_player:
                result = float("inf")
                for move in range(0, len(possible_moves)):
                    board = game_state.copy(move)
                    board.make_a_move(0)
                    result = min(result, self.__alpha_beta(board, new_flag, depth - 1, not minimising_player, alpha, beta, timer - (time() - start_time)))
                    if result <= alpha:
                        break
                    beta = min(beta, result)
                return result
            else:
                result = float("-inf")
                for move in range(0, len(possible_moves)):
                    board = game_state.copy(move)
                    board.make_a_move(0)
                    result = max(result, self.__alpha_beta(board, new_flag, depth - 1, not minimising_player, alpha, beta, timer - (time() - start_time)))
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
            self.__grid.append([self.EMPTY for _ in range(8)])
        self.__grid[3][3] = self.WHITE
        self.__grid[4][4] = self.WHITE
        self.__grid[3][4] = self.BLACK
        self.__grid[4][3] = self.BLACK
        self.__boundary = {}
        self.__initialise_boundary()
        self.__current_player = self.BLACK
        self.__opponents = {self.BLACK: self.WHITE, self.WHITE: self.BLACK}
        self.__possible_moves = []
        self.__moves_meta_data = []
        self.__moves_story = []

    def copy(self, move):
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

    def __initialise_boundary(self):
        for row in range(2, 6):
            for col in range(2, 6):
                if (row, col) not in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    self.__boundary[(row, col)] = 0

    def get_possible_moves(self):
        self.__moves_meta_data = []
        self.__possible_moves = []
        for row, col in self.__boundary:
            move_effects = []
            for row_change in [-1, 0, 1]:
                for col_change in [-1, 0, 1]:
                    if not (row_change == 0 and col_change == 0) and 0 <= row + row_change < 8 and 0 <= col + col_change < 8:
                        if self.__grid[row + row_change][col + col_change] == self.__opponents[self.__current_player]:
                            scale = 2
                            same_piece_found = False
                            while 0 <= row + row_change * scale < 8 and 0 <= col + col_change * scale < 8 and self.__grid[row + row_change * scale][col + col_change * scale] != self.EMPTY and not same_piece_found:
                                if self.__grid[row + row_change * scale][col + col_change * scale] == self.__current_player:
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
        return self.__opponents[self.__current_player]

    def get_current_player(self):
        return self.__current_player

    def make_a_move(self, move):
        if move is not None:
            # Move
            row = self.__possible_moves[move][0]
            col = self.__possible_moves[move][1]
            self.__grid[row][col] = self.__current_player
            for effect in self.__moves_meta_data[move]:
                for scale in range(1, effect[2]):
                    self.__grid[row + effect[0] * scale][col + effect[1] * scale] = self.__current_player

            # Saving into history
            self.__moves_story.append([row, col, self.__moves_meta_data[move]])

            # Boundary update
            del self.__boundary[(row, col)]
            for row_change in [-1, 0, 1]:
                for col_change in [-1, 0, 1]:
                    if 0 <= row + row_change < 8 and 0 <= col + col_change < 8:
                        if self.__grid[row + row_change][col + col_change] == self.EMPTY and (row + row_change, col + col_change) not in self.__boundary:
                            self.__boundary[(row + row_change, col + col_change)] = 0
        self.__current_player = self.__opponents[self.__current_player]

    def undo_move(self):
        if len(self.__moves_story) > 0:
            move = self.__moves_story.pop()
            for effect in move[2][::-1]:
                for scale in range(1, effect[2]):
                    self.__grid[move[0] + effect[0] * scale][move[1] + effect[1] * scale] = self.__current_player
            self.__grid[move[0]][move[1]] = self.EMPTY
            self.__current_player = self.__opponents[self.__current_player]
            self.__boundary[(move[0], move[1])] = 0

    def get_board(self):
        return self.__grid

    def win_status(self):
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

    def get_number_of_pieces(self):
        black_count = 0
        while_count = 0
        for row in range(0, 8):
            for col in range(0, 8):
                if self.__grid[row][col] == self.BLACK:
                    black_count += 1
                elif self.__grid[row][col] == self.WHITE:
                    while_count += 1
        return [black_count, while_count]
