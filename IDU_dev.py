print('IDU 更新\ndev 14 金矿、金锭、钻石矿\ndev 15 金镐、钻石镐')
import pygame
import random
import time
import sys
import platform

from basic import *
import sight

pygame.init()
pygame.key.stop_text_input()

# 定义常量(用户可以修改设置)
SC_WIDTH = 1000
SC_HEIGHT = 700
BLOCK_SIZE = 50
BOX_SIZE = 50
DROP_SIZE = 40
MP_BLW = 100
MP_BLH = 200
BURN_TIME = 5
BLOCK_DROP_DELTA = (BLOCK_SIZE - DROP_SIZE) / 2
BOX_CARD_DELTA = (BOX_SIZE - DROP_SIZE) / 2
BLOCK_SIZE_1in5 = BLOCK_SIZE // 5
BLOCK_SIZE_3in5 = BLOCK_SIZE - BLOCK_SIZE_1in5 * 2
MP_WIDTH = MP_BLW * BLOCK_SIZE
MP_HEIGHT = MP_BLH * BLOCK_SIZE
WIDTH = int(SC_WIDTH / BLOCK_SIZE)
HEIGHT = int(SC_HEIGHT / BLOCK_SIZE)

if platform.system() == 'Windows':
    font = {
        10: pygame.font.SysFont('kaiti', 10),
        20: pygame.font.SysFont('kaiti', 20),
        30: pygame.font.SysFont('kaiti', 30),
        40: pygame.font.SysFont('kaiti', 40),
    }
else:
    font = {
        10: pygame.font.SysFont('kaittf', 10),
        20: pygame.font.SysFont('kaittf', 20),
        30: pygame.font.SysFont('kaittf', 30),
        40: pygame.font.SysFont('kaittf', 40),
    }
def show_text(text,color=(0,0,0),pos=(0,0),size=20):
    screen.blit(font[size].render((text),True,color),pos)

screen = pygame.display.set_mode((SC_WIDTH,SC_HEIGHT))
pygame.display.set_caption('IDU Sandbox Driver (实变函数版)')


def loadblock(name,s):
    return pygame.transform.smoothscale(pygame.image.load(f'./images/{name}'),(s,s))
def loadactor(name):
    return pygame.image.load(f'./images/actor/{name}.png')
la, lb = loadactor, loadblock

binfo = {     # 原图片,作为掉落物的图片,掉落物的bid,硬度,占用容量
    0: [None,None,0,0,0],
    1001: [lb('草地.png',BLOCK_SIZE),lb('土.png',DROP_SIZE),1002,10,1],
    1002: [lb('土.png',BLOCK_SIZE),lb('土.png',DROP_SIZE),1002,20,1],
    1003: [lb('石块.png',BLOCK_SIZE),lb('石块.png',DROP_SIZE),1003,70,1],
    1004: [lb('树干.png',BLOCK_SIZE),lb('树干.png',DROP_SIZE),1004,40,1],
    1005: [lb('木板.png',BLOCK_SIZE),lb('木板.png',DROP_SIZE),1005,30,1],
    1006: [lb('工作台.png',BLOCK_SIZE),lb('工作台.png',DROP_SIZE),1006,60,1],
    1007: [lb('石工作台.png',BLOCK_SIZE),lb('石工作台.png',DROP_SIZE),1007,150,1],
    1008: [lb('铁矿.png',BLOCK_SIZE),lb('铁矿.png',DROP_SIZE),1008,300,1],
    1009: [lb('煤矿.png',BLOCK_SIZE),lb('煤炭.png',DROP_SIZE),2002,200,1],
    1010: [lb('熔炉.png',BLOCK_SIZE),lb('熔炉.png',DROP_SIZE),1010,220,1],
    1011: [lb('铁块.png',BLOCK_SIZE),lb('铁块.png',DROP_SIZE),1011,650,1],
    1012: [lb('铁工作台.png',BLOCK_SIZE),lb('铁工作台.png',DROP_SIZE),1012,850,1],
    1013: [lb('金矿.png',BLOCK_SIZE),lb('金矿.png',DROP_SIZE),1013,500,1],
    1014: [lb('钻石矿.png',BLOCK_SIZE),lb('钻石矿.png',DROP_SIZE),2005,1200,1],
    # 1015: [lb('金块.png',BLOCK_SIZE),lb('金块.png',DROP_SIZE),1015,1000,1],
    # 1016: [lb('钻石块.png',BLOCK_SIZE),lb('钻石块.png',DROP_SIZE),1016,3600,1],
    2001: [None,lb('木棍.png',DROP_SIZE),2001,0,1],
    2002: [None,lb('煤炭.png',DROP_SIZE),2002,0,1],
    2003: [None,lb('铁锭.png',DROP_SIZE),2003,0,1],
    2004: [None,lb('金锭.png',DROP_SIZE),2004,0,1],
    2005: [None,lb('钻石.png',DROP_SIZE),2005,0,1],
    # 后5项: 耐用度、挖掘加成、攻击加成、跳跃加成、范围加成
    3001: [None,lb('木镐.png',DROP_SIZE),3001,0,255,300,1,1,0,10],
    3002: [None,lb('石镐.png',DROP_SIZE),3002,0,255,1200,3,2,0,20],
    3003: [None,lb('铁镐.png',DROP_SIZE),3003,0,255,3500,8,3,0,35],
    3004: [None,lb('金镐.png',DROP_SIZE),3004,0,255,4000,10,2,0,60],
    3005: [None,lb('钻石镐.png',DROP_SIZE),3005,0,255,6600,20,5,0,90],
}
burns = {
    1008: 2003,
    1013: 2004,
}
fuels = {
    1004: 8,
    2002: 25,
}
data = [
    *([0 for i in range(100)] for line in range(10)),
    *([1001 for i in range(100)] for line in range(1)),
    *([1002 for i in range(100)] for line in range(10)),
    *([{1:1003,2:1003,3:1009,4:1009,5:1008,6:1008,7:1008,8:1009,9:1013,10:1014,}[random.randint(1,10)] for i in range(100)] for line in range(179)),
]

