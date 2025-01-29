from __future__ import annotations
from typing import Tuple
import platform
import pygame
import math
import time

pygame.init()

if platform.system() == 'Windows':
    font = {
        10: pygame.font.SysFont('kaiti', 10),
        15: pygame.font.SysFont('kaiti', 15),
        20: pygame.font.SysFont('kaiti', 20),
        25: pygame.font.SysFont('kaiti', 25),
        30: pygame.font.SysFont('kaiti', 30),
        40: pygame.font.SysFont('kaiti', 40),
    }
else:
    font = {
        10: pygame.font.SysFont('kaittf', 10),
        15: pygame.font.SysFont('kaittf', 15),
        20: pygame.font.SysFont('kaittf', 20),
        25: pygame.font.SysFont('kaittf', 25),
        30: pygame.font.SysFont('kaittf', 30),
        40: pygame.font.SysFont('kaittf', 40),
    }
def show_text(screen: pygame.Surface, text = '', color = (0, 0, 0), pos = (0, 0), size = 20):
    screen.blit(font[size].render((text), True, color), pos)
def show_tip(screen: pygame.Surface, text = '', pos = (0, 0), size = 20, color = (255, 255, 255), bg_color = (88, 88, 88), alpha = 128):
    textsur = font[size].render((text), True, color)
    bgsur = pygame.Surface((textsur.get_width(), textsur.get_height()), pygame.SRCALPHA)
    bgsur.fill(bg_color)
    bgsur.set_alpha(alpha)
    bgsur.blit(textsur, (0, 0))
    screen.blit(bgsur, pos)
    return textsur.get_width(), textsur.get_height()

def load_actor(name):
    return pygame.image.load(f'./images/actor/{name}.png').convert_alpha()
def load_block(name, s):
    return pygame.transform.smoothscale(pygame.image.load(f'./images/{name}').convert_alpha(), (s, s))
def load_decorate(name):
    return pygame.image.load(f'./images/decorate/{name}.png').convert_alpha()
la, lb, ld = load_actor, load_block, load_decorate

def get_rotate_angle(x1, y1, x2, y2):
    return -math.degrees(math.atan2(y2 - y1, x2 - x1))

def get_distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def collision(x1, y1, w1, h1, x2, y2, w2, h2):
    l1, r1, t1, b1 = x1, x1 + w1, y1, y1 + h1
    l2, r2, t2, b2 = x2, x2 + w2, y2, y2 + h2
    return not (l1 < r1 < l2 < r2 or 
                l2 < r2 < l1 < r1 or 
                t1 < b1 < t2 < b2 or 
                t2 < b2 < t1 < b1)

def math_pos_to_pygame_pos(x, y, scw, sch):
    return scw + x, sch - y

def draw_progress(screen, value = 100, total = 100,
                  x = 0, y = 0, length = 100, width = 2,
                  color = (255, 0, 0), bgcolor = (0, 0, 0)):
    pygame.draw.line(screen, bgcolor, (x, y), (x + length, y), width)
    if length * value / total >= 1:      # 两个点就重合（距离>=1px）才会绘制
        pygame.draw.line(screen, color, (x, y), (x + length * value / total, y), width)

class Progress:
    def __init__(self, screen, value = 0, total = 1, x = 0, y = 0, length = 100, width = 2, color = (255, 0, 0), bgcolor = (0, 0, 0)):
        self.scr = screen
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.color = color
        self.bgcolor = bgcolor
        self.set(value, total)
    def set(self, value, total):
        self.value = value
        self.total = total
    def advance(self, n = 1):
        self.value = max(0, min(self.total, self.value + n))
    def clear(self):
        self.value = 0
    def show(self):
        draw_progress(self.scr, self.value, self.total, self.x, self.y, self.length, self.width, self.color, self.bgcolor)
    @property
    def is_full(self):
        return self.value >= self.total
    @property
    def is_empty(self):
        return self.value <= 0

