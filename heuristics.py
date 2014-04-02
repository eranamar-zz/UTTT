#=======================================================
#       heuristics.py
#       Created by: Adi Ben Binyamin
#                   Eran Amar
#========================================================
from global_consts import *

class Heuristic:
    '''
    Abstract class.
    Heuristics to evaluate states. sometimes depends on the player that the evaluation
    is related to.
    In general heuristics classes should be static.
    '''
    @staticmethod
    def get_evaluate_function(player_obj):
        '''
        returns a FUNCTION with the following signature: "def evaluate(some_state): returns <legal action>"
        '''
        raise NotImplementedError()

class WinningPossibilitiesHeu(Heuristic):
    #parameters for that heuristics
    APPROXIMATE_WIN_SCORE = 7
    BIG_BOARD_WEIGHT = 23
    WIN_SCORE = 10**6
    POSSIBLE_WIN_SEQUENCES = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]

    @staticmethod
    def get_evaluate_function(player_obj):
        return lambda some_state: WinningPossibilitiesHeu.__eval_state(some_state, player_obj)

    @staticmethod
    def __eval_state(state, player):
        uttt_board = state.get_board()
        if uttt_board.has_winner():
            winner = uttt_board.get_winner()
            free_cells = 0
            for i in xrange(9):
                miniB = uttt_board.get_miniBoard(i)
                free_cells += len(miniB.get_legal_cells())
            return WinningPossibilitiesHeu.WIN_SCORE + free_cells if winner == str(player) else -WinningPossibilitiesHeu.WIN_SCORE - free_cells
        if uttt_board.is_board_full():
            return 0
        board_as_mini = uttt_board.convert_tMiniB()
        ret = WinningPossibilitiesHeu.__assess_miniB(board_as_mini, player) * WinningPossibilitiesHeu.BIG_BOARD_WEIGHT
        for i in xrange(9):
            miniB = uttt_board.get_miniBoard(i)
            if not miniB.is_board_full():
                ret += WinningPossibilitiesHeu.__assess_miniB(miniB, player)
        return ret

    @staticmethod
    def __assess_miniB(miniB, player):
        if miniB.is_board_full():
            return 0
        player_counter = 0
        opponent_counter = 0
        player_str = str(player)
        opponent_str = str(player.opponent())
        miniB_as_list = miniB.get_board()
        for seq in WinningPossibilitiesHeu.POSSIBLE_WIN_SEQUENCES:
            filtered_seq = [miniB_as_list[index] for index in seq if miniB_as_list[index] != EMPTY]
            if player_str in filtered_seq:
                if opponent_str in filtered_seq:
                    continue
                if len(filtered_seq) > 1:
                    player_counter += WinningPossibilitiesHeu.APPROXIMATE_WIN_SCORE
                player_counter += 1
            elif opponent_str in filtered_seq:
                if len(filtered_seq) > 1:
                    opponent_counter += WinningPossibilitiesHeu.APPROXIMATE_WIN_SCORE
                opponent_counter += 1
        return player_counter - opponent_counter

class CellsWeightHeu(Heuristic):
    #parameters for that heuristics
    BOARD_WIN_SCORE = 100
    TIE = 0
    SCORE_PER_CELL = {0: 30, 1: 20, 2: 30, 3: 20, 4: 50, 5: 20, 6: 30, 7: 20, 8: 30}
    CLOSE_TO_WIN_SCORE = 75
    BIG_BOARD_WEIGHT = 20
    BLOCKING_OPTIONS = {0: [(1, 2), (3, 6), (4, 8)], 1: [(0, 2), (4, 7)],
                    2: [(0, 1), (4, 6), (5, 8)], 3: [(0, 6), (5, 4)],
                    4: [(0, 8), (2, 6), (1, 7), (3, 5)], 5: [(2, 8), (3, 4)],
                    6: [(0, 3), (7, 8), (2, 4)], 7: [(6, 8), (1, 4)],
                    8: [(6, 7), (2, 5), (0, 4)]}

    @staticmethod
    def get_evaluate_function(player_obj):
        return lambda some_state: CellsWeightHeu.__eval_state(some_state, str(player_obj))


    @staticmethod
    def __eval_state(some_state, player_str):
        ret_val = 0
        last_move = some_state.get_last_move()
        for i in xrange(9):
            miniB = some_state.get_board().get_miniBoard(i)
            ret_val += CellsWeightHeu.__assess_miniB(miniB, last_move.inner_index, player_str)
        uttt_as_minib = some_state.get_board().convert_tMiniB()
        ret_val += (CellsWeightHeu.__assess_miniB(uttt_as_minib, last_move.miniB_index, player_str) * CellsWeightHeu.BIG_BOARD_WEIGHT)
        return ret_val

    @staticmethod
    def __assess_miniB(miniB, index_played, player_str):
        if miniB.has_winner():
            if player_str == miniB.get_winner():
                return CellsWeightHeu.BOARD_WIN_SCORE
            return -CellsWeightHeu.BOARD_WIN_SCORE
        if miniB.is_board_full():
            return CellsWeightHeu.TIE
        curr_board = miniB.get_board()
        for blocking_index1, blocking_index2 in CellsWeightHeu.BLOCKING_OPTIONS[index_played]:
            if curr_board[blocking_index1] == player_str:
                if curr_board[blocking_index1] == curr_board[blocking_index2]:
                    return CellsWeightHeu.CLOSE_TO_WIN_SCORE
        return CellsWeightHeu.SCORE_PER_CELL[index_played]

class RecursiveWeightHeu(Heuristic):
    CELL_WEIGHT = [3, 2, 3, 2, 4, 2, 3, 2, 3]
    SUM_ALL_CELLS_WEIGHT = 24
    TIE = 0
    WIN_GAME_SCORE = 24*24

    @staticmethod
    def get_evaluate_function(player_obj):
        return lambda some_state: RecursiveWeightHeu.__eval_state(some_state, str(player_obj))

    @staticmethod
    def __eval_state(state, player_str):
        val = 0
        uttt = state.get_board()
        if uttt.has_winner():
            if uttt.get_winner() == player_str:
                return RecursiveWeightHeu.WIN_GAME_SCORE
            return -RecursiveWeightHeu.WIN_GAME_SCORE
        if uttt.is_board_full():
            return RecursiveWeightHeu.TIE
        for i in xrange(9):
            miniB = uttt.get_miniBoard(i)
            miniB_val = RecursiveWeightHeu.__assess_miniB(miniB, player_str)
            val += (RecursiveWeightHeu.CELL_WEIGHT[i] * miniB_val)
        return val

    @staticmethod
    def __assess_miniB(miniB, player_str):
        val = 0
        minib = miniB.get_board()
        if miniB.has_winner():
            if miniB.get_winner() == player_str:
                return RecursiveWeightHeu.SUM_ALL_CELLS_WEIGHT
            return -RecursiveWeightHeu.SUM_ALL_CELLS_WEIGHT
        if miniB.is_board_full():
            return RecursiveWeightHeu.TIE
        for i in xrange(9):
            if minib[i] == player_str:
                val += RecursiveWeightHeu.CELL_WEIGHT[i]
            elif minib[i] == EMPTY:
                val += 0
            else:
                val -= RecursiveWeightHeu.CELL_WEIGHT[i]
        return val

