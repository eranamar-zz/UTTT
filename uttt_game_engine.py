#=======================================================
#       uttt_game_engine.py
#       Created by: Adi Ben Binyamin
#                   Eran Amar
#========================================================
from time import *
from agents_factory import AgentFactory, AGENTS
from global_consts import *
from action import Action

#===============================
#       Configurations:
#===============================

DEBUG_FLAG = False


def debug(s):
    if DEBUG_FLAG:
        print s


def assess_board(lst, get_func=list.__getitem__):
    center_item = get_func(lst, 4)
    if center_item != EMPTY:  # (1,1)
        if (center_item == get_func(lst, 0) and center_item == get_func(lst, 8)) or (
                        center_item == get_func(lst, 2) and center_item == get_func(lst,
                                                                                    6)):
            return center_item

    for i in xrange(3):
        row_head = i * 3
        col_head = i
        if get_func(lst, i * 3 + i) == EMPTY:  # (0,0), (1,1), (2,2)
            continue
        # test complete row:
        if get_func(lst, row_head) == get_func(lst, row_head + 1) and get_func(lst,
                                                                               row_head) == get_func(
                lst, row_head + 2):
            return get_func(lst, row_head)
        # test complete column:
        if get_func(lst, col_head) == get_func(lst, col_head + 3) and get_func(lst,
                                                                               col_head) == get_func(
                lst, col_head + 6):
            return get_func(lst, col_head)
    return None


def convert_board(next_board_pos):
    if next_board_pos:
        return '%s-%s' % (Game.FIRST_INDEX_2_STR[next_board_pos[0]],
                          Game.SECOND_INDEX_2_STR[next_board_pos[1]])
    return 'any free board'


def draw_board(uttt_board, next_board=None):
    nextToPlayIn = (next_board / 3, next_board % 3) if next_board is not None else None
    full_board = uttt_board.convert_t2D()
    board_matrix = [[" "] * 25 for _ in range(16)]

    # Draw in board outline
    for row in [0, 5, 10, 15]:
        for col in range(len(board_matrix[row])):
            board_matrix[row][col] = "_"
        for col in [0, 8, 16, 24]:
            board_matrix[row][col] = " "
    for col in [0, 8, 16, 24]:
        for row in range(1, len(board_matrix)):
            board_matrix[row][col] = "|"

    # Draw in mini boards
    rowTable = [2, 3, 4, 7, 8, 9, 12, 13, 14]
    colTable = [2, 4, 6, 10, 12, 14, 18, 20, 22]
    for row in range(9):
        for col in range(9):
            board_matrix[rowTable[row]][colTable[col]] = full_board[row][col]


    # Highlight miniboard that's about to be played in
    if nextToPlayIn != None:
        r_jump = nextToPlayIn[0] * 5
        c_jump = nextToPlayIn[1] * 8
        # Top/bottom sides
        for row in [r_jump, r_jump + 5]:
            for col in [c_jump + 2, c_jump + 4, c_jump + 6]:
                board_matrix[row][col] = " "
        # Left/right sides
        for row in [r_jump + 2, r_jump + 4]:
            for col in [c_jump, c_jump + 8]:
                board_matrix[row][col] = " "

    drawnBoard = []
    for row in board_matrix:
        newRow = ""
        for col in row:
            newRow = newRow + col
        drawnBoard.append(newRow)

    row_index = 0
    print '    0 1 2   3 4 5   6 7 8  '

    for i in xrange(len(drawnBoard)):
        if i in [2, 3, 4, 7, 8, 9, 12, 13, 14]:
            print '%d %s' % (row_index, drawnBoard[i])
            row_index += 1
        else:
            print '  %s' % (drawnBoard[i])

    if not uttt_board.has_winner() and not uttt_board.is_board_full():
        print 'Next board to play in: %s' % convert_board(nextToPlayIn)


