#!/usr/bin/env python
# tic-tac-toe optimal solver implementation from http://cwoebker.com/posts/tic-tac-toe

import numpy as np
import random
from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer
import cPickle as pickle

numGamesForTraining = 1000
numEpochsForTraining = 100

# if usePriorNetwork = False, then the newly trained network will be saved in fileNameForNetworkSavingLoading
# if usePriorNetwor = True, then the network will be loaded from fileNameForNetworkSavingLoading
usePriorNetwork = True
fileNameForNetworkSavingLoading = "trainednetwork"


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
    
    # create a Feed-Forward Neural Network
    fnn = buildNetwork(9, 9, 9, outclass=SoftmaxLayer)

    # Load the Network from Memory if desired
    if (usePriorNetwork):
        fileObject = open(fileNameForNetworkSavingLoading,'r')
        fnn = pickle.load(fileObject)

    # If not loading from memory, train the network
    else:
        
        # loop over all of the games
        for i in range(numGamesForTraining):
            # initialize a new game
            board = Tic()
            
            # loop until the game is complete
            while not board.complete():
                player = 'X'
                
                # add the board configuration and resultant best-move to the training set
                configs.append(board.getBoard())
                player_move = determine(board, player)
                decisions.append(player_move)
                
                # makes sure the player move is valid
                if not player_move in board.available_moves():
                    continue
                board.make_move(player_move, player)

                if board.complete():
                    break
                
                # switch to the other player
                player = get_enemy(player)

                # add the board configuation and resultant best-move to the training set
                configs.append(board.getBoard())
                computer_move = determine(board, player)
                decisions.append(computer_move)

                board.make_move(computer_move, player)
            
            print "winner is", board.winner()
            
        # create a classification dataset from the input values
        dataset = ClassificationDataSet(9, nb_classes=9)
        for i in range(len(configs)):
            dataset.appendLinked(configs[i], [decisions[i]])
        dataset._convertToOneOfMany()

        # use backpropogation to train the neural network
        trainer = BackpropTrainer( fnn, dataset=dataset, momentum=0.1, verbose=True, weightdecay=0.01)
        for i in range(numEpochsForTraining):
            trainer.trainEpochs(1)
        # print predictions on the training data- not actually used for anything
        prediction_moves = trainer.testOnClassData()

        # save the network to the specified file to save time later if not retraining
        fileObject = open(fileNameForNetworkSavingLoading, 'w')
        pickle.dump(fnn, fileObject)
        fileObject.close()

    computer_moves = []


    # this loop is just for testing purposes - just to see how different the learned network generally behaves
    print "Determining the predicted moves and the computer's moves..."
    for config in configs:
        config = from_feature_vector(config)
        board = Tic(squares = config)

        player = 'O'

        computer_move = determine(board, player)
        computer_moves.append(computer_move)

    configs = []
    decisions = []
    
    # In this stage, we play the ideal solver against the learned neural network, and count the number of draws, wins and losses
    # note, it is not possible to win against the computer - so really we are trying to find the number of draws
    winners = []
    numGames = 100
    for i in range(numGames):
        board = Tic()
        
        # play until someone wins the game
        while not board.complete():
            player = 'X'
            #datasettmp = ClassificationDataSet(9, nb_classes=9)
            #datasettmp.appendLinked(board.getBoard(), [0])
            
            # get the activations for a given board state
            activation = fnn.activate(board.getBoard())
            activation = np.array(activation)

            # argsort activations from greatest to least
            order_of_attempts = np.argsort((-1)*activation)
            attempt = 0
            
            # keep picking moves from highest to least activation until an available one is found
            player_move = order_of_attempts[attempt]
            while player_move not in board.available_moves():
                attempt += 1
                player_move = order_of_attempts[attempt]

            print player_move

            board.make_move(player_move, player)
            #board.show()

            if board.complete():
                break
            
            # let the computer make its move
            player = get_enemy(player)
            configs.append(board.getBoard())

            computer_move = determine(board, player)

            decisions.append(computer_move)

            board.make_move(computer_move, player)

        print "winner is", board.winner()
        winners.append(board.winner())
    
    # calculate the number of wins for each
    Xwins = [win for win in winners if win == 'X']
    numXwins = len(Xwins)
    Owins = [win for win in winners if win == 'O']
    numOwins = len(Owins)

    print "Number of times Neural Net won is ", numXwins, " out of ", numGames
    print "Number of times Optimal Solver won is ", numOwins, " out of ", numGames
    print "Number of Draws is ", numGames - numXwins - numOwins, " out of ", numGames




