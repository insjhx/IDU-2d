import pygame
import random
import time
import sys
import platform

from basic import *
import sight
import save

# Const
SC_WIDTH = 1000
SC_HEIGHT = 700
BLOCK_SIZE = 50
BOX_SIZE = 50
DROP_SIZE = 40
WIDTH = SC_WIDTH // BLOCK_SIZE
HEIGHT = SC_HEIGHT // BLOCK_SIZE
MPW = len(save.data[0])
MPH = len(save.data)
g = 0.15

# 基础Init
pygame.init()
pygame.key.stop_text_input()

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
def loadactor(name):
    return pygame.image.load(f'./images/actor/{name}.png')
def loadblock(name,s):
    return pygame.transform.smoothscale(pygame.image.load(f'./images/{name}'),(s,s))
la, lb = loadactor, loadblock

# +---------------------------------+
# |            方块信息             |
# | 0    空气                       |
# | 1XXX 普通方块                   |
# |      [0]图片                    |
# |      [1]掉落物id                |
# |      [2]硬度                    |
# |      [3]碰撞箱削弱              |
# | 2XXX 物品（非工具）             |
# |      [0]图片                    |
# |      [1]原方块id                |
# |      [2]占用容量                |
# | 3XXX 物品（工具）               |
# |      [0]图片                    |
# |      [1]耐久                    |
# |      [2]加成                    |
# |      [*]占用容量都为256         |
# | 4XXX 其他/特殊                  |
# | 5位数: 代表多格方块             |
# +---------------------------------+
# *加成 = [范围, 挖掘, 铲土, 攻击, 跳跃, 防护]
# *碰撞箱削弱 = [上px, 下px, 左px, 右px]
binfo = {
    0: [],
    1001: [lb('草地.png',BLOCK_SIZE), 2001, 10, [0, 0, 0, 0]],
    2001: [lb('土.png',DROP_SIZE), 1001, 1],
    3001: [lb('木镐.png',DROP_SIZE), 100, [0, 1, 0, 1, 0, 0]],
}



# 事物Init
# screen = pygame.display.set_mode((SC_WIDTH,SC_HEIGHT))
# pygame.display.set_caption('IDU Sandbox Driver')

class Command:
    def __init__(self):
        self.text = '<cmd>'
        self.cmd = {
            'p': self.c_p,
        }
    def execute(self, text, permission=1):
        t = text.split()
        if t[0][0] != '/':
            return (False, '[/] 命令前缺少匹配符</>')
        self.cmd[t[0][1:]](t[1:])
    def c_p(self, args):
        thing = eval(args[0])
        if get_class_text(thing)[0] != 'thing':
            return (False, '[/p] 传输的事物的基类必须是<thing>')
        thing.p(int(args[1]), int(args[2]))
        return True

class Map:
    def __init__(self):
        self.text = '<map>'
        self.data = [[]]
    def read(self):
        return self.data
    def write(self, d):
        self.data = d

class Thing:
    def __init__(self, w=1, h=1):
        self.text = '<thing>'
        self.x = 0.0
        self.y = 0.0
        self.xspeed = 0.0
        self.yspeed = 0.0
        self.w = w
        self.h = h
    def __str__(self):
        return f'<{self.text[1:-1]} | x: {round(self.x,1)}, y: {round(self.y,1)}, sx: {round(self.xspeed,1)}, sy: {round(self.yspeed,1)}, >'
    def p(self, x=None, y=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
    def v(self, x=None, y=None):
        if x is not None:
            self.xspeed = x
        if y is not None:
            self.yspeed = y
    def movep(self, addx=0.0, addy=0.0):
        self.x += addx
        self.y += addy
    def speedup(self, addsx=0.0, addsy=0.0):
        self.xspeed += addsx
        self.yspeed += addsy
    def move(self, data):
        vx, vy = self.xspeed, self.yspeed
        
        # l & r
        top = int(self.top / 50)
        bottom = int(self.bottom / 50)
        left = int(self.left / 50)
        right = int(self.right / 50)
        if vx < 0:
            for row in range(top, bottom + 1):
                if left <= 0 or data[row][left-1]:
                    vx = -min(vx, -self.space_left)
                    break
        elif vx > 0:
            for row in range(top, bottom + 1):
                if right >= MPW - 1 or data[row][right+1]:
                    vx = min(vx, self.space_right)
                    break
        
        # t & b
        top = int(self.top / 50)
        bottom = int(self.bottom / 50)
        left = int(self.left / 50)
        right = int(self.right / 50)
        if vy < 0:
            for col in range(left, right + 1):
                if top <= 0 or data[top-1][col]:
                    vy = -min(vy, -self.space_top)
                    break
        elif vy > 0:
            for col in range(left, right + 1):
                if bottom >= MPH - 1 or data[bottom+1][col]:
                    vy = min(vy, self.space_bottom)
                    break
        
        self.v(vx, vy)
        self.movep(self.xspeed, self.yspeed)
    def next(self, data):
        self.speedup(addsy=g)
        self.move(data)
    @property
    def left(self):
        return self.x
    @property
    def right(self):
        return self.x + self.w - 1
    @property
    def top(self):
        return self.y
    @property
    def bottom(self):
        return self.y + self.h - 1
    @property
    def cx(self):
        return self.x + self.w / 2
    @property
    def cy(self):
        return self.y + self.h / 2
    @property
    def space_left(self):
        return self.left % 50
    @property
    def space_right(self):
        return 49 - self.right % 50
    @property
    def space_top(self):
        return self.top % 50
    @property
    def space_bottom(self):
        return 49 - self.bottom % 50

class Living(Thing):
    def __init__(self, hp):
        super().__init__()
        self.text = '<thing-living>'
        self.hp = hp

class Player(Living):
    def __init__(self):
        super().__init__(100)

def get_class_text(obj):
    t = obj.text
    if (t[0] != '<') or (t[-1] != '>'):
        raise Exception('不匹配的class_text')
    return t[1:-1].split('-')





# 准备对象
cmd = Command()
gamemap = Map()
gamemap.write(save.data)
player = Player()

# 主程序
while True:
    text = input('>>')
    if text:
        cmd.execute(text)
    player.next(save.data)
    print(player)

pygame.quit()