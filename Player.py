'''
玩家类，该类中定义了用于模特卡罗模拟的策略的类型，通过添加不同的策略可以提高模拟的表现
'''
from random import randint, choice
from Hand import Hand
from PlayerTypes import PlayerTypes
from MonteCarlo import MonteCarlo
from Card import Card,Suit,Rank
import sys
from Variables import hearts,spades,queen
class Player:
	def __init__(self, name, player_type, game, player=None):
		if player is not None:
			self.name = player.name
			self.hand = player.hand
			self.score = player.score
			self.roundscore = player.roundscore
			self.tricksWon = player.tricksWon
			self.type = player.type
			self.gameState = player.gameState
			
		else:
			self.name = name
			self.hand = Hand()
			self.score = 0
			self.roundscore = 0
			self.tricksWon = []
			self.type = player_type
			self.gameState = game

	def __eq__(self, other):
		return self.name == other.name

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		return hash(repr(self))

	def addCard(self, card):
		self.hand.addCard(card)

	# 随机选则一张可以出的牌
	def randomPlay(self): 
		return choice(self.gameState.getLegalPlays(self))		
	# 出大牌
	def naiveMaxAIPlay(self): 
		gameState = self.gameState
		validClubs = []
		validDiamonds = []
		validSpades = []
		validHearts = []

		validHand = [validClubs, validDiamonds, validSpades, validHearts]
		for suit in range(0,4):
			handSuit = self.hand.hand[suit]
			for card in handSuit:
				if gameState.isValidCard(card,self):
 					validHand[suit].append(card)

		#if first, play highest card in a random suit
		if gameState.currentTrick.isUnset():
			if gameState.heartsBroken == True or self.hasOnlyHearts():
			  suitRange = 3
			else:
				suitRange = 2
			randomSuit = randint(0,suitRange)
			return Hand.highestCard(validHand[randomSuit])
		#if not first:
		else:
			# print("Not going first!")
			trickSuit = gameState.currentTrick.suit.iden
			#if there are cards in the trick suit play highest card in trick suit
			if(len(validHand[trickSuit]) > 0):
				# print("Still cards in trick suit")
				return Hand.highestCard(validHand[trickSuit])
			else:
				# print("No cards in trick suit")

				#play cards by points, followed by rank
				minPoints = sys.maxsize
				minCard = None
				for suit in range(0,4):
					for card in validHand[suit]:
						cardPoints = -card.rank.rank
						if card.suit == Suit(hearts):
							cardPoints -= 15 #Greater than rank of all non-point cards
						if card.suit == Suit(spades) and card.rank == Rank(queen):
							cardPoints -= 13
						if cardPoints < minPoints:
							minPoints = cardPoints
							minCard = card
				return minCard

		#should never get here
		#raise Exception("failed programming")
		#return None

	# 尽量避免获得牌权
	def naiveMinAIPlay(self):
		#get list of valid cards
		gameState = self.gameState
		validClubs = []
		validDiamonds = []
		validSpades = []
		validHearts = []

		validHand = [validClubs, validDiamonds, validSpades, validHearts]
		for suit in range(0,4):
			handSuit = self.hand.hand[suit]
			for card in handSuit:
				if gameState.isValidCard(card,self):
 					validHand[suit].append(card)

 		# self.print_hand(validHand)

		#if first, play lowest card in a random suit
		if gameState.currentTrick.isUnset():
			# print("Going first!")
			#include hearts if hearts not broken or only has hearts
			if gameState.heartsBroken == True or self.hasOnlyHearts():
			  suitRange = 3
			else:
				suitRange = 2
			randomSuit = randint(0,suitRange)
			#return lowest card
			# print("Current trick suit is: ", gameState.currentTrick.suit.iden)
			# print("Going first and playing lowest card")
			return Hand.lowestCard(validHand[randomSuit])
		#if not first:
		else:
			# print("Not going first!")
			trickSuit = gameState.currentTrick.suit.iden
			#if there are cards in the trick suit play lowest card in trick suit
			if(len(validHand[trickSuit]) > 0):
				# print("Still cards in trick suit")
				return Hand.lowestCard(validHand[trickSuit])
			else:
				# print("No cards in trick suit")

				#play cards by points, followed by rank
				maxPoints = -sys.maxsize
				maxCard = None
				for suit in range(0,4):
					for card in validHand[suit]:
						cardPoints = card.rank.rank
						if card.suit == Suit(hearts):
							cardPoints += 15 #Greater than rank of all non-point cards
						if card.suit == Suit(spades) and card.rank == Rank(queen):
							cardPoints += 13
						if cardPoints > maxPoints:
							maxPoints = cardPoints
							maxCard = card
				return maxCard

	# 模特卡罗模拟
	def monteCarloAIPlay(self):
		mcObj = MonteCarlo(self.gameState, self.name)
		mcObj.update(self.gameState.cardsPlayed)
		card = mcObj.getPlay()
		return card

	# 出牌框架
	def play(self, option='play', c=None, auto=False):
		card = None
		if c is not None:
			card = c
			card = self.hand.playCard(card)
		#elif self.type == PlayerTypes.Human:
			#card = self.humanPlay(option)
		elif self.type == PlayerTypes.Random:
			card = self.randomPlay()
		elif self.type == PlayerTypes.NaiveMinAI:
			card = self.naiveMinAIPlay()
		elif self.type == PlayerTypes.NaiveMaxAI:
			card = self.naiveMaxAIPlay()
		elif self.type == PlayerTypes.MonteCarloAI:
			card = self.monteCarloAIPlay()
		return card

	def trickWon(self, trick): # 赢牌后更新得分
		self.roundscore += trick.points


	def hasSuit(self, suit):
		return len(self.hand.hand[suit.iden]) > 0

	def removeCard(self, card):
		self.hand.removeCard(card)

	def hasOnlyHearts(self):
		return self.hand.hasOnlyHearts()	