class MiniBoard:
    def __init__(self, other=None):
        self._winner = None
        if other is not None:
            assert (len(other) == 9)
            self._board = list(other)
            self._legal_cells = [i for i in xrange(9) if self._board[i] == EMPTY]
            self._assess_board()
        else:
            self._board = [EMPTY] * 9
            self._legal_cells = range(9)

    def do_move(self, player, index):
        assert (index in self._legal_cells)
        self._board[index] = str(player)
        self._legal_cells.remove(index)
        self._assess_board()

    def _assess_board(self):
        if self._winner is not None:
            return
        self._winner = assess_board(self._board)
        if self._winner is not None:
            self._legal_cells = []


    def has_winner(self):
        return (self._winner is not None)

    def get_winner(self):
        return self._winner

    def get(self, index):
        assert (0 <= index < 9)
        return self._board[index]

    def is_board_full(self):
        return len(self._legal_cells) == 0

    def deep_copy(self):
        dup = MiniBoard(self._board)
        dup._legal_cells = list(self._legal_cells)
        dup._winner = self._winner
        return dup

    def get_board(self):
        return self._board

    def get_legal_cells(self):
        return self._legal_cells

    def __str__(self):
        return str(self._board)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class UTTTBoard:
    def __init__(self, boards=list()):
        self._boards = boards
        i = len(boards)
        while i < 9:
            self._boards.append(MiniBoard())
            i += 1
        self._winner = None
        self._available_boards = [i for i in xrange(9) if
                                  self._boards[i].is_board_full() == False]

    def do_move(self, player, miniB_index, inner_index):
        assert (miniB_index in self._available_boards)
        self.get_miniBoard(miniB_index).do_move(player, inner_index)
        self._assess_board()
        if self.get_miniBoard(miniB_index).is_board_full():
            self._available_boards.remove(miniB_index)

    def _assess_board(self):
        if self._winner is not None:
            return
        get_func = lambda obj, index: (self._boards[index].get_winner() or EMPTY)
        self._winner = assess_board(self._boards, get_func)


    def has_winner(self):
        return (self._winner is not None)

    def get_winner(self):
        return self._winner

    def is_board_full(self):
        return len(self._available_boards) == 0

    def get_miniBoard(self, index):
        assert (0 <= index < 9)
        return self._boards[index]

    def get_single_cell(self, miniBoard_pos, inner_pos):
        return self.get_miniBoard(miniBoard_pos).get(inner_pos)

    def deep_copy(self):
        dup_boards = [miniB.deep_copy() for miniB in self._boards]
        dup = UTTTBoard(dup_boards)
        dup._winner = self._winner
        return dup

    def convert_t2D(self):
        full_board = []
        for miniB_row in xrange(3):
            for inner_row in xrange(3):
                row = []
                for col in xrange(3):
                    mini = (self._boards)[miniB_row * 3 + col]
                    middle = str(mini.get_winner()) if inner_row == 1 else SPACE
                    row.extend(mini.get_board()[
                               inner_row * 3: inner_row * 3 + 3] if not mini.has_winner() else [
                        SPACE, middle, SPACE])
                full_board.append(row)
        return full_board

    def convert_tMiniB(self):
        return MiniBoard([(innerB.get_winner() or EMPTY) for innerB in self._boards])

    def __str__(self):
        return '\n'.join([str(miniB) for miniB in self._boards])

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class Player:
    def __init__(self, is_x=True):
        self._is_x = is_x

    def is_x(self):
        return self._is_x

    def opponent(self):
        return Player(not self._is_x)

    def __str__(self):
        return X_PLAYER if self._is_x else Y_PLAYER

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class State:
    def __init__(self, uttt=None, player=Player(), mini_board=None):
        self._uttt = UTTTBoard() if uttt is None else uttt.deep_copy()
        self.player_turn = player  # default to x's turn
        self.mini_board = mini_board
        self._last_move = None

    def get_legal_actions(self):
        acts = []
        miniBs = [self.mini_board] if self.mini_board is not None else range(9)
        #debug('available miniBs: %s' % miniBs)
        for board_index in miniBs:
            legal_cells = self._uttt.get_miniBoard(board_index).get_legal_cells()
            for cell in legal_cells:
                acts.append(Action(board_index, cell))
        return acts

    def generate_successor(self, act):
        new_state = State(self._uttt, self.player_turn.opponent(), act.inner_index)
        new_state._uttt.do_move(self.player_turn, act.miniB_index, act.inner_index)
        new_state._last_move = act
        if new_state._uttt.get_miniBoard(act.inner_index).is_board_full():
            new_state.mini_board = None
        return new_state

    def is_terminal(self):
        return self._uttt.has_winner() or self._uttt.is_board_full()

    def get_last_move(self):
        return self._last_move

    def get_board(self):
        return self._uttt

    def get_player(self):
        return self.player_turn

    def draw(self):
        if Game.ENABLE_GRAPHICS:
            print 'Player %s turn: (board state befor the move)' % self.player_turn
            draw_board(self._uttt, self.mini_board)


    def deep_copy(self):
        new_state = State(self._uttt, self.player_turn, self.mini_board)
        new_state._last_move = self._last_move
        return new_state

    def __str__(self):
        return str(self._uttt) + str(self.player_turn)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class Timer:
    MOVES, TOTAL_TIME, AVG_MOVE = 0, 1, 2
    def __init__(self):
        self.statistics = {X_PLAYER:[0, 0.0, 0.0], Y_PLAYER:[0, 0.0, 0.0]}

    def total_moves(self):
        return self.statistics[X_PLAYER][Timer.MOVES] + self.statistics[Y_PLAYER][Timer.MOVES]

    def measure_move(self, agent_obj, agent_name, state):
        start_t = clock()
        action = agent_obj.choose_act(state)
        end_t = clock()
        self.statistics[agent_name][Timer.MOVES] += 1
        self.statistics[agent_name][Timer.TOTAL_TIME] += (end_t - start_t)
        return action

    def calc_avg(self):
        self.statistics[X_PLAYER][Timer.AVG_MOVE] = self.statistics[X_PLAYER][Timer.TOTAL_TIME] / self.statistics[X_PLAYER][Timer.MOVES]
        self.statistics[Y_PLAYER][Timer.AVG_MOVE] = self.statistics[Y_PLAYER][Timer.TOTAL_TIME] / self.statistics[Y_PLAYER][Timer.MOVES]