class Record:
    def __init__(self):
        self.record_color = {
            '新手': (255, 255, 255),
            '入门': (208, 208, 208),
            '初级': (100, 100, 255),
            '中级': (100, 255, 100),
            '高级': (255, 100, 100),
            '特级': (200, 100, 255),
            '史诗': (100, 255, 200),
            '传说': (255, 255, 100),
        }
        self.record_dict = {
            '进击的镐子I': [0, '新手', '这下挖东西方便多了！'],
            '进击的镐子II': [0, '新手', '你看，越硬的镐子，挖起来越顺手！'],
            '进击的镐子III': [0, '入门', '叮！不愧是你！喜提铁镐一个！'],
            '进击的镐子IV': [0, '入门', '金镐不错，就是有点耗资。'],
            '进击的镐子V': [0, '入门', '是时候展示地表最强之镐了！'],
            '原始武装(锐剑I)': [0, '新手', '现在不用害怕怪物的攻击了，杀牛羊也会更加便捷！'],
            '坚如磐石(锐剑II)': [0, '新手', '你的装备更好了！不过，还有很多更高级的剑呢。'],
            '铁血战士(锐剑III)': [0, '入门', '现在，你不惧怕大多数敌人了。'],
            '黄金之刃(锐剑IV)': [0, '入门', '黄金的性价比不高，但它实在耀眼！'],
            '钻石耀剑(锐剑V)': [0, '入门', '哦，天哪！真是一把宝剑啊！'],
            '耐用的燃料': [0, '新手', '这团黑漆漆的东西是什么？'],
            '来硬的': [0, '新手', '通过煅烧获得一个铁锭'],
            '金！色！传！说！': [0, '新手', '通过煅烧获得一个金锭'],
            '钻！石！': [0, '入门', '终于挖到赚需了兄弟们，呃呃呃！'],
        }
        self.show_queue = []
        self.name = self.desc = ''
        self.color = (0, 0, 0)
        self.stop_time = 0
        self.rect = pygame.Rect(0, -80, 1000, 80)
    def record(self, name):
        if self.record_dict[name][0]:
            return
        self.record_dict[name][0] = 1
        self.show_queue.append((name, self.record_color[self.record_dict[name][1]], self.record_dict[name][2]))
    def show(self, screen):
        if self.name:
            if not self.stop_time:        # 下降
                self.rect.y += 1
                if self.rect.y >= 0:
                    self.stop_time = time.time()
            elif time.time() - self.stop_time > 3:        # 定格3秒后上升
                self.rect.y -= 1
                if self.rect.y <= -80:
                    self.name = ''
                    self.stop_time = 0
            pygame.draw.rect(screen, (88, 88, 88), self.rect, 0, 6)
            pygame.draw.rect(screen, self.color, self.rect, 3, 6)
            show_text(screen, self.name, self.color, (self.rect.x + 10, self.rect.y + 10), 40)
            show_text(screen, self.desc, (255, 255, 255), (self.rect.x + 10, self.rect.y + 50), 20)
        elif self.show_queue:
            self.name, self.color, self.desc = self.show_queue.pop(0)

class Label:
    def __init__(self, text = '', pos = (0, 0), size = 20, color = (255, 255, 255), bg_color = (88, 88, 88), alpha = 128):
        self.text = text
        self.pos = pos
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.alpha = alpha
    def show_on(self, surface: pygame.Surface):
        show_tip(surface, self.text, self.pos, self.size, self.color, self.bg_color, self.alpha)

class Button(Label):
    def __init__(self, text = '', pos = (0, 0), size = 20, color = (255, 255, 255), bg_color = (88, 88, 88), alpha = 128, border = 2, border_color = (0, 0, 0, 0)):
        super().__init__(text, pos, size, color, bg_color, alpha)
        self.border = self.real_border = border
        self.real_alpha = self.alpha
        self.border_color = border_color
        self.high = False
        self.w = self.h = 0
    def hightlight(self):
        self.real_border += 1
        self.real_alpha = min(self.alpha * 1.5, 255)
        self.high = True
    def unhightlight(self):
        self.real_border = self.border
        self.real_alpha = self.alpha
        self.high = False
    def show_on(self, surface: pygame.Surface):
        self.w, self.h = show_tip(surface, self.text, self.pos, self.size, self.color, self.bg_color, self.real_alpha)
        pygame.draw.rect(surface, self.border_color, (self.pos, (self.w, self.h)), self.real_border)

class Chatbox:
    def __init__(self, data: dict, conn: dict, images: dict, hides: list):
        self.data = data
        self.images = images
        self.image = None
        self.image_pos = (0, 0)
        self.conn = conn
        self.hides = hides
        self.hide = False
        self.index = ''
        self.current = []
        self.x = self.y = 0
        self.set_mode(0, 0, 1, 1)
        self.set_alpha(200)
    def next(self, value):
        self.index += value
        self.index = self.conn.get(self.index, self.index)
        self.image, self.image_pos = self.images.get(self.index, (self.image, self.image_pos))
        self.current = self.data[self.index]
        if self.index in self.hides:
            self.hide = True
    def set_mode(self, x, y, w, h):
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = pygame.Rect(0, 0, w, h)
        self.x, self.y = x, y
        self.set_alpha(200)
    def set_alpha(self, alpha):
        self.surface.set_alpha(alpha)
    def draw(self, screen: pygame.Surface):
        if self.hide:
            return
        self.surface.fill((255, 255, 255, 0))
        pygame.draw.rect(self.surface, (0, 0, 0), self.rect, 0, 10)
        pygame.draw.rect(self.surface, (255, 255, 255), self.rect, 5, 10)
        for each in self.current:
            each.show_on(self.surface)
        screen.blit(self.surface, (self.x, self.y))
        if self.image:
            screen.blit(self.image, self.image_pos)
    def update(self, event):
        if self.hide:
            return
        has_button = False
        for each in self.current:
            if type(each) == Button:
                has_button = True
                x, y = pygame.mouse.get_pos()
                x -= self.x
                y -= self.y
                if each.w and each.h and collision(*each.pos, each.w, each.h, x, y, 1, 1):
                    if not each.high:
                        each.hightlight()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.next(each.text)
                elif each.high:
                    each.unhightlight()
        if not has_button:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                self.next('>')


# record_dict = {
#     '挖掘！': [0,'新手','完成第一个方块的挖掘'],
#     '伐木工': [0,'新手','砍一下木头'],
#     '背包！': [0,'新手','按下[E]打开背包'],
#     '是时候开始工作了': [0,'新手','合成3*3木工作台'],
#     '进击的镐子I': [0,'入门','合成第一个木镐'],
#     '进击的镐子II': [0,'入门','合成第一个石镐'],
#     '进击的镐子III': [0,'初级','合成第一个铁镐'],
#     '进击的镐子IV': [0,'初级','合成第一个金镐'],
#     '进击的镐子V': [0,'中级','合成第一个钻石镐'],
#     '石器时代': [0,'入门','完成第一个石块的挖掘'],
#     '一起燃烧吧': [0,'入门','合成第一个熔炉，这玩意应该需要点燃料。'],
#     '铁器时代': [0,'入门','完成第一个铁矿的挖掘，铁是很重要的物质。'],
#     '燃料！': [0,'入门','完成第一个煤矿的挖掘，煤炭可以在熔炉中使用。（其实木头也可以当燃料）'],
#     '土产过多': [0,'入门','一个物品格子中放满了土方块'],
#     '砖家': [0,'初级','一个物品格子中放满了石块'],
#     '铁锭！': [0,'初级','熔炉煅烧出来的东西往往很有用，比如制作一些工具、防具、攻击器具等。'],
#     '铁饭碗': [0,'初级','在5*5铁工作台上工作'],
# }
















# 数据
dialog = {
    '0-0-0': ('author_i1','欢迎来到IDU沙盒'),
    '0-0-1': ('author_i1','我是作者。对话功能还在测试中'),
    '0-0-2': ('author_i1','↑↓←→移动，e背包，祝你玩得愉快！'),
    '0-0-3': '/finish_inside',
    '0-1-0': ('author_i1','内测中！'),
    # '0-1-0': '/finish_outside',
    # => '1-0-0': '...',
    # '0-1-0': '/finish_inside',
    # => '0-2-0': '...',
}
