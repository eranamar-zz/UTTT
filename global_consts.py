#=======================================================
#       global_consts.py
#       Created by: Adi Ben Binyamin
#                   Eran Amar
#========================================================

X_PLAYER = 'x'
Y_PLAYER = 'o'
EMPTY = '.'
SPACE = ' '
RANDOMNESS_SUFFIX = '#R'
RANDOM_FORMULA = lambda p: (5.0/(p**2))
USAGE = '''Usage: python uttt_game_engine.py <x_player_string> <o_player_string>

You may choose any players from the options below (case sensitive):
  Player String:          Description:
    human           the user chooses the moves
    random          chooses moves randomly
    reflex          choose the most top-left available cell
    MM_Cells#R      Minimax player (with CellsWeightHeu) & random jump optimization
    MM_Cells        Minimax player (with CellsWeightHeu)
    MM_Recursive#R  Minimax player (with RecursiveWeightHeu) & random jump optimization
    MM_Recursive    Minimax player (with RecursiveWeightHeu)
    MM_Winning#R    Minimax player (with WinningPossibilitiesHeu)
    MM_Winning      Minimax player (with WinningPossibilitiesHeu) & random jump optimization
    G_Cells         Greedy player with CellsWeightHeu
    G_Recursive     Greedy player with RecursiveWeightHeu
    G_Winning       Greedy player with WinningPossibilitiesHeu'''        