g = 0.15
boxclick = []
droplist = []

class Bar:
    def __init__(self,width,site,color,text='text'):
        self.width = width
        self.color = color
        self.text = text
        self.site = site
        self.textsite = (site[0] + 3, site[1])
        self.fullrect = pygame.Rect(self.site, (self.width, 25))
        self.realrect = pygame.Rect(self.site, (self.width, 25))
    def show(self,slider):
        self.realrect.width = self.width * slider.part
        pygame.draw.rect(screen,(128,128,128),self.fullrect,0)
        pygame.draw.rect(screen,self.color,self.realrect,0)
        pygame.draw.rect(screen,(0,0,0),self.fullrect,3)
        show_text(f'{self.text}: {slider.v}/{slider.f}',(0,0,0),self.textsite)

class Thing:
    def __init__(self):
        self.text = '事物基类（受重力都需要基于此）：玩家、掉落物、生物等。还未制作'

class Drop:
    def __init__(self,bid,pos):
        self.bid = bid
        self.pos = pos   # 绝对坐标
        self.speed = 0
        droplist.append(self)
    def drop(self,map):
        y = self.pos[1] + 40 - 1
        xl = self.pos[0]
        xr = xl + DROP_SIZE
        lx, ly = map.convert(1,xl,y)
        rx, ry = map.convert(1,xr,y)
        delta = 49
        # (*注 ly >= MP_BLH - 1) ly必定和ry相等，不用再判断ry.
        if ly >= MP_BLH - 1 or map.data[ly+1][lx] or map.data[ry+1][rx]:
            delta = 49 - y % 50
        self.pos[1] += min(self.speed, delta)
        if delta < 1:
            self.speed = 0
        else:
            self.speed = min(self.speed+g,30)
    def draw(self,mx,my):
        ax, ay = self.pos
        sx, sy = round(ax - mx), round(ay - my)
        if (-DROP_SIZE <= sx < SC_WIDTH) and (-DROP_SIZE <= sy < SC_HEIGHT):
            screen.blit(binfo[self.bid][1],(sx,sy))

class Card:
    def __init__(self,bid,value=1):
        self.bid = bid
        self.value = value
        self.capacity = binfo[bid][4]
        self.tp = 'normal'
        if 1000 <= bid <= 9999 and bid // 1000 == 3 and binfo[bid][5]:
            self.tp = 'resistant'
            self.resistant = Slider(binfo[bid][5],binfo[bid][5],0)
    def __iadd__(self,other):
        self.value += other.value
        return self
    def __isub__(self,other):
        self.value -= other.value
        return self
    def __add__(self,other):
        return self.value + other.value
    def __sub__(self,other):
        return self.value - other.value
    def full(self):
        return self.value * self.capacity >= 255
    def overflow(self):
        if self.value * self.capacity < 256:
            return 0
        over = self.value - 255 // self.capacity
        self.value = 255 // self.capacity
        return over
    def draw(self,pos):
        screen.blit(binfo[self.bid][1],pos)
        if 2 <= self.value < 10:
            show_text(str(self.value),(255,255,255),(pos[0]+DROP_SIZE-10,pos[1]+DROP_SIZE-20))
        elif 10 <= self.value < 100:
            show_text(str(self.value),(255,255,255),(pos[0]+DROP_SIZE-20,pos[1]+DROP_SIZE-20))
        elif 100 <= self.value < 256:
            show_text(str(self.value),(255,255,255),(pos[0]+DROP_SIZE-30,pos[1]+DROP_SIZE-20))
        if self.tp == 'resistant':
            if not self.resistant.isf:
                pygame.draw.line(screen, (0,0,0), pos,
                                 (pos[0]+DROP_SIZE, pos[1]), 2)
                pygame.draw.line(screen, (255,100,100), pos,
                                 (pos[0]+DROP_SIZE*self.resistant.part, pos[1]), 2)
    def tool_use(self):
        self.resistant -= 1
        return self.resistant.v

