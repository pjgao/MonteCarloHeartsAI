'''
类含义：当前回合出的牌
用来计算当前花色、最大牌，得分情况
'''

from Card import Card, Suit
import time
#from Variables import *
import Variables

hearts = 3 # the corresponding index to the suit hearts
spades = 2
queen = 12


class Trick:
	def __init__(self):
		self.trick = [0, 0, 0, 0]
		self.suit = Suit(-1)
		self.cardsInTrick = 0
		self.points = 0
		self.highest = 0 # rank of the high trump suit card in hand
		self.winner = -1

	def reset(self):
		self.trick = [0, 0, 0, 0]
		self.suit = -1
		self.cardsInTrick = 0
		self.points = 0
		self.highest = 0
		self.winner = -1

	# def cardsInTrick(self):
	# 	count = 0
	# 	for card in self.trick:
	# 		if card is not 0:
	# 			count += 1
	# 	return count

	def isUnset(self):
		return self.cardsInTrick == 0

	def setTrickSuit(self, card):
		self.suit = card.suit

	def addCard(self, card, index): # 出了一张牌或者初始化的时候，更新状态

		if self.cardsInTrick == 0: # if this is the first card added, set the trick suit
			self.setTrickSuit(card)

		self.trick[index] = card
		self.cardsInTrick += 1

		if card.suit == Suit(hearts):
			self.points += 1
		elif card == Card(queen, spades):
			self.points += 13

		if card.suit == self.suit:
			if card.rank.rank > self.highest:
				self.highest = card.rank.rank
				self.winner = index

	def getCurrentPlayer(self,trickWinner): # 从已出牌中判断该谁出牌了

		trick = self.trick
		ind = trickWinner
		if trick[ind] is 0:
			return ind
		count = 0
		while trick[ind] is not 0 and count < 4:
			ind = (ind + 1) % 4
			count += 1
		if count == 4:
			return -1
		else:
			return ind