class Game:
    FIRST_INDEX_2_STR = {0: 'top', 1: 'middle', 2: 'bottom'}
    SECOND_INDEX_2_STR = {0: 'left', 1: 'center', 2: 'right'}
    TURNS_INTERVAL_SEC = 0
    ENABLE_GRAPHICS = True

    @staticmethod
    def play(state, x_agent, y_agent, enable_prints=True):
        t = Timer()
        state.draw()
        while not state.is_terminal():
            if state.player_turn.is_x():
                action = t.measure_move(x_agent, X_PLAYER, state)
            else:
                action = t.measure_move(y_agent, Y_PLAYER, state)
            state = state.generate_successor(action)
            state.draw()
            sleep(Game.TURNS_INTERVAL_SEC)
        t.calc_avg()
        if enable_prints:
            print 'The winner is %s! Total moves: %d' % (state.get_board().get_winner(), t.total_moves())
        return str(state.get_board().get_winner()), t

    @staticmethod
    def set_enable_graphics(val):
        Game.ENABLE_GRAPHICS = bool(val)

def print_statistics(first_agent_type, second_agent_type, wins, avg_move, session_size):
    print ' ===  Statistics  ==='
    print 'Agent %s vs %s:' % (first_agent_type, second_agent_type)
    print '%s wins:\t%s. avg_move:\t%5f ms' %   (first_agent_type,
                                            (100.0*wins[X_PLAYER])/session_size,
                                            (1000.0*avg_move[X_PLAYER])/session_size)
    print '%s wins:\t%s. avg_move:\t%5f ms' %   (second_agent_type,
                                            (100.0*wins[Y_PLAYER])/session_size,
                                            (1000.0*avg_move[Y_PLAYER])/session_size)
    print '%s:\t%s.' % ('Ties', (100.0*wins['None'])/session_size)
    print '--------------'*4

def run_session(first_agent_type, second_agent_type, session_size=10, initial_state=State(), enable_prints=True):
    if session_size > 1:
        Game.set_enable_graphics(False)
    if enable_prints:
        print 'The session start with %s agent for X player, and %s agent for O player' % (
        first_agent_type, second_agent_type)
    wins = {X_PLAYER: 0,
            Y_PLAYER: 0,
            'None'  : 0}
    avg_move = { X_PLAYER : 0.0, Y_PLAYER: 0.0 }
    for i in xrange(session_size):
        # generates the agents here to ensure counter reset for randomfull-agent
        x_agent = AgentFactory(first_agent_type, Player(is_x=True))
        y_agent = AgentFactory(second_agent_type, Player(is_x=False))
        winner, t = Game.play(initial_state, x_agent, y_agent, enable_prints)
        wins[winner] += 1
        avg_move[X_PLAYER] += t.statistics[X_PLAYER][Timer.AVG_MOVE]
        avg_move[Y_PLAYER] += t.statistics[Y_PLAYER][Timer.AVG_MOVE]
    print_statistics(first_agent_type, second_agent_type, wins, avg_move, session_size)

def run_all():
    repeat = 100
    Game.set_enable_graphics(False)
    agents = list(AGENTS.keys())
    agents.remove('human')
    print '+++++++++++++' *5
    print 'Starting full sessions with size %s, list of participating agents: %d = %s' % (
        str(repeat), len(agents), str(agents))
    print '+++++++++++++' *5
    for x_player in agents:
        for y_player in agents:
            if x_player == y_player:
                continue            
            print '[%s vs %s]' % (x_player, y_player)
            run_session(x_player,y_player,session_size=repeat,enable_prints=False)
               
        
if __name__ == '__main__':
    from sys import argv
    if not argv:
        print USAGE
    else:
        if 'python' in argv[0].lower():
            argv = argv[2:]
        else:
            argv = argv[1:]
        if len(argv) != 2:
            print USAGE
        else:
            run_session(argv[0], argv[1], session_size=1, enable_prints=True)    