class Box:
    def __init__(self,x,y,tp='save'):
        self.x, self.y = x, y
        self.tp = tp
        self.rect = pygame.Rect(self.x, self.y, BOX_SIZE, BOX_SIZE)
        self.inside = None
        boxclick.append(self)
    def catch(self,card):
        self.inside = card
    def push(self):
        card = self.inside
        self.inside = None
        return card
    def draw(self,color=(88,88,88)):
        pygame.draw.rect(screen,(188,188,188),self.rect,0,5)
        pygame.draw.rect(screen,color,self.rect,3,5)
        if self.inside:
            self.inside.draw((self.rect.x+BOX_CARD_DELTA, self.rect.y+BOX_CARD_DELTA))

class Player:
    def __init__(self):
        self.hpBar = Bar(200,(10,10),(255,0,0),'HP')
        self.satietyBar = Bar(200,(10,40),(255,200,0),'ST')
        self.restart()
    def restart(self):
        # 位参
        self.x = SC_WIDTH / 2 - 20
        self.y = SC_HEIGHT / 2 - 60
        self.xspeed = 3   # 正方向向右
        self.yspeed = 0   # 正方向向下
        self.hitground = False
        self.rect = pygame.Rect(self.x,self.y,40,120)
        # 属性参
        self.jumpforce = 5
        self.digforce = 1
        self.attack = 1
        self.chooserange = 250
        self.hp = Slider(100,100)
        self.satiety = Slider(100,100)
    def bind(self,map_):
        self.map = map_
    
    def move(self):
        # 读取键盘移动意图
        xoffset = keystate[pygame.K_RIGHT] - keystate[pygame.K_LEFT]
        xoffset *= self.xspeed
        if xoffset:
            self.satiety -= 0.0003
        if self.hitground:
            if keystate[pygame.K_UP]:
                self.hitground = False
                self.yspeed = -self.jumpforce
                self.satiety -= 0.05
        else:
            self.yspeed = min(30, self.yspeed + g)
        yoffset = self.yspeed
        
        # 四种情况详细研究碰撞
        bleft, btop = self.map.convert(1,self.x,self.y)
        bright, bbottom = self.map.convert(1,self.x+self.rect.w-1,self.y+self.rect.h-1)
        if xoffset < 0:    # 左右碰到方块限制
            for row in range(btop,bbottom+1):
                if bleft <= 0 or self.map.data[row][bleft-1]:
                    delta = self.x - bleft * 50
                    xoffset = -min(-xoffset, delta)
                    break
        elif xoffset > 0:
            for row in range(btop,bbottom+1):
                if bright >= MP_BLW - 1 or self.map.data[row][bright+1]:
                    delta = bright * 50 + 50 - self.x - self.rect.w
                    xoffset = min(xoffset, delta)
                    break
        self.x += xoffset    # x移动（提前移动避免出现斜对角卡方块情况）
        self.x = min(max(self.x, 0), MP_WIDTH - 41)
        
        bleft, btop = self.map.convert(1,self.x,self.y)
        bright, bbottom = self.map.convert(1,self.x+self.rect.w-1,self.y+self.rect.h-1)
        self.hitground = False
        if yoffset < 0:    # 上下碰到方块限制
            for col in range(bleft,bright+1):
                if btop <= 0 or self.map.data[btop-1][col]:
                    delta = self.y - btop * 50
                    if -yoffset >= delta:
                        yoffset = -delta
                        self.yspeed = 0    # 撞墙弹力将速度抵消
                    break
        elif yoffset > 0:
            for col in range(bleft,bright+1):
                if bbottom >= MP_BLH - 1 or self.map.data[bbottom+1][col]:
                    delta = bbottom * 50 + 50 - self.y - self.rect.h
                    if yoffset >= delta:
                        yoffset = delta
                        self.hitground = True
                        if self.yspeed >= 8:
                            self.hp -= (self.yspeed - 8) * 5
                        self.yspeed = 0
                    break
        self.y += yoffset      # y移动
        self.y = min(max(self.y, 0), MP_HEIGHT - 121)
        
        # 在地图边缘自移动
        if self.x <= SC_WIDTH / 2 - 20:
            self.rect.x = int(self.x)
        elif self.x >= MP_WIDTH - SC_WIDTH / 2 - 20:
            self.rect.x = int(SC_WIDTH-MP_WIDTH+self.x+1)
        if self.y <= SC_HEIGHT / 2 - 60:
            self.rect.y = int(self.y)
        elif self.y >= MP_HEIGHT - SC_HEIGHT / 2 - 60:
            self.rect.y = int(SC_HEIGHT-MP_HEIGHT+self.y+1)
    
    def keep(self):
        if self.hp < 1:
            self.restart()
        if self.satiety <= 0:
            self.hp -= 0.03
        self.satiety -= 0.001
        self.hp += 0.001
    def hit_drop(self):
        dropindex = 0
        while dropindex < len(droplist):
            drop = droplist[dropindex]
            if hit_rect(self.x,self.y,
                        self.rect.w,self.rect.h,
                        drop.pos[0],drop.pos[1],
                        DROP_SIZE,DROP_SIZE):
                if receive_drop(drop.bid,inventory):
                    droplist.remove(drop)
                elif receive_drop(drop.bid,bag):
                    droplist.remove(drop)
            else:
                dropindex += 1
    
    def draw(self):
        pygame.draw.rect(screen,(255,0,0),self.rect,3)
    def draw_info(self):
        self.hpBar.show(self.hp)
        self.satietyBar.show(self.satiety)
    
    @property
    def position(self):
        return [self.x, self.y, self.rect.x, self.rect.y]
    @property
    def center(self):
        return self.rect.center

