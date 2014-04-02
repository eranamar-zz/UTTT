#=======================================================
#       agents_pool.py
#       Created by: Adi Ben Binyamin
#                   Eran Amar
#========================================================
import random
import sys
import re
from action import Action

class Agent:
    '''
    Abstract class.
    '''
    def choose_act(self, state):
        '''
        return legal action for the given state that the agent should perform.
        '''
        raise NotImplementedError()

class AlphaBetha(Agent):
    # The searching depth of the alpha-beta. Note that the depth decrease only on opponents turns
    # therefor the actual depth in the game tree is TWICE the value of ALPHA_BETA_DEPTH.
    ALPHA_BETA_DEPTH = 2

    @staticmethod
    def __runAB(eval_func, state):
        acts_res = []
        for act in state.get_legal_actions():
            successor_state = state.generate_successor(act)
            acts_res.append((act, AlphaBetha.__min_val_ab(eval_func, successor_state, AlphaBetha.ALPHA_BETA_DEPTH)))
        _, best_val = max(acts_res, key=lambda x: x[1])
        return random.choice([best_action for best_action, val in acts_res if val == best_val])
    @staticmethod
    def __min_val_ab(eval_func, state, depth, alpha=-sys.maxint, beta=sys.maxint):
        if AlphaBetha.__terminal_test(state, depth):
            return eval_func(state)
        val = sys.maxint
        for act in state.get_legal_actions():
            successor_state = state.generate_successor(act)
            val = min(val, AlphaBetha.__max_val_ab(eval_func, successor_state, depth - 1, alpha, beta))
            if val <= alpha:
                return val
            beta = min(beta, val)
        return val
    @staticmethod
    def __max_val_ab(eval_func, state, depth, alpha=-sys.maxint, beta=sys.maxint):
        if AlphaBetha.__terminal_test(state, depth):
            return eval_func(state)
        val = -sys.maxint
        for act in state.get_legal_actions():
            successor_state = state.generate_successor(act)
            val = max(val, AlphaBetha.__min_val_ab(eval_func, successor_state, depth, alpha, beta))
            if val >= beta:
                return val
            alpha = max(alpha, val)
        return val
    @staticmethod
    def __terminal_test(state, depth):
        return state.is_terminal() or (depth == 0)

    def __init__(self, heuristic, player_obj):
        self._eval_func = heuristic.get_evaluate_function(player_obj)

    def choose_act(self, state):
        return AlphaBetha.__runAB(self._eval_func, state)

class GreedyAgent(Agent):
    '''
    This agent return the best action by some evaluate function WITHOUT looking on
    next turns.
    '''
    def __init__(self, heuristic, player_obj):
        self._eval_func = heuristic.get_evaluate_function(player_obj)

    def choose_act(self, state):
        acts_vals = [(act, self._eval_func(state.generate_successor(act))) for act in state.get_legal_actions()]
        _, best_val = acts_vals[0]
        for act, val in acts_vals:
            if val > best_val:
                best_val = val
        return random.choice([act for act,val in acts_vals if val==best_val])

class ReflexAgent(Agent):
    '''
    That agent returns the first legal action found.
    '''
    def choose_act(self, state):
        return state.get_legal_actions()[0]

class RandomAgent(Agent):
    '''
    That agent choose action randomly among the available legal actions.
    '''
    def choose_act(self, state):
        return random.choice(state.get_legal_actions())

class HumanAgent(Agent):
    '''
    That agent request the user to choose a valid move. (10 wrong inputs will terminate the program!)
    '''
    def choose_act(self, state):
        patt = r'[ ]*[0-8][ ]*,?[ ]*[0-8][ ]*'
        legal_acts = state.get_legal_actions()
        for attempt in range(10):
            try:
                user_in = raw_input(
                    "You are the %s player. Enter input: " % state.get_player()).strip()
                if user_in.lower() in ["quit", "q"]:
                    print 'Terminating by request...'
                    exit(0)
                if re.match(patt, user_in):
                    user_raw, user_col = (int(user_in[0]), int(user_in[-1]))
                    miniB_index = (user_raw / 3) * 3 + user_col / 3
                    inner_index = (user_raw % 3) * 3 + user_col % 3
                    act = Action(miniB_index, inner_index)
                    if not act in legal_acts:
                        print 'The move is illegal!'
                    else:
                        return act
                else:
                    print 'The input does not match the required pattern: %s' % patt
            except Exception as e:
                print 'Exception:', e
            print "Either enter a coordinate in the form 'r, c' where r and c are" \
                  " integers between 0 and 8, or enter 'quit' or 'q' to stop the game. Tries left: %d" % (9-attempt)
        print "User failed to enter valid input 10 times. Stopping the game."
        exit(1)

class GenericRandomJumpAgent(Agent):
    INITIAL_COUNTER = 3.0

    def __init__(self, another_agent_obj, random_jump_formula):
        '''
        random_jump_formula is a function which get a natural number and returns
        the probability for that number (i.e rational in [0,1])
        '''
        self.counter = GenericRandomJumpAgent.INITIAL_COUNTER
        self._agent = another_agent_obj
        self._probability_formula = random_jump_formula

    def choose_act(self, state):
        if self.__to_jump():
            return random.choice(state.get_legal_actions())
        return self._agent.choose_act(state)

    def get_counter(self):
        return int(self.counter)

    def reset_counter(self):
        self.counter = GenericRandomJumpAgent.INITIAL_COUNTER

    def get_probability_formula(self):
        return self._probability_formula

    def __to_jump(self):
        '''
        flip a coin with probability regarding the probability formula, and return
        True iff the coins says to choose action randomly, else chooses action using
        the inner agent object.
        Each call to that function increase the value of self.counter
        '''
        jump = random.random() < self._probability_formula(self.counter)
        self.counter += 0.1
        return jump
