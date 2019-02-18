'''
MonteCarlo模拟需要模拟个各玩家每个回合的出牌，因此使用本文件把所有模拟的过程封装了起来只留出了接口MonteCarloPlay
模拟的时候使用Heart为游戏类，模拟的时候MonteCarlo玩家的牌已知，其他三玩家牌未知

@author: pipixiu
@time: 2018.9.30
@city: Nanjing
'''

from Card import Suit,Rank
from Hearts import Hearts
from Deck import Deck
from Card import Card
from Player import Player
from PlayerTypes import PlayerTypes
from Trick import Trick # 回合类
import collections

Card_C = collections.namedtuple('Card', ['point', 'suit']) # 接口使用的牌类型

def Card_C2Card(card_c):
    # 为了接口类型保持一致，将模拟的时候用牌类做了一次转换
    return Card(card_c.point,card_c.suit)

def getScoreFromAllcards(all_cards):
    '''
    从MonteCarloPlay的输入参数中确定当前的得分情况，初始化给Heart
    '''
    score_dict = {0:0,1:0,2:0,3:0}
    for i in all_cards:
        if len(i)== 4:
            score = 0
            max_card,max_index = i[0][1],[0][0]
            for j in i:
                if j[1].suit== 3:
                    score+=1
                elif j[1] == Card_C(point=12,suit=2):
                    score += 12
                if j[1].suit== max_card.suit and j[1].point>max_card.point:
                    max_card = j[1]
                    max_index = j[0]
            score_dict[max_index]+=score
    return score_dict

def MonteCarloPlay(deck, history_self,history_A,history_B,history_C,history_P0,REPLAY=False):
    '''
    输入一摞牌，选出最应该出的牌

    规则打牌的判断机制，对于自己第几个出，自己出牌前已经打出的牌，红桃牌，黑桃Q的打出情况，
    以及应该打出大小点等各类情况都进行判断，从而选出应当打出的最适合的牌。
    input:
    deck:           列表，当前玩家手中的牌，如：
                    deck = [Card_C(point=7, suit=0),Card_C(point=10, suit=3),Card_C(point=11, suit=3)]
    history_self:   同deck列表，当前玩家已出的牌
    history_A:      同deck列表，玩家A已出的牌
    history_B:      同deck列表，玩家B已出的牌
    history_C:      同deck列表，玩家C已出的牌
    history_P0:     列表，每个回合第一个发牌的人的index。当前玩家:0, A:1, B:2, C:3
                    如：history_P0 = [0,1,1]表示第一回合是当前玩家先出的牌，第二回合玩家1先出的牌，第三回合还是玩家1先出的牌
    output:
    pos: Card_C类型，选出的最优的牌
    '''
    # -------------------------初始化MentorCarol类----------------------------------
    # 计算历史牌
    deck = sorted(deck,key=lambda x:x.suit*10+x.point)
    history = [history_self,history_A,history_B,history_C]    

    #从输入参数中计算每轮出的牌   
    allTurnsCard = []
    # 每个回合的出牌情况，总共三层，第一层为玩家i，出牌c，第二层为4个玩家，第三层为出了几个回合[[[1,Card(2,3)],[2,Card(3,3)],[],[]]]
    for i,j in enumerate(history_P0):    
        tmp = []
        for k in range(4):        
            now = history[(j+k)%4] 
            if len(now) > i:
                tmp.append([(j+k)%4,now[i]])
        allTurnsCard.append(tmp)
    score_dict = getScoreFromAllcards(allTurnsCard) # 每个玩家的得分dict
    thisTurnOutCard = allTurnsCard[-1] if allTurnsCard and len(allTurnsCard[-1])!=4 else [] # 当前回合玩家出牌情况，按照出牌顺序排列
    #outQueen = True if [outCard for turn in allTurnsCard for outCard in turn if outCard[1] == Card_C(12,2)] else False
    outHeart = True if [j for i in allTurnsCard for j in i if j[1].suit == 3] else False # 红桃是否已出


    h = Hearts()
    # h是MonteCarlo使用的游戏类，在该类中，四个玩家轮流出牌并计算得分，计出MonteCarlo玩家出什么牌时得到最优的概率并选择出该牌
    oneMonte_threeNaive_anon = [Player("AI 1  ", PlayerTypes.MonteCarloAI, h), Player("AI 2 ", PlayerTypes.NaiveMinAI, h),Player("AI 3  ", PlayerTypes.NaiveMinAI, h), Player("AI 4  ", PlayerTypes.NaiveMaxAI, h)]
    # 在模拟策略中使用一个MonteCarlo方法，其余三个使用Naive方法，此处可以设计不同的玩家规则来提高MonteCarlo模拟的表现
    h.players = oneMonte_threeNaive_anon    
    h.heartsBroken = outHeart 
    h.losingPlayer = None
    h.allTricks = []
    h.currentTrick = Trick()
    for j,i in enumerate(h.players): # 更新四个玩家的得分
        i.score = score_dict[j]
    for i in thisTurnOutCard: # 更新当前回合出的牌
        h.currentTrick.addCard(Card_C2Card(i[1]),i[0])
    h.trickWinner = thisTurnOutCard[0][0] if thisTurnOutCard else 0

    h.cardsPlayed = tuple(Card_C2Card(i[1]) for i in sum(allTurnsCard,[])) # keep track of state in a tuple
    h.cardsPlayedbyPlayer = {h.players[j]:[Card_C2Card(k) for k in i] for j,i in enumerate(history)} # 每个玩家已出牌字典

    h.shift = len(thisTurnOutCard) # 出牌次序
    h.winningPlayer = None
    h.winningPlayers = None # list
    h.trickNum = len(history_P0)-1 # 当前是第一轮出牌
    #h.dealer = 0 # so that first dealer is 0    
    
    #更新模拟的Monto玩家的牌
    MontoPlayer = h.players[0]
    for j in deck:
        MontoPlayer.hand.addCard(Card(j.point,j.suit))
        MontoPlayer.hand.updateHand() # 更新状态信息

    
    
    #--------------------------------------开始玩游戏----------------------------------------

    if MontoPlayer.hand.contains2ofclubs: # 如果有梅花2，则调用play函数直接出2c
        addCard = MontoPlayer.play(option="play", c='2c')
    else:
        addCard = None
        while addCard is None: # wait until a valid card is passed            
            addCard = MontoPlayer.play(auto=True) 
            if addCard is not None:
                if h.isValidCard(addCard, MontoPlayer) == False:
                    addCard = None                
    out_card = Card_C(point=addCard.rank.rank, suit=addCard.suit.iden) # 输出牌转换为接口的nametuple类型
    return out_card