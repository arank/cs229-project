#!/usr/bin/env python
# tic-tac-toe optimal solver implementation from http://cwoebker.com/posts/tic-tac-toe


import random
from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer


class Tic(object):
    winning_combos = (
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6])

    winners = ('X-win', 'Draw', 'O-win')

    def __init__(self, squares=[]):
        if len(squares) == 0:
            self.squares = [None for i in range(9)]
        else:
            self.squares = squares

    def getBoard(self):
        newboard = []
        for x in self.squares:
            if x == 'X':
                newboard.append(1)
            elif x == 'O':
                newboard.append(-1)
            else:
                newboard.append(0)
        return newboard
    def show(self):
        for element in [self.squares[i:i + 3] for i in range(0, len(self.squares), 3)]:
            print element

    def available_moves(self):
        """what spots are left empty?"""
        return [k for k, v in enumerate(self.squares) if v is None]

    def available_combos(self, player):
        """what combos are available?"""
        return self.available_moves() + self.get_squares(player)

    def complete(self):
        """is the game over?"""
        if None not in [v for v in self.squares]:
            return True
        if self.winner() != None:
            return True
        return False

    def X_won(self):
        return self.winner() == 'X'

    def O_won(self):
        return self.winner() == 'O'

    def tied(self):
        return self.complete() == True and self.winner() is None

    def winner(self):
        for player in ('X', 'O'):
            positions = self.get_squares(player)
            for combo in self.winning_combos:
                win = True
                for pos in combo:
                    if pos not in positions:
                        win = False
                if win:
                    return player
        return None

    def get_squares(self, player):
        """squares that belong to a player"""
        return [k for k, v in enumerate(self.squares) if v == player]

    def make_move(self, position, player):
        """place on square on the board"""
        self.squares[position] = player

    def alphabeta(self, node, player, alpha, beta):
        if node.complete():
            if node.X_won():
                return -1
            elif node.tied():
                return 0
            elif node.O_won():
                return 1
        for move in node.available_moves():
            node.make_move(move, player)
            val = self.alphabeta(node, get_enemy(player), alpha, beta)
            node.make_move(move, None)
            if player == 'O':
                if val > alpha:
                    alpha = val
                if alpha >= beta:
                    return beta
            else:
                if val < beta:
                    beta = val
                if beta <= alpha:
                    return alpha
        if player == 'O':
            return alpha
        else:
            return beta


def determine(board, player):
    a = -2
    choices = []
    if len(board.available_moves()) == 9:
        return 4
    for move in board.available_moves():
        board.make_move(move, player)
        val = board.alphabeta(board, get_enemy(player), -2, 2)
        board.make_move(move, None)
        #print "move:", move + 1, "causes:", board.winners[val + 1]
        if val > a:
            a = val
            choices = [move]
        elif val == a:
            choices.append(move)
    #print choices
    return random.choice(choices)


def get_enemy(player):
    if player == 'X':
        return 'O'
    return 'X'

def to_feature_vector(board):
    vec = []
    for move in board.squares:
        if move is None:
            vec.append(0)
        elif move == 'X':
            vec.append(1)
        elif move == 'O':
            vec.append(2)
            
    return vec

def from_feature_vector(moves):
    vec = []
    for move in moves:
        if move == 0:
            vec.append(None)
        elif move == 1:
            vec.append('X')
        elif move == -1:
            vec.append('O')
            
    return vec



if __name__ == "__main__":
    configs = []
    decisions = []
    for i in range(1000):
        board = Tic()
        #board.show()
        #print board.getBoard()

        while not board.complete():
            player = 'X'
            #player_move = int(raw_input("Next Move: ")) - 1
            player_move = random.randint(0,8)
            if not player_move in board.available_moves():
                continue
            board.make_move(player_move, player)
            #board.show()

            if board.complete():
                break
            player = get_enemy(player)
            configs.append(board.getBoard())

            computer_move = determine(board, player)
            decisions.append(computer_move)
            board.make_move(computer_move, player)
            #board.show()
        print "winner is", board.winner()
        
    print len(configs)




    dataset = ClassificationDataSet(9)
    for i in range(len(configs)):
        dataset.appendLinked(configs[i], [decisions[i]])
    dataset._convertToOneOfMany()


    fnn = buildNetwork(9, 9, 9, outclass=SoftmaxLayer)
    trainer = BackpropTrainer( fnn, dataset=dataset, momentum=0.1, verbose=True, weightdecay=0.01)
    for i in range(100):
        trainer.trainEpochs(1)

    prediction_moves = trainer.testOnClassData()
    #print prediction_moves
    computer_moves = []

    #print "Now for the computer moves"
    print "Determining the predicted moved and the computer's moves..."
    for config in configs:
        config = from_feature_vector(config)
        board = Tic(squares = config)
        #print "Board is: "
        player = 'O'
        #board.show()
        computer_move = determine(board, player)
        computer_moves.append(computer_move)
        #print "Computer move"
        #print computer_move

    print prediction_moves
    print computer_moves













def to_feature_vector(board):
    vec = []
    for move in board.squares:
        if move is None:
            vec.append(0)
        elif move == 'X':
            vec.append(1)
        elif move == 'O':
            vec.append(2)
            
    return vec


