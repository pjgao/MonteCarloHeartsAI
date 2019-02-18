'''
游戏类，具体出牌操作在player类，该类用于更新状态，统计得分等来维持游戏
'''
from Deck import Deck
from Card import Card, Suit, Rank
from Player import Player
from Trick import Trick
from PlayerTypes import PlayerTypes
from Variables import hearts,spades,queen,totalTricks      
#import Variables
import random


class Hearts:
    def __init__(self):
        oneMonte_threeNaive_anon = [Player("AI 1  ", PlayerTypes.NaiveMinAI, self), Player("AI 2 ", PlayerTypes.MonteCarloAI, self),
                                                               Player("AI 3  ", PlayerTypes.NaiveMinAI, self), Player("AI 4  ", PlayerTypes.NaiveMaxAI, self)]
        thePlayers = oneMonte_threeNaive_anon
        #Shake up the order
        random.shuffle(thePlayers)
        self.players = thePlayers
        self.allTricks = []
        self.currentTrick = Trick()
        self.trickWinner = -1

        self.cardsPlayed = () #keep track of state in a tuple
        temp = dict.fromkeys(thePlayers)
        for key in temp:
            temp[key] = []
        self.cardsPlayedbyPlayer = temp
        self.shift = 0
        self.winningPlayer = None
        self.winningPlayers = None

        self.humanExists = False


        self.roundNum = 0
        self.trickNum = 0 # initialization value such that first round is round 0
        self.dealer = -1 # so that first dealer is 0
        #self.passes = [1, -1, 2, 0] # left, right, across, no pass


        self.heartsBroken = False
        self.losingPlayer = None

        # Generate a full deck of cards and shuffle it
        # # else:
        # 	self = copy.deepcopy(orig)
        #return flat array of cards
    def getLegalPlays(self, player):
        if player.type == PlayerTypes.MonteCarloAI:            
            validHand = []
            for suit in range(0,4):
                handSuit = player.hand.hand[suit]
                for card in handSuit:
                    if self.isValidCard(card,player):
                        validHand.append(card)            
        else:
            monterCards = sum(self.players[0].hand.hand,[])
            playedCards = self.cardsPlayed
            d = Deck()
            validHand = [i for i in d.deck if i not in monterCards+list(playedCards)]
        #print('player:',player.name,'vali:',validHand)
        return validHand
    def getCurrentPlayer(self):	
        return self.players[self.currentTrick.getCurrentPlayer(self.trickWinner)]
    def step(self, card, player, monteCarlo = False):
        #add card to state
        self.cardsPlayed = self.cardsPlayed + (card,)
        self.cardsPlayedbyPlayer[player].append(card)

        player.removeCard(card)
        start = (self.trickWinner + self.shift) % len(self.players)
        self.currentTrick.addCard(card, start)
        self.shift += 1
        if self.shift == 4:
            self.evaluateTrick()
            self.trickNum += 1
            self.shift = 0
            #end game and evaluate winner if round is over
            if monteCarlo:
                if (self.trickNum >= totalTricks):
                    self.winningPlayers = self.roundWinners()
                    self.handleScoring()
                    self.winningPlayer = self.getWinner()

    def isValidCard(self, card, player):
        if card is None:
            return False

        # if it is not the first trick and no cards have been played:
        if self.trickNum != 0 and self.currentTrick.cardsInTrick == 0:
            if card.suit == Suit(hearts) and not self.heartsBroken:
                if not player.hasOnlyHearts():
                    return False
        #Can't play hearts or queen of spades on first hand
        if self.trickNum == 0:
            if card.suit == Suit(hearts):
                return False
            elif card.suit == Suit(spades) and card.rank == Rank(queen):
                return False
        return True


    def evaluateTrick(self):
        self.trickWinner = self.currentTrick.winner
        p = self.players[self.trickWinner]
        p.trickWon(self.currentTrick)
        self.allTricks.append(self.currentTrick.trick)
        self.currentTrick = Trick()

    def roundWinners(self):
        winners = []
        for player in self.players:
            if player.roundscore == 26:
                #shotMoon = True
                winners.append(player)
                return winners

        minScore = 200 # impossibly high
        winner = None
        for p in self.players:
            if p.roundscore < minScore:
                winner = p
                minScore = p.roundscore

        winners.append(winner)
        #check for a draw
        for p in self.players:
            if p != winner and p.roundscore == minScore:
                winners.append(p)
        return winners

    def handleScoring(self):
        p, highestScore = None, 0
        shotMoon = False
        for player in self.players:
            if player.roundscore == 26:
                shotMoon = True
        for player in self.players:
            if shotMoon and player.roundscore != 26:
                player.score += 26
            elif not shotMoon:
                player.score += player.roundscore
            player.roundscore = 0
            if player.score > highestScore:
                p = player
                highestScore = player.score
            self.losingPlayer = p
    def getWinner(self):
        minScore = 200 # impossibly high
        winner = None
        for p in self.players:
            if p.score < minScore:
                winner = p
                minScore = p.score
        return winner
    def getFirstTrickStarter(self):
        for i,p in enumerate(self.players):
            if p.hand.contains2ofclubs:
                self.trickWinner = i
