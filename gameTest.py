'''
该文件简单的创建了Card, Deck, Player, Game类，Game类中auto_play函数使用了1个MonteCarloAI和3个相同的规则策略完成了13回合的游戏
@author: pipixiu
@time: 2018.9.30
@city: Nanjing
'''

from encapsule import MonteCarloPlay
import random
import collections

Card = collections.namedtuple('Card', ['point', 'suit']) 
'''
使用namedtuple创建Card类型，包含point,suit两个属性
point: 纸牌点数, 2-14, 11为J, 12为Q, 13为K,14为A
suit: 纸牌花色，梅花:0, 方块:1, 黑桃:2, 红桃:3
使用：spadeQ: Card(12,2)
'''

def card2chinese(card):
    '''
    将某张牌类转换为中文可读
    __input:
    card: Card类型
    __output:
    str类型，牌的中文名称
    '''
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = '梅花 方块 黑桃 红桃'.split()
    return suits[card.suit] + ranks[card.point - 2]

class Deck:
    #牌堆类，一堆52张牌
    def __init__(self):
        # 建立牌堆
        card = []
        for i in range(4):
            for j in range(13):
                card.append(Card(j + 2, i))
        self.card = card

    def shuffle(self):
        # 洗牌
        random.shuffle(self.card)

    def deal(self, n=4):
        # 发牌，分四份
        if not len(self.card):
            print('no cards')
            return [[] * n]
        p = []
        for i in range(n):
            p.append((self.card[len(self.card) // n * i:len(self.card) // n * (i + 1)]))
        return p


class Player:
    # 玩家类
    def __init__(self, player_id, hand=[]):        
        self.player_id = player_id
        self.hand = hand # 玩家手牌

    def sortHand(self):  # 整理，排序手发到的牌
        self.hand.sort(key=lambda x: (x.suit, x.point))

    def sortSuit(self):
        # 将剩余的牌按花色分类，便于后续的出牌的判断
        club = []
        diamond = []
        spade = []
        heart = []
        for i in range(len(self.hand)):
            if self.hand[i].suit == 0:
                club.append(i)
            elif self.hand[i].suit == 1:
                diamond.append(i)
            elif self.hand[i].suit == 2:
                spade.append(i)
            elif self.hand[i].suit == 3:
                heart.append(i)
        return [club, diamond, spade, heart]


class Game:
    # 游戏类,该类中封装了一个规则玩牌函数PlayCards，和传牌函数TransferThreeCards
    # find_first, choose_card, split_by_suit都是上述两函数用到的
    # getScoreFromGame是从游戏记录中history_P0以及history中统计得分情况
    # auto_play为一局13个回合的游戏函数，游戏过程将会打印出来
    def __init__(self):
        self.deck = Deck()
        self.players = [None]*4
        self.history = [[], [], [], []] # 四个玩家已经出的牌
        self.history_P0 = [] # 每轮先出的玩家的index
        self.deck.shuffle()
        # 先洗牌

        for player_id, one_deck in enumerate(self.deck.deal()):
            self.players[player_id] = Player(player_id, one_deck)
            # 发牌
        self.players[0].sortHand()
        self.players[1].sortHand()
        self.players[2].sortHand()
        self.players[3].sortHand()
        # 排序手中的牌

    def find_first(self):
        '''
        从已出牌中判断该谁先出牌
        '''
        first_id = 0
        if not self.history_P0: # 如果还未出牌，则有梅花2的先出
            for player_id in range(4):
                if self.players[player_id].hand[0] == Card(2, 0):
                    first_id = player_id
        else: # 找到上回合得到出牌权的玩家
            last_first = self.history_P0[-1]
            card_max = self.history[last_first][-1]
            for i in range(4):
                now_card = self.history[(last_first + i) % 4][-1]
                if now_card.suit == card_max.suit and now_card.point > card_max.point:
                    card_max = now_card
                    first_id = (last_first + i) % 4
        return first_id

    def choose_card(self, suitsDeck, flag):
        '''
        传入待选择的几个花色，选出最大的值或者最小的值。(此时应可任选花色)
        suitsDeck: 不同花色牌的列表
        flag: 0,选最大; 1,选最小
        '''
        k = flag * 15
        m, pos = None, None
        for oneSuitDeck in suitsDeck:
            if len(oneSuitDeck) == 0:
                continue
            else:
                if flag == 1:
                    if oneSuitDeck[0].point <= k:  # 跨花色最最小的牌
                        pos = oneSuitDeck[0]  # 出最小
                        k = oneSuitDeck[0].point
                        m = oneSuitDeck
                elif flag == 0:
                    if oneSuitDeck[-1].point >= k:  # 跨花色选最大的牌
                        pos = oneSuitDeck[-1]
                        k = oneSuitDeck[-1].point
                        m = oneSuitDeck
        if m:
            m.remove(pos)
            return pos
        else:
            return None

    def split_by_suit(self, deck):
        '''
        将一摞牌按花色分摞
        '''
        a, b, c, d = [], [], [], []
        suitsDeck = [a, b, c, d]
        for card in deck:
            suitsDeck[card.suit].append(card)
        return suitsDeck

    # -------------传牌---出牌函数------------------------------

    def TransferThreeCards(self, deck):
        '''
        input:
        deck:         列表，当前玩家手中的13张牌，如：
                      deck = [Card(point=7, suit=0),Card(point=10, suit=3),Card(point=11, suit=3),...]
        output:
        transferCards:应当传出的三张牌
                      transferCards = [Card(point=7, suit=0),Card(point=10, suit=3),Card(point=11, suit=3)]
        '''
        deck = sorted(deck, key=lambda x: x.suit * 10 + x.point)
        kinds = self.split_by_suit(deck)
        select = []
        for i in range(3):  # 先选大于黑桃Q的AKQ
            if len(kinds[2]) != 0:  # 若有黑桃
                if kinds[2][-1].point >= 10:  #
                    select.append(kinds[2].pop())
            else:  #
                break
        for i in range(4):  # 再选红桃大于J的AKQJ
            if len(kinds[3]) != 0:
                if kinds[3][-1].point >= 9:
                    select.append(kinds[3].pop())
            else:
                break
        while len(select) < 3:  # 还不足三个的话，在梅花，方块里选最大的
            select.append(self.choose_card(kinds, 0))
        transferCards = [select[0], select[1], select[2]]
        return transferCards

    def PlayCards(self, deck, history_self, history_A, history_B, history_C, history_P0, REPLAY=False):
        '''
        输入一摞牌，选出最应该出的牌

        规则打牌的判断机制，对于自己第几个出，自己出牌前已经打出的牌，红桃牌，黑桃Q的打出情况，
        以及应该打出大小点等各类情况都进行判断，从而选出应当打出的最适合的牌。
        input:
        deck:           列表，当前玩家手中的牌，如：
                        deck = [Card(point=7, suit=0),Card(point=10, suit=3),Card(point=11, suit=3)]
        history_self:   同deck列表，当前玩家已出的牌
        history_A:      同deck列表，玩家A已出的牌
        history_B:      同deck列表，玩家B已出的牌
        history_C:      同deck列表，玩家C已出的牌
        history_P0:     列表，每个回合第一个发牌的人的index。当前玩家:0, A:1, B:2, C:3
                        如：history_P0 = [0,1,1]表示第一回合是当前玩家先出的牌，第二回合玩家1先出的牌，第三回合还是玩家1先出的牌
        REPLAY如果出牌不符合要求，则重新出牌    
        output:
        pos: Card类型，选出的最优的牌
        '''

        deck = sorted(deck, key=lambda x: x.suit * 10 + x.point)
        history = [history_self, history_A, history_B, history_C]

        # 从输入参数中计算每轮出的牌
        allTurnsCard = []
        for i, j in enumerate(history_P0):
            tmp = []
            for k in range(4):
                now = history[(j + k) % 4]
                if len(now) > i:
                    tmp.append([(j + k) % 4, now[i]])
            allTurnsCard.append(tmp)

        thisTurnOutCard = allTurnsCard[-1] if allTurnsCard and len(allTurnsCard[-1]) != 4 else []
        if thisTurnOutCard:
            maxCard = \
            max([i for i in thisTurnOutCard if i[1].suit == thisTurnOutCard[0][1].suit], key=lambda x: x[1].point)[1]
            print(maxCard)
        # outQueen = True if Card(12,2) in allTurnsCard else False
        outQueen = True if [outCard for turn in allTurnsCard for outCard in turn if
                            outCard[1] == Card(12, 2)] else False
        outHeart = True if [j for i in allTurnsCard for j in i if j[1].suit == 3] else False
        nowSuit = thisTurnOutCard[0][1].suit if thisTurnOutCard else None
        # print('queen:',outQueen,'heart:',outHeart)
        # 各花色已出牌数统计
        suit_numbers = list(map(lambda x: x.suit, sum(self.history, [])))
        suit_count_dict = {i: suit_numbers.count(i) for i in set(suit_numbers)}
        # print('thisTurn',thisTurnOutCard)
        kinds = self.split_by_suit(deck)  # 按花色分成四类排序
        if len(thisTurnOutCard) == 0:  # 如果是第一个出牌的
            if len(deck) == 13:  # 因为是第一回合且第一个出牌，最小的肯定是梅花2
                pos = deck[0]
            else:
                if (outHeart == False) and (deck[0].suit != 3):  # 如果红桃还没出，且当前最小值不是红桃
                    del kinds[3]  # 不能出红桃类
                if outQueen == False:
                    if (len(kinds[2]) == 0) or (kinds[2][-1].point >= 12):  # 没有黑桃或者黑桃最大值大于Q
                        pos = self.choose_card(kinds, 1)
                    else:  # 如果有小黑桃
                        pos = kinds[2][0]  # 出黑桃最小牌，拱猪
                else:  # 如果黑桃Q已出
                    pos = self.choose_card(kinds, 1)

        elif len(thisTurnOutCard) < 3:  # 如果电脑不是最后一个出的

            maxCard = 0
            for outCard in thisTurnOutCard:  # 对于每个出牌
                card = outCard[1]
                if card.suit == nowSuit:  # 找到这一轮花色的最大值
                    if card.point > maxCard:
                        maxCard = card.point
            if len(kinds[nowSuit]) == 0:  # 如果没有该花色，优先黑桃Q
                hasPig = False
                for spadeCard in kinds[2]:  # 黑桃中每个牌
                    if spadeCard.point == 12:  # 如果有黑桃Q
                        pos = spadeCard  # 打黑Q
                        HasPig = True
                        break
                if not hasPig:  # 如果没有黑Q
                    del kinds[nowSuit]  # 不出黑桃
                    pos = self.choose_card(kinds, 0)  # 在剩余的几个花色里选择最优的
                if len(deck) == 13:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 如果是黑Q或红桃，一直再找最优
                        pos = self.choose_card(kinds, 0)  # flag是0，选最大值
                        # card = per.hand[pos]
            else:  # 如果有该花色
                if len(deck) == 13:  # 如果是第一轮出牌
                    pos = kinds[0][-1]  # 第一轮出最大的牌，第一轮肯定是梅花，故suit0
                else:
                    bigpos = []
                    smallpos = []
                    for card in kinds[nowSuit]:  # 分为比当前回合最大牌大和比它小的两摞
                        if card.point > maxCard:
                            bigpos.append(card)
                        else:
                            smallpos.append(card)
                    if len(smallpos) != 0:  # 如果有小的
                        pos = smallpos[-1]  # 就出小的里面最大的
                    else:
                        pos = bigpos[0]  # 大牌里面最小的
                        if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                            pos = kinds[nowSuit][1]  # 如果没有小的，如果大的里面最小的是黑桃Q且大的有两张牌以上，选择比最小的大一的

        elif len(thisTurnOutCard) == 3:  # 如果该玩家最后一个出牌

            maxCard = 0  # 该花色最大的牌
            for outCard in thisTurnOutCard:
                card = outCard[1]  # 每个人出的牌
                if card.suit == nowSuit:
                    if card.point > maxCard:
                        maxCard = card.point
            if len(kinds[nowSuit]) == 0:  # 无该花色的牌
                hasPig = False
                for spadeCard in kinds[2]:  # 找黑桃Q
                    if spadeCard.point == 12:
                        pos = spadeCard
                        hasPig = True
                        break
                if not hasPig:
                    del kinds[nowSuit]  # 如果没黑桃Q，在除了该花色以外的里面选最优
                    pos = self.choose_card(kinds, 0)
                if len(deck) == 13:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 找到的最优不能是黑桃Q或者红桃
                        pos = self.choose_card(kinds, 0)
            else:  # 有该花色的牌
                if len(deck) == 13:  # 第一轮出该花色最大的牌
                    pos = kinds[0][-1]
                else:  # 其他轮小心猪和红桃
                    hasScoreCard = False  # 看出的牌里是否有猪和红桃
                    for outCard in thisTurnOutCard:
                        card = outCard[1]
                        if (card.suit == 2 and card.point == 12) or (card.suit == 3):
                            hasScoreCard = True
                            break
                    if not hasScoreCard:  # 如果没有分
                        pos = kinds[nowSuit][-1]  # 出最大的，最大的是猪的话出黑桃里小一点的。
                        if pos.suit == 2 and pos.point == 12 and len(kinds[nowSuit]) >= 2:
                            pos = kinds[nowSuit][-2]  # （如果黑桃只有一张Q了，就只能出去了）
                    else:  # 如果出现了分
                        bigpos = []
                        smallpos = []
                        for card in kinds[nowSuit]:
                            if card.point > maxCard:
                                bigpos.append(card)
                            else:
                                smallpos.append(card)
                        if len(smallpos) != 0:  # 有小牌， 就出比当前最大的小一的牌
                            pos = smallpos[-1]
                        else:  # 没有小牌，就只能拿分了，用最大的牌来拿分，如果最大的牌是黑Q尽量避免黑Q，选用黑小，无黑小则只能用黑Q了
                            pos = bigpos[-1]
                            if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                                pos = bigpos[-2]
        if REPLAY == True:
            deck = [i for i in deck if i.suit != pos.suit]
            kinds = self.split_by_suit(deck)  # 按花色分成四类排序
            if len(thisTurnOutCard) == 0:  # 如果是第一个出牌的
                if len(deck) == 13:  # 因为是第一回合且第一个出牌，最小的肯定是梅花2
                    pos = deck[0]
                else:
                    if (outHeart == False) and (deck[0].suit != 3):  # 如果红桃还没出，且当前最小值不是红桃
                        del kinds[3]  # 不能出红桃类
                    if outQueen == False:
                        if (len(kinds[2]) == 0) or (kinds[2][-1].point >= 12):  # 没有黑桃或者黑桃最大值大于Q
                            pos = self.choose_card(kinds, 1)
                        else:  # 如果有小黑桃
                            pos = kinds[2][0]  # 出黑桃最小牌，拱猪
                    else:  # 如果黑桃Q已出
                        pos = self.choose_card(kinds, 1)

            elif len(thisTurnOutCard) < 3:  # 如果电脑不是最后一个出的

                maxCard = 0
                for outCard in thisTurnOutCard:  # 对于每个出牌
                    card = outCard[1]
                    if card.suit == nowSuit:  # 找到这一轮花色的最大值
                        if card.point > maxCard:
                            maxCard = card.point
                if len(kinds[nowSuit]) == 0:  # 如果没有该花色，优先黑桃Q
                    hasPig = False
                    for spadeCard in kinds[2]:  # 黑桃中每个牌
                        if spadeCard.point == 12:  # 如果有黑桃Q
                            pos = spadeCard  # 打黑Q
                            HasPig = True
                            break
                    if not hasPig:  # 如果没有黑Q
                        del kinds[nowSuit]  # 不出黑桃
                        pos = self.choose_card(kinds, 0)  # 在剩余的几个花色里选择最优的
                    if len(deck) == 13:  # 如果是第一次出牌
                        while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 如果是黑Q或红桃，一直再找最优
                            pos = self.choose_card(kinds, 0)  # flag是0，选最大值
                            # card = per.hand[pos]
                else:  # 如果有该花色
                    if len(deck) == 13:  # 如果是第一轮出牌
                        pos = kinds[0][-1]  # 第一轮出最大的牌，第一轮肯定是梅花，故suit0
                    else:
                        bigpos = []
                        smallpos = []
                        for card in kinds[nowSuit]:  # 分为比当前回合最大牌大和比它小的两摞
                            if card.point > maxCard:
                                bigpos.append(card)
                            else:
                                smallpos.append(card)
                        if len(smallpos) != 0:  # 如果有小的
                            pos = smallpos[-1]  # 就出小的里面最大的
                        else:
                            pos = bigpos[0]  # 大牌里面最小的
                            if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                                pos = kinds[nowSuit][1]  # 如果没有小的，如果大的里面最小的是黑桃Q且大的有两张牌以上，选择比最小的大一的

            elif len(thisTurnOutCard) == 3:  # 如果该玩家最后一个出牌

                maxCard = 0  # 该花色最大的牌
                for outCard in thisTurnOutCard:
                    card = outCard[1]  # 每个人出的牌
                    if card.suit == nowSuit:
                        if card.point > maxCard:
                            maxCard = card.point
                if len(kinds[nowSuit]) == 0:  # 无该花色的牌
                    hasPig = False
                    for spadeCard in kinds[2]:  # 找黑桃Q
                        if spadeCard.point == 12:
                            pos = spadeCard
                            hasPig = True
                            break
                    if not hasPig:
                        del kinds[nowSuit]  # 如果没黑桃Q，在除了该花色以外的里面选最优
                        pos = self.choose_card(kinds, 0)
                    if len(deck) == 13:  # 如果是第一次出牌
                        while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 找到的最优不能是黑桃Q或者红桃
                            pos = self.choose_card(kinds, 0)
                else:  # 有该花色的牌
                    if len(deck) == 13:  # 第一轮出该花色最大的牌
                        pos = kinds[0][-1]
                    else:  # 其他轮小心猪和红桃
                        hasScoreCard = False  # 看出的牌里是否有猪和红桃
                        for outCard in thisTurnOutCard:
                            card = outCard[1]
                            if (card.suit == 2 and card.point == 12) or (card.suit == 3):
                                hasScoreCard = True
                                break
                        if not hasScoreCard:  # 如果没有分
                            pos = kinds[nowSuit][-1]  # 出最大的，最大的是猪的话出黑桃里小一点的。
                            if pos.suit == 2 and pos.point == 12 and len(kinds[nowSuit]) >= 2:
                                pos = kinds[nowSuit][-2]  # （如果黑桃只有一张Q了，就只能出去了）
                        else:  # 如果出现了分
                            bigpos = []
                            smallpos = []
                            for card in kinds[nowSuit]:
                                if card.point > maxCard:
                                    bigpos.append(card)
                                else:
                                    smallpos.append(card)
                            if len(smallpos) != 0:  # 有小牌， 就出比当前最大的小一的牌
                                pos = smallpos[-1]
                            else:  # 没有小牌，就只能拿分了，用最大的牌来拿分，如果最大的牌是黑Q尽量避免黑Q，选用黑小，无黑小则只能用黑Q了
                                pos = bigpos[-1]
                                if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                                    pos = bigpos[-2]
        return pos

    def getScoreFromGame(self):
        '''
        从游戏状态中获得得分情况
        '''
        allTurnsCard = [] # 每个回合的出牌情况，总共三层，第一层为玩家i，出牌c，第二层为4个玩家，第三层为出了几个回合[[[1,Card(2,3)],[2,Card(3,3)],[],[]]]
        for i, j in enumerate(self.history_P0):
            tmp = []
            for k in range(4):
                now = self.history[(j + k) % 4]
                if len(now) > i:
                    tmp.append([(j + k) % 4, now[i]])
            allTurnsCard.append(tmp)

        score = {i: 0 for i in range(4)}
        for turn in allTurnsCard:
            maximum = 0
            turnSuit = turn[0][1].suit
            s = 0
            for c in turn:
                if c[1].suit == 3:
                    s += 1
                if c[1] == Card(12, 2):
                    s += 13
                if c[1].suit == turnSuit and c[1].point > maximum:
                    maximum = c[0]
            score[maximum] += s
        if 26 in score.values(): # 是否有人收全红
            for i,j in score.items():
                if j == 26:
                    score[i] = 0
                else:
                    score[i]=26
        return score

    def AutoPlay(self):
        '''
        玩牌函数，玩家0使用了MonteCarloPlay，其他玩家使用规则PlayCards
        返回四个玩家得分字典
        '''
        for turn_index in range(13):
            first_id = self.find_first()
            print(f'第{turn_index+1}回合___从玩家{first_id}开始' + '_' * 100)
            self.history_P0.append(first_id)
            for i in range(4):
                out_index = (first_id + i) % 4
                print('玩家', out_index)
                before_hand = self.players[out_index].hand
                now_p0 = [(p0 + 4 - out_index) % 4 for p0 in self.history_P0]
                # 此处history_P0需做转换，对于不同的玩家，每个玩家都认为自己是玩家0，玩家0,1,2,3只是相对的指出各个玩家的顺序
                
                if out_index == 0: # 使用MonteCarlo
                    out_card = MonteCarloPlay(self.players[out_index].hand, self.history[(out_index) % 4],
                                              self.history[(out_index + 1) % 4], self.history[(out_index + 2) % 4],
                                              self.history[(out_index + 3) % 4], now_p0)
                else: # 使用规则
                    out_card = self.PlayCards(self.players[out_index].hand, self.history[(out_index) % 4],
                                              self.history[(out_index + 1) % 4], self.history[(out_index + 2) % 4],
                                              self.history[(out_index + 3) % 4], now_p0)
                print('hand:', [card2chinese(i) for i in before_hand])
                print('out_card:', card2chinese(out_card))

                
                self.players[out_index].hand.remove(out_card)
                self.history[out_index].append(out_card)
                print('------------------------------------------')
        score = self.getScoreFromGame()
        for i, j in score.items():
            print(f'玩家{i}最终得分:{j}')
        return score

if __name__ == '__main__':
    scores = []
    '''
    进行n次游戏,统计得分情况
    '''
    NUM_GAME = 1
    for _ in range(NUM_GAME):
        game = Game()
        score = game.AutoPlay()
        scores.append(score)
        print(score)
