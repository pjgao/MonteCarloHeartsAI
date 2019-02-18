from math import log, sqrt
from random import randint
from random import choice
from Hand import Hand
import datetime
import copy
from Variables import *
import Variables
import sys

class MonteCarlo:
    def __init__(self, gameState, name, **kwargs):
        self.gameState = gameState
        self.ai = name
        self.aiplayer = None
        for p in gameState.players:
            if p.name == name:
                self.aiplayer = p
        self.states = []
        seconds = kwargs.get('time', Variables.monteCarloTime)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_moves = kwargs.get('max_moves',100)
        self.max_depth = 0

        self.wins = {}
        self.plays = {}
        self.C = kwargs.get('C', 1.4)

        #parameters
        self.threshold_difference = 13

    def redistribute(self, board):
        cards = []
        numOfCards = {}
        for player in board.players:
            if player.name != self.ai:
                num = 0
                for suit in player.hand.hand:
                    cards = cards + suit
                    num += len(suit)
                numOfCards[player.name] = num
        #distribute randomly
        for player in board.players:
            if player.name != self.ai:
                hand = Hand()
                for x in range(numOfCards[player.name]):
                    index = randint(0,len(cards)-1)
                    cardAdd = cards[index]
                    cards.remove(cardAdd)
                    hand.addCard(cardAdd)
                player.hand = hand

    def update(self, state):
        self.states.append(state)

    def getPlay(self):

        self.max_depth = 0
        player = self.aiplayer
        legal = self.gameState.getLegalPlays(player)

        # 得分处理
        min_score = sys.maxsize
        max_score = -sys.maxsize - 1
        for p in self.gameState.players:
            if p.score < min_score:
                min_score = p.score
            if p.score > max_score:
                max_score = p.score
        if player.score - min_score >= self.threshold_difference or \
           max_score - player.score >= self.threshold_difference:
            self.useRoundScoreOnly = True
        else:
            self.useRoundScoreOnly = False

        # 如果只剩一张牌，不再模拟直接返回
        if len(legal) == 0:
            return -1
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        # 模拟一定时间，将结果存在self.plays, self.wins，根据模拟情况计算获胜概率
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.runSimulation()
            games += 1

        moves_states = []
        for p in legal:
            legalState = self.gameState.cardsPlayed + (p,)
            moves_states.append((p, legalState))

        #Pick the move with the highest percentage of wins.
        '''add wins equeal zero, random select
        '''
        if sum(self.wins.values())==0:
            move = choice(legal)
        else:
            percent_wins, move = max(
                (self.wins.get((player, S), 0) /
                self.plays.get((player, S), 1),
                p) 
                for p, S in moves_states
            )

        return move

    def runSimulation(self):
        # 将原来牌局的状态全部复制下来，进行模拟出牌，得到模拟结果
        plays, wins = self.plays, self.wins

        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        board = copy.deepcopy(self.gameState)
        
        #self.redistribute(board)

        expand = True
        mcard = []
        for t in range(self.max_moves):
            # 一直循环直到出完所有的牌
            player = board.getCurrentPlayer()
            legal = board.getLegalPlays(player)

            if not legal:
                break

            moves_states = []
            for p in legal:
                legalState = board.cardsPlayed + (p,)
                moves_states.append((p, legalState))
            pass
            #if stats available on all legal moves, use them
            #all moved states[(4c,(2c,3c,4c))] in plays' key(('ai1',(2c,3c,4c)):4)
            if all(plays.get((player, S)) for p, S in moves_states):
                # If we have stats on all of the legal moves here, use them.
                log_total = log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                     self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else: 
                #make arbitrary decision
                move, state = choice(moves_states)
                mcard.append(move)
            board.step(move, player, True)
            state = board.cardsPlayed
            states_copy.append(state)

            if expand and (player, state) not in self.plays:
                expand = False
                self.plays[(player, state)] = 0
                self.wins[(player, state)] = 0
                if (t > self.max_depth):
                    self.max_depth = t
            visited_states.add((player,state))

            winners = None
            if self.useRoundScoreOnly:
                winners = board.winningPlayers
            else:
                if board.winningPlayer is not None:
                    winners = [board.winningPlayer]

            if winners: # 所有牌出完，某位玩家胜出，该次模拟结束
                break
        if not winners:
            print('error:')
            print(player,[[i,j] for i,j in enumerate(board.cardsPlayed)],legal)
            print(board.getLegalPlays(player),board.cardsPlayedbyPlayer[player])
            print(board.allTricks)
            print([pl.roundscore for pl in board.players])
            print(t,winners)
        for player, state in visited_states: # 将本次模拟的结果添加到MonteCarlo类的plays和wins中
            if (player, state) not in self.plays:
                continue
            self.plays[(player, state)] += 1
            if player in winners:
                self.wins[(player,state)] += 1
        return


