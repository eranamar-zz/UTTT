#===================================================
#       Action class
#       Created by: Adi Ben Binyamin
#                   Eran Amar
#===================================================

class Action():
    def __init__(self, miniB_i, inner_i):
        self.miniB_index = miniB_i
        self.inner_index = inner_i

    def __str__(self):
        miniB_row, miniB_col = self.miniB_index / 3, self.miniB_index % 3
        inner_row, inner_col = self.inner_index / 3, self.inner_index % 3
        return 'miniB: (%d, %d), inside: (%d, %d)' % (
            miniB_row, miniB_col, inner_row, inner_col)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)