class GameMap:
    def __init__(self,data):
        self.data = data
        self.highlightrect = pygame.Rect(0,0,50,50)
        self.highbid = 0
        self.offsetx = self.offsety = 0
        self.dig_progress = Slider(0,0,0)
    
    def include(self,player):
        self.player = player
        pl_pos = self.player.position
        self.offsetx = pl_pos[0] - pl_pos[2]
        self.offsety = pl_pos[1] - pl_pos[3]
    def convert(self,tp,x,y,scx=None,scy=None):
        if tp == 1:     # 绝对坐标转绝对方块
            return [int(x // 50), int(y // 50)]
        if tp == 2:     # 绝对方块转绝对坐标
            return [x * 50, y * 50]
        if tp == 3:     # 绝对方块转相对坐标
            return [x * 50 - scx, y * 50 - scy]
    
    def draw_drops(self):
        for drop in droplist:
            drop.drop(self)
            drop.draw(self.offsetx, self.offsety)
    def draw(self):
        # 绘制
        px, py, psx, psy = self.player.position
        self.offsetx, self.offsety = px - psx, py - psy
        bleft, btop = self.convert(1, self.offsetx, self.offsety)
        bright, bbottom = bleft + WIDTH, btop + HEIGHT
        while btop <= bbottom:
            while bleft <= bright:
                image = binfo[self.data[btop][bleft]][0]
                if image:
                    screen.blit(image,self.convert(3, bleft, btop, self.offsetx, self.offsety))
                bleft += 1
            bleft = bleft - 1 - WIDTH
            btop += 1
        
        # 高亮
        if not (bag_open or furnace_open):
            ex, ey = mousestate['pos']
            px, py = self.player.center
            distance = get_distance(ex,ey,px,py)
            invent_c = inventory[invent_choose-1].inside
            idigforce, iattack, ijumpforce, ichooserange = binfo[invent_c.bid][6:10] \
                                                           if (invent_c and 1000 <= invent_c.bid <= 9999 and invent_c.bid // 1000 == 3) \
                                                           else [0, 0, 0, 0]       # 以3开头的物品判断属性附加
            if 0 <= ex < SC_WIDTH and 0 <= ey <= SC_HEIGHT and distance <= self.player.chooserange + ichooserange:
                highlight_col, highlight_row = self.convert(1, self.offsetx+ex, self.offsety+ey)
                highleft, hightop = self.convert(2, highlight_col, highlight_row)
                highbid = self.data[highlight_row][highlight_col]
                if highbid != self.highbid:
                    self.highbid = highbid
                    self.dig_progress.clear()
                    self.dig_progress.change_full(binfo[self.highbid][3])
                if self.highbid:
                    border = 3
                    x_ = highleft + BLOCK_SIZE_1in5 - self.offsetx
                    y_ = hightop + 5 - self.offsety
                    pygame.draw.line(screen, (0,0,0), (x_,y_),
                                     (x_ + BLOCK_SIZE_3in5, y_), 2)
                    pygame.draw.line(screen, (88,255,188), (x_,y_),
                                     (x_ + BLOCK_SIZE_3in5 * (1-self.dig_progress.part), y_), 2)
                    if mousestate[1]:
                        if invent_c and invent_c.tp == 'resistant' and (not invent_c.tool_use()):
                            inventory[invent_choose-1].catch(None)
                        self.dig_progress += self.player.digforce + idigforce
                        self.player.satiety -= 0.002
                        if self.dig_progress.isf:
                            self.player.satiety -= 0.02
                            self.data[highlight_row][highlight_col] = 0
                            Drop(binfo[self.highbid][2], [highleft+BLOCK_DROP_DELTA, hightop+BLOCK_DROP_DELTA])
                            record.new('挖掘！')
                            if highbid == 1003:
                                record.new('石器时代')
                            elif highbid == 1004:
                                record.new('伐木工')
                            elif highbid == 1008:
                                record.new('铁器时代')
                            elif highbid == 1009:
                                record.new('燃料！')
                else:
                    border = 1
                    if mousestate[3]:
                        self.player.satiety -= 0.005
                        invent = inventory[invent_choose-1].inside
                        if invent and binfo[invent.bid][0]:
                            self.data[highlight_row][highlight_col] = invent.bid
                            invent.value -= 1
                            if invent.value < 1:
                                inventory[invent_choose-1].push()
                self.highlightrect.topleft = self.convert(3, highlight_col, highlight_row, self.offsetx, self.offsety)
                pygame.draw.rect(screen,(0,0,0),self.highlightrect,border,3)
        
        # 绘制掉落物
        self.draw_drops()

class SunAct:
    def __init__(self,d,h,suntime):
        self.d = d
        self.h = h
        self.r = self.d / 2
        self.sunrise, self.sunset = suntime
        self.noon = (self.sunrise + self.sunset) / 2
        self.v = self.d / (self.sunset - self.sunrise)
        self.rect = pygame.Rect(0,0,100,100)
        self.sun_pos = False
    def get_sun_pos(self,t):
        '''
        x 与 time 的关系：
            x = (t - noon) / (sunset - sunrise) * d
        y 与 x 的关系：
            圆标准方程（不知道别的什么函数/方程能更好描述天体运动路径了）
        '''
        if t < self.sunrise or t > self.sunset:
            self.sun_pos = False
            return
        x = round((t - self.noon) * self.v)
        y = round((self.r ** 2 - x ** 2) ** 0.5)
        self.sun_pos = (x+self.r, self.h-y)      # 返回的坐标系是数学的，所以改变
    def day(self):
        if self.sun_pos:
            self.rect.center = self.sun_pos
            pygame.draw.rect(screen,(255,0,0),self.rect,0,25)
            pygame.draw.rect(screen,(255,195,111),self.rect,5,25)
    def night(self,t):
        if not self.sun_pos:
            if self.sunrise - 1 <= t <= self.sunrise:
                sightbg_alpha = (self.sunrise - t) * 255
            elif self.sunset <= t <= self.sunset + 1:
                sightbg_alpha = (t - self.sunset) * 255
            else:
                sightbg_alpha = 255
            sightbg.set_alpha(sightbg_alpha)
            screen.blit(sightbg,(0,0))
    def background(self,t):
        # 默认日出日落为6点和18点
        if 6.5 <= t < 16.5:
            color = (255,255,255)
        elif 4.5 <= t < 5:
            delta = t - 4.5
            color = (10+delta*90,10+delta*90,10+delta*300)
        elif 5 <= t < 5.5:
            delta = t - 5
            color = (55+delta*400,55+delta*200,160-delta*200)
        elif 5.5 <= t < 6.5:
            delta = t - 5.5
            color = (255,155+delta*100,60+delta*195)
        elif 16.5 <= t < 17.5:
            delta = t - 16.5
            color = (255,255-delta*100,255-delta*200)
        elif 17.5 <= t < 18:
            delta = t - 17.5
            color = (255-delta*400,155-delta*200,55+delta*300)
        elif 18 <= t < 18.5:
            delta = t - 18
            color = (55-delta*90,55-delta*90,205-delta*390)
        else:
            color = (10,10,10)
        screen.fill(color)

class Record:
    def __init__(self,all):
        self.all = all
        self.rect = pygame.Rect(0,-60,SC_WIDTH,60)
        self.show = None
        self.step = 0
        self.step2start = 0
        self.wait = []
    def new(self,name):
        self.wait.append(name)
    def push(self):
        if self.step == 0 and self.wait:
            name = self.wait.pop()
            if not self.all[name][0]:
                self.all[name][0] = 1
                self.show = [name] + self.all[name][1:]
                self.step = 1
                self.step2start = time.time()
    def keep(self):
        self.push()
        if self.step == 1:
            self.rect.y += 1
            if self.rect.y == 0:
                self.step = 2
        elif self.step == 2:
            if time.time() - self.step2start > 3:
                self.step = 3
                self.step2start = 0
        elif self.step == 3:
            self.rect.y -= 1
            if self.rect.y == -60:
                self.step = 0
                self.show = None
        if self.step:
            pygame.draw.rect(screen,(238,238,238),self.rect,0,5)
            pygame.draw.rect(screen,record_color[self.show[1]],self.rect,3,5)
            show_text(f'[{self.show[1]}]{self.show[0]}',record_color[self.show[1]],(self.rect.x+10,self.rect.y+5),30)
            show_text(self.show[2],(0,0,0),(self.rect.x+10,self.rect.y+35),20)

class Dialoger:
    def __init__(self):
        self.rect = pygame.Rect(0,SC_HEIGHT-220,SC_WIDTH,220)
        self.index = [0,0,-1]
        self.on = False
        self.nxt()
    def nxt(self):
        self.index[2] += 1
        string = dialog[f'{self.index[0]}-{self.index[1]}-{self.index[2]}']
        if type(string) == str:
            if string[0] == '/':
                command = string[1:]
                if command == 'finish_inside':
                    self.index[1] += 1
                    self.index[2] = -1
                elif command == 'finish_outside':
                    self.index = [self.index[0]+1,0,-1]
                else:
                    raise Exception(f'[IDU-Dialoger] unknown command "{string}".')
                self.nxt()
                self.on = False
                return
            else:
                raise Exception(f'[IDU-Dialoger] command "{string}" in {self.index} without "/".')
        self.image, self.text = string[0], string[1]
        self.image = eval(self.image)
    def skip(self):
        self.index[1] += 1
        self.index[2] = 0
        self.image, self.text = dialog[f'{self.index[0]}-{self.index[1]}-{self.index[2]}']
        self.image = eval(self.image)
        self.on = False
    def draw(self):
        pygame.draw.rect(screen,(88,88,88),self.rect,0,10)
        pygame.draw.rect(screen,(0,0,0),self.rect,5,10)
        screen.blit(self.image,(self.rect.x+10,self.rect.y-50))
        show_text(self.text,(255,255,255),(self.rect.x+100,self.rect.y+15))
        show_text('[X]继续  [Z]跳过',(255,255,255),(self.rect.right-175,self.rect.bottom-35))

def receive_drop(bid,boxes):
    search_index = None
    for boxindex in range(len(boxes)):
        box = boxes[boxindex]
        if box.inside and box.inside.bid == bid and (not box.inside.full()):
            boxes[boxindex].inside.value += 1
            return True
        if (not search_index) and (not box.inside):
            search_index = boxindex
    if search_index:
        boxes[search_index].catch(Card(bid,1))
        return True
    return False

def get_craft(craft):
    l = [[] for i in range(craftsize)]
    for row in range(craftsize):
        for col in range(craftsize):
            c = craft[row*craftsize+col].inside
            l[row].append(c.bid if c else 0)
    top = left = craftsize - 1
    right = bottom = 0
    for row in range(len(l)):
        for col in range(len(l[row])):
            if l[row][col]:
                top = min(top,row)
                bottom = max(bottom,row)
                left = min(left,col)
                right = max(right,col)
    clip = tuple(tuple(l[row][col] for col in range(left,right+1)) \
           for row in range(top,bottom+1)) \
           if (top <= bottom and left <= right) else ((0,),)
    return recipe.get(clip)
def clear_craft(craft):
    for box in craft:
        if box.inside:
            box.inside.value -= 1
            if not box.inside.value:
                box.catch(None)
def pushout_craft():
    for box in craft:
        c = box.push()
        if c:
            for i in range(c.value):
                Drop(c.bid,[player.x,player.y])
    to_craft.catch(None)
def create_craft(size):
    global craft, craftsize
    craftsize = size
    for c in craft:      # 回收资源。
        boxclick.remove(c)
    craft = [Box(bag_rect.x+100+col*50,bag_rect.y+100+BOX_SIZE*row,'craft') for row in range(size) for col in range(size)]



player = Player()
gamemap = GameMap(data)
player.bind(gamemap)
gamemap.include(player)
sun = SunAct(SC_WIDTH,SC_HEIGHT,(6,18))
sightbg = sight.generate_surface(SC_WIDTH,SC_HEIGHT,150,50)
sightbg.set_alpha(0)
record = Record(record_dict)

inventory = [Box((SC_WIDTH-9*BOX_SIZE)/2+BOX_SIZE*(i-1), SC_HEIGHT-BOX_SIZE-20) for i in range(1,10)]
invent_choose = 1
bag = [Box((SC_WIDTH-12*BOX_SIZE)/2+col*50,SC_HEIGHT-BOX_SIZE-100-BOX_SIZE*row) for row in range(3) for col in range(12)]
bag_open = False
bag_rect = pygame.Rect(SC_WIDTH/2-400,SC_HEIGHT/2-260,800,600)
craft = []
create_craft(2)
furnace_thing = Box(SC_WIDTH/2-300,SC_HEIGHT/2-210,'fthing')
furnace_fire = Box(SC_WIDTH/2-300,SC_HEIGHT/2-110,'ffire')
furnace_result = Box(SC_WIDTH/2-100,SC_HEIGHT/2-160,'fres')
furnace_open = False
furnace_is_burning = 0
single_burn_time = furnace_burn_time = 0
to_craft = Box(bag_rect.x+300,bag_rect.y+125,'to_craft')

keystate = {
    pygame.K_UP: 0,
    pygame.K_DOWN: 0,
    pygame.K_LEFT: 0,
    pygame.K_RIGHT: 0,
    pygame.K_w: 0,
    pygame.K_s: 0,
    pygame.K_a: 0,
    pygame.K_d: 0,
}
mousestate = {
    'pos': (-1,-1),
    1: 0,
    3: 0,
}

author_i1 = la('作者1')
author_i2 = la('作者2')
author_i3 = la('作者3')
author_i4 = la('作者4')
author_i5_1 = la('作者5-1')
author_i6 = la('作者6')
author_i7_1 = la('作者7-1')
author_i7_2 = la('作者7-2')
dialoger = Dialoger()
dialoger.on = True

clock = pygame.time.Clock()
gamestarttime = time.time()

# -------↑一般测试初始量↑------- #
# -------↓特殊测试初始量↓------- #
inventory[0].catch(Card(1002,16))
inventory[1].catch(Card(1003,16))
inventory[2].catch(Card(1005,32))
# inventory[3].catch(Card(3003,1))
# inventory[4].catch(Card(1012,64))
bag[0].catch(Card(1002,128))
bag[1].catch(Card(1003,128))
mousecard = None



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            mousestate['pos'] = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousestate[event.button] = 1
            if bag_open or furnace_open:
                for box in boxclick:
                    if box.rect.collidepoint(mousestate['pos']) and \
                       ((bag_open and box.tp in ['save','craft','to_craft']) or \
                        (furnace_open and box.tp in ['save','fthing','ffire','fres'])):
                        boxcard = box.push()
                        if event.button == 1:
                            if mousecard and boxcard and mousecard.bid == boxcard.bid and box.tp != 'to_craft':
                                box.catch(boxcard)
                                box.inside += mousecard
                                mousecard.value = box.inside.overflow()
                            else:
                                if box.tp == 'to_craft':
                                    if boxcard and (not mousecard):
                                        clear_craft(craft)
                                        if boxcard.bid == 1006:
                                            record.new('是时候开始工作了')
                                        elif boxcard.bid == 1010:
                                            record.new('一起燃烧吧')
                                        elif boxcard.bid == 3001:
                                            record.new('进击的镐子I')
                                        elif boxcard.bid == 3002:
                                            record.new('进击的镐子II')
                                        elif boxcard.bid == 3003:
                                            record.new('进击的镐子III')
                                        elif boxcard.bid == 3004:
                                            record.new('进击的镐子IV')
                                        elif boxcard.bid == 3005:
                                            record.new('进击的镐子V')
                                    else:
                                        box.catch(boxcard)
                                        break
                                elif box.tp == 'fres':
                                    if boxcard and (not mousecard):
                                        if boxcard.bid == 2003:
                                            record.new('铁锭！')
                                    else:
                                        box.catch(boxcard)
                                        break
                                box.catch(mousecard)
                                mousecard = boxcard
                            if mousecard and mousecard.value < 1: mousecard = None
                        elif event.button == 3:
                            if box.tp in ['to_craft','fres']:
                                box.catch(boxcard)
                                break
                            if mousecard and boxcard and mousecard.bid == boxcard.bid:
                                box.catch(boxcard)
                                if not box.inside.full():
                                    box.inside.value += 1
                                    mousecard.value -= 1
                            elif mousecard and (not boxcard):
                                box.catch(Card(mousecard.bid,1))
                                mousecard.value -= 1
                            elif (not mousecard) and boxcard:
                                mousecard = Card(boxcard.bid,boxcard.value // 2)
                                box.catch(boxcard)
                                box.inside -= mousecard
                            else:
                                box.catch(boxcard)
                            if mousecard and mousecard.value < 1: mousecard = None
                        if box.inside and box.inside.full():
                            if box.inside.bid == 1002:
                                record.new('土产过多')
                            elif box.inside.bid == 1003:
                                record.new('砖家')
                        break
                if bag_open:
                    gc = get_craft(craft)
                    if gc:
                        to_craft.catch(Card(*gc))
                    else:
                        to_craft.catch(None)
                elif furnace_open:
                    if (not furnace_is_burning) and (furnace_thing.inside and furnace_thing.inside.bid in burns) \
                       and (furnace_fire.inside and furnace_fire.inside.bid in fuels) \
                       and ((not furnace_result.inside) or (furnace_result.inside and \
                            furnace_result.inside.bid == burns[furnace_thing.inside.bid])):
                        furnace_is_burning = fuels[furnace_fire.inside.bid]
                        furnace_fire.inside.value -= 1
                        if furnace_fire.inside.value < 1: furnace_fire.catch(None)
                        furnace_burn_time = single_burn_time = time.time()
            else:
                if event.button == 3:
                    if gamemap.highbid == 1006:
                        bag_open = True
                        create_craft(3)
                    elif gamemap.highbid == 1007:
                        bag_open = True
                        create_craft(4)
                    elif gamemap.highbid == 1012:
                        bag_open = True
                        create_craft(5)
                        record.new('铁饭碗')
                    elif gamemap.highbid == 1010:
                        furnace_open = True
        if event.type == pygame.MOUSEBUTTONUP:
            mousestate[event.button] = 0
        if event.type == pygame.KEYDOWN:
            ek = event.key
            keystate[ek] = 1
            if 49 <= ek <= 57:
                invent_choose = int(chr(ek))
            if ek == ord('e'):
                record.new('背包！')
                if bag_open:
                    bag_open = False
                    pushout_craft()
                elif not furnace_open:
                    bag_open = True
                    create_craft(2)
                if furnace_open:
                    furnace_open = False
            elif dialoger.on and ek == ord('x'):
                dialoger.nxt()
            elif dialoger.on and ek == ord('z'):
                dialoger.skip()
        if event.type == pygame.KEYUP:
            keystate[event.key] = 0
    
    if furnace_is_burning:
        if time.time() - furnace_burn_time > furnace_is_burning:
            furnace_is_burning = 0
            single_burn_time = furnace_burn_time = 0
        if furnace_thing.inside and time.time() - single_burn_time > BURN_TIME:
            furnace_thing.inside.value -= 1
            if furnace_result.inside:
                furnace_result.inside.value += 1
            else:
                furnace_result.catch(Card(burns[furnace_thing.inside.bid],1))
            single_burn_time = time.time()
            if furnace_thing.inside.value < 1:
                furnace_thing.catch(None)
                furnace_is_burning = 0
                single_burn_time = furnace_burn_time = 0
    
    gametime = (time.time() - gamestarttime) * 1000 / 3600 + 6
    gamedaytime = gametime % 24
    sun.background(gamedaytime)
    
    # 白天（太阳图层在最底下）
    sun.get_sun_pos(gamedaytime)
    sun.day()
    
    gamemap.draw()
    player.keep()
    player.move()
    player.hit_drop()
    player.draw()
    
    # 黑夜（视野图层在最顶上）
    sun.night(gamedaytime)
    
    if bag_open:
        pygame.draw.rect(screen,(128,128,128),bag_rect,0,15)
        pygame.draw.rect(screen,(0,0,0),bag_rect,3,15)
        for box in bag:
            box.draw()
        for box in craft:
            box.draw()
        to_craft.draw()
    elif furnace_open:
        pygame.draw.rect(screen,(128,128,128),bag_rect,0,15)
        pygame.draw.rect(screen,(0,0,0),bag_rect,3,15)
        for box in bag:
            box.draw()
        furnace_thing.draw()
        furnace_fire.draw()
        furnace_result.draw()
        if furnace_is_burning and furnace_thing.inside:
            pygame.draw.line(screen,(255,255,255),(SC_WIDTH/2-240,SC_HEIGHT/2-140),(SC_WIDTH/2-140,SC_HEIGHT/2-140),10)
            pygame.draw.line(screen,(255,208,111),(SC_WIDTH/2-240,SC_HEIGHT/2-140),(SC_WIDTH/2-240+round(100*(time.time()-single_burn_time)/BURN_TIME),SC_HEIGHT/2-140),10)
    for box in inventory:
        box.draw()
    inventory[invent_choose-1].draw((255,0,0))
    player.draw_info()
    
    record.keep()
    
    if dialoger.on:
        dialoger.draw()
    
    if mousecard:
        mousecard.draw(mousestate['pos'])
    
    pygame.display.update()
    clock.tick(100)