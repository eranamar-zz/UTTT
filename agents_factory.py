#=======================================================
#       agents_factory.py
#       Created by: Adi Ben Binyamin
#                   Eran Amar
#========================================================
from agents_pool import *
from heuristics import *
from global_consts import *


def player_for_agent_attacher(agent_type, heuristic):
    return lambda player_obj: agent_type(heuristic, player_obj)

# The names format is <agent_type>_<heu>_<random/deterministic>
AGENTS = {
                # Basic agents:
        'human':    lambda player_obj: HumanAgent(),
        'random':   lambda player_obj: RandomAgent(),
        'reflex':   lambda player_obj: ReflexAgent(),

        # --------------------------------------------------------
                # Minimax agents no randomness:
        'MM_Winning':   player_for_agent_attacher(AlphaBetha,WinningPossibilitiesHeu),
        'MM_Cells':     player_for_agent_attacher(AlphaBetha,CellsWeightHeu),
        'MM_Recursive': player_for_agent_attacher(AlphaBetha,RecursiveWeightHeu),

        # --------------------------------------------------------
                # Minimax agents WITH randomness:
        'MM_Winning#R':     None,
        'MM_Cells#R':       None,
        'MM_Recursive#R':   None,

        # --------------------------------------------------------
                # Greedy agents no randomness:
        'G_Winning':    player_for_agent_attacher(GreedyAgent,WinningPossibilitiesHeu),
        'G_Cells':      player_for_agent_attacher(GreedyAgent,CellsWeightHeu),
        'G_Recursive':  player_for_agent_attacher(GreedyAgent,RecursiveWeightHeu),

}

def AgentFactory(type_name, player_obj):
    if not type_name in AGENTS.keys():
        print 'Error! there is no such agent "%s".' % type_name
        print USAGE
        from sys import exit
        exit(1)
    base_type = type_name.replace(RANDOMNESS_SUFFIX, '')
    base_agent = (AGENTS[base_type])(player_obj)
    if RANDOMNESS_SUFFIX in type_name:
        return GenericRandomJumpAgent(base_agent, RANDOM_FORMULA)
    return base_agent

