from __future__ import annotations
from typing import Tuple, List, Dict, Any

import platform
import pygame
import random
import time
import math
import sys

from basic import *
from recipe import *
import sight
import save

''' 游戏编写设定
量词使用:
  sc: screen量词 (相对于screen而言)
  mp: map量词 (相对于map而言)
  px: pixel量词 (像素单位)
  bl: block量词 (方块单位)
  * example: mp_bl意思是相对map的以block为单位的量词
'''

# 常量和定义
if '基本构造设定':
    BLOCK_SIZE = 50                                       # (px)
    SLOT_SIZE = 50                                        # (px)
    DROP_SIZE = 40                                        # (px)
    DROP_SIZE_HALF = DROP_SIZE // 2                       # (px)
    BLOCK_SIZE_1in5 = BLOCK_SIZE // 5                     # (px)
    BLOCK_DROP_DELTA = BLOCK_SIZE - DROP_SIZE             # (px)
    SLOT_DROP_DELTA = SLOT_SIZE - DROP_SIZE               # (px)
    BLOCK_DROP_SPACE = BLOCK_DROP_DELTA // 2              # (px)
    SLOT_DROP_SPACE = SLOT_DROP_DELTA // 2                # (px)

if '屏幕大小':
    SCW_px = 1000                                  # (px)
    SCH_px = 700                                   # (px)
    SCW_bl = SCW_px // BLOCK_SIZE                  # (bl)
    SCH_bl = SCH_px // BLOCK_SIZE                  # (bl)
    SCW_px_half = SCW_px // 2                      # (px)
    SCH_px_half = SCH_px // 2                      # (px)

if '地图大小':
    MPW_bl = len(save.data[0])                     # (bl)
    MPH_bl = len(save.data)                        # (bl)
    MPW_px = MPW_bl * BLOCK_SIZE                   # (px)
    MPH_px = MPH_bl * BLOCK_SIZE                   # (px)
    MPR_px = MPW_px - SCW_px - 1                   # (px)
    MPB_px = MPH_px - SCH_px - 1                   # (px)

if '自然条件':
    GRAVITY = 15
    GROUND_FRICTION = 0.9
g = GRAVITY / 100

pygame.init()
pygame.key.stop_text_input()

screen = pygame.display.set_mode((SCW_px, SCH_px))
pygame.display.set_caption('IDU 24H3 Sandbox Driver')

def load_actor(name):
    return pygame.image.load(f'./images/actor/{name}.png').convert_alpha()
def load_block(name, s):
    return pygame.transform.smoothscale(pygame.image.load(f'./images/{name}').convert_alpha(), (s, s))
def load_decorate(name):
    return pygame.image.load(f'./images/decorate/{name}.png').convert_alpha()
la, lb, ld = load_actor, load_block, load_decorate

binfo = {
    0: [],
    100101: [lb('土.png', BLOCK_SIZE), 200101, 15, 0, 0, [0, 0, 0, 0]],
    100102: [lb('草地.png', BLOCK_SIZE), 200101, 10, 0, 0, [0, 0, 0, 0]],
    100201: [lb('石块.png', BLOCK_SIZE), 200201, 80, 1, 0, [0, 0, 0, 0]],
    100301: [lb('树干.png', BLOCK_SIZE), 200301, 60, 0, 1, [0, 0, 0, 0]],
    100401: [lb('木板.png', BLOCK_SIZE), 200401, 15, 0, 1, [0, 0, 0, 0]],
    100601: [lb('工作台.png', BLOCK_SIZE), 200601, 50, 0, 1, [0, 0, 0, 0]],
    100701: [lb('熔炉.png', BLOCK_SIZE), 200701, 180, 0, 1, [0, 0, 0, 0]],
    100801: [lb('石工作台.png', BLOCK_SIZE), 200801, 200, 0, 1, [0, 0, 0, 0]],
    100901: [lb('煤矿.png', BLOCK_SIZE), 200901, 135, 1, 0, [0, 0, 0, 0]],
    101001: [lb('铁矿.png', BLOCK_SIZE), 201001, 320, 2, 0, [0, 0, 0, 0]],
    101101: [lb('金矿.png', BLOCK_SIZE), 201101, 480, 3, 0, [0, 0, 0, 0]],
    101201: [lb('钻石矿.png', BLOCK_SIZE), 201201, 1660, 3, 0, [0, 0, 0, 0]],
    101501: [lb('箱子.png', BLOCK_SIZE), 201501, 85, 0, 1, [0, 0, 0, 0]],
    101601: [lb('铁块.png', BLOCK_SIZE), 201601, 860, 2, 0, [0, 0, 0, 0]],
    # 101701: [lb('金块.png', BLOCK_SIZE), 201701, 1250, 3, 0, [0, 0, 0, 0]],
    # 101801: [lb('钻石块.png', BLOCK_SIZE), 201801, 4750, 3, 0, [0, 0, 0, 0]],

    200101: [lb('土.png', DROP_SIZE), 100101, 64],
    200201: [lb('石块.png', DROP_SIZE), 100201, 64],
    200301: [lb('树干.png', DROP_SIZE), 100301, 64],
    200401: [lb('木板.png', DROP_SIZE), 100401, 64],
    200501: [lb('木棍.png', DROP_SIZE), 0, 64],
    200601: [lb('工作台.png', DROP_SIZE), 100601, 64],
    200701: [lb('熔炉.png', DROP_SIZE), 100701, 64],
    200801: [lb('石工作台.png', DROP_SIZE), 100801, 64],
    200901: [lb('煤炭.png', DROP_SIZE), 0, 64],
    201001: [lb('铁矿.png', DROP_SIZE), 101001, 64],
    201101: [lb('金矿.png', DROP_SIZE), 101101, 64],
    201201: [lb('钻石.png', DROP_SIZE), 0, 64],
    201301: [lb('铁锭.png', DROP_SIZE), 0, 64],
    201401: [lb('金锭.png', DROP_SIZE), 0, 64],
    201501: [lb('箱子.png', DROP_SIZE), 101501, 64],
    201601: [lb('铁块.png', DROP_SIZE), 101601, 64],
    # 201701: [lb('金块.png', DROP_SIZE), 101701, 64],
    # 201801: [lb('钻石块.png', DROP_SIZE), 101801, 64],

    300101: [lb('木镐.png', DROP_SIZE), 20, [10, 1, 0, 1, 0, 0, 0, 1]],
    300201: [lb('石镐.png', DROP_SIZE), 60, [10, 2, 0, 2, 0, 0, 0, 2]],
    300301: [lb('铁镐.png', DROP_SIZE), 350, [20, 4, 0, 3, 0, 0, 0, 3]],
    300401: [lb('金镐.png', DROP_SIZE), 180, [30, 5, 0, 3, 0, 0, 0, 2]],
    300501: [lb('钻石镐.png', DROP_SIZE), 1000, [50, 8, 0, 4, 0, 0, 0, 4]],
}
burnables = {                        # 被煅烧物id: 结果id
    201001: 201301,
    201101: 201401,
}
fuels = {                            # 燃料id: 燃烧持久(帧)
    200301: 1000,
    200401: 250,
    200501: 100,
    200601: 600,
    200901: 2500,
}



class Map:
    def __init__(self):
        self.x = 0.0                  # 地图左上角x坐标(px)
        self.y = 0.0                  # 地图左上角y坐标(px)
        self.data = [[]]
        self.function_blocks: Dict[Tuple[int, int], Page] = {}
        self.drop_list: List[Drop] = []
        self.dig_pos = None
        self.dig_progress = 0
        self.hightlight_rect = pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
    def load(self, data: list):
        self.data = data
    def save(self) -> list:
        return self.data
    
    def cannot_cross_block(self, row: int, col: int) -> bool:    # 判断方块是否不能被穿过
        return self.data[row][col] and binfo[self.data[row][col]][4] == 0
    
    def recv(self, event: dict, player: Player):        # 接收游戏事件
        col, row = px_to_bl(sc_to_mp(self, event['mpos']))
        mx, my = bl_to_px((col, row))
        x, y = mp_to_sc(self, (mx, my))
        bid = self.data[row][col]
        chosen_slot = player.bag.items[inventory_chosen_index]
        dig_speed_addition = dig_level_addition = 0
        if chosen_slot.bid // 100000 == 3:
            dig_speed_addition = binfo[chosen_slot.bid][2][1]
            dig_level_addition = binfo[chosen_slot.bid][2][7]

        # 绘制方块高亮框
        hightlightwidth = {True: 3, False: 2}[bool(bid)]
        self.hightlight_rect.topleft = (x, y)
        pygame.draw.rect(screen, (0, 0, 0), self.hightlight_rect, hightlightwidth, 3)

        # 左键按下：挖掘
        if event['mb 1'] and bid:
            if self.dig_pos == (col, row):
                self.dig_progress += 1 + dig_speed_addition
                if self.dig_progress < binfo[bid][2]:
                    x += BLOCK_SIZE_1in5
                    y += 5
                    draw_progress(screen, self.dig_progress, binfo[bid][2], x, y, BLOCK_SIZE_1in5 * 3, 2, (88, 255, 188))
                    return
                self.data[row][col] = 0
                if dig_level_addition >= binfo[bid][3]:
                    if chosen_slot.durable:
                        chosen_slot.durable -= 1
                        chosen_slot.update()
                    self.drop_list.append(Drop(binfo[bid][1]))
                    self.drop_list[-1].set_p(mx + random.randint(0, BLOCK_DROP_DELTA), my)
                    page: Page | None = self.function_blocks.get((col, row), None)
                    if page:
                        for slot in page.items:
                            if slot.mode != 'craft':
                                while slot.count:
                                    self.drop_list.append(slot.push_one_out())
                                    self.drop_list[-1].set_p(mx + random.randint(0, BLOCK_DROP_DELTA), my)
                        del self.function_blocks[(col, row)]
            else:
                self.dig_pos = (col, row)
        else:
            self.dig_pos = None
        self.dig_progress = 0
        
        if event['mb 3']:
            match bid:
                case 0:
                    if chosen_slot.bid // 100000 == 2 and binfo[chosen_slot.bid][1]:
                        self.data[row][col] = binfo[chosen_slot.bid][1]
                        chosen_slot.count -= 1
                        chosen_slot.update()
                        match self.data[row][col]:
                            case 100601:
                                pg = Page(300, 200, 400, 200, 'craft', (3, 3))
                                for row_ in range(3):         # 这里row/col避免重名加上下划线
                                    for col_ in range(3):
                                        pg.append(Slot(375 + col_ * SLOT_SIZE, 225 + row_ * SLOT_SIZE))
                                pg.append(Slot(575, 275, 'craft'))
                                self.function_blocks[(col, row)] = pg
                            case 100701:
                                pg = Page(350, 250, 300, 150, 'smelt')
                                pg.append(Slot(375, 275, 'burnable'))
                                pg.append(Slot(375, 325, 'fuel'))
                                pg.append(Slot(575, 300, 'result'))
                                pg.add_extension(Progress(screen, 0, 500, 450, 315, 100, 20, (255, 208, 111), (255, 255, 255)))
                                pg.add_extension(Progress(screen, 0, 500, 450, 335, 100, 20, (96, 88, 88), (255, 255, 255)))
                                self.function_blocks[(col, row)] = pg
                            case 100801:
                                pg = Page(275, 150, 450, 250, 'craft', (4, 4))
                                for row_ in range(4):
                                    for col_ in range(4):
                                        pg.append(Slot(350 + col_ * SLOT_SIZE, 175 + row_ * SLOT_SIZE))
                                pg.append(Slot(625, 250, 'craft'))
                                self.function_blocks[(col, row)] = pg
                            case 101501:
                                pg = Page(225, 200, 550, 200)
                                for row_ in range(3):
                                    for col_ in range(9):
                                        pg.append(Slot(275 + col_ * SLOT_SIZE, 225 + row_ * SLOT_SIZE))
                                self.function_blocks[(col, row)] = pg
                case 100601 | 100701 | 100801 | 101501:
                    player.bag.tap()
                    self.function_blocks[(col, row)].tap()
    
    def update_drop(self):
        for drop in self.drop_list:
            if drop.floating:
                drop.vy += g
            drop.move(self)
            drop.rub_ground()
            drop.show(self)
    
    def set_sight(self, visitor: Entity, offset: Tuple[int, int]):
        ox, oy = offset
        self.x = min(max(0, visitor.x - ox), MPR_px)
        self.y = min(max(0, visitor.y - oy), MPB_px)
    def show(self):
        for row in range(SCH_bl + 1):
            for col in range(SCW_bl + 1):
                bid = self.data[self.y_bl + row][self.x_bl + col]
                if bid:
                    screen.blit(binfo[bid][0], (col * BLOCK_SIZE - self.x_offset, row * BLOCK_SIZE - self.y_offset))
    
    @property
    def x_bl(self) -> int:                         # 地图左上角x坐标(bl)
        return int(self.x / BLOCK_SIZE)
    @property
    def y_bl(self) -> int:                         # 地图左上角y坐标(bl)
        return int(self.y / BLOCK_SIZE)
    @property
    def x_offset(self) -> int | float:             # 地图左上角在屏幕上的x偏移量(px)
        return self.x % BLOCK_SIZE
    @property
    def y_offset(self) -> int | float:             # 地图左上角在屏幕上的y偏移量(px)
        return self.y % BLOCK_SIZE

sightbg = sight.generate_surface(SCW_px, SCH_px, 150, 50)
sightbg.set_alpha(0)
class Celestial_motion:
    def __init__(self, r = SCW_px_half, sunrise = 6, sunset = 18):
        self.r = r * 1.0
        self.sunrise = sunrise * 1.0
        self.sunset = sunset * 1.0
        self.day_long = self.sunset - self.sunrise
        self.rect = pygame.Rect(0, 0, 100, 100)
        self.bg_color = (255, 255, 255)
    def get_angle(self, t: float):
        # θ = π - π * (t - sunrise) / day_long
        return math.pi - math.pi * (t - self.sunrise) / self.day_long
    def update(self, t: float):
        angle = self.get_angle(t)
        x, y = self.get_pos(angle, self.r)
        self.rect.center = math_pos_to_pygame_pos(x, y, SCW_px_half, SCH_px)
    def show(self, t: float):
        screen.fill(self.bg_color)
        if self.sunrise <= t < self.sunset:
            self.update(t)
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 0, 20)
            pygame.draw.rect(screen, (255, 195, 111), self.rect, 5, 20)
        else:
            self.update(t - self.day_long)
            pygame.draw.rect(screen, (66, 111, 255), self.rect, 0, 20)
            pygame.draw.rect(screen, (125, 35, 255), self.rect, 5, 20)
        if self.sunrise - 1 <= t <= self.sunrise:
            value = round((self.sunrise - t) * 255)
            sightbg.set_alpha(value)
            self.bg_color = (255 - value, 255 - value, 255 - value)
        elif self.sunset <= t <= self.sunset + 1:
            value = round((t - self.sunset) * 255)
            sightbg.set_alpha(value)
            self.bg_color = (255 - value, 255 - value, 255 - value)
    @staticmethod
    def get_pos(angle: float, r: float):
        # x = r * cos(θ)
        # y = r * sin(θ)
        return r * math.cos(angle), r * math.sin(angle)

slotimg = ld('slot')
slotimg_selected = ld('slot_red')

class Slot:
    def __init__(self, x: int | float, y: int | float, mode: str = 'normal'):
        self.bid = 0
        self.count = 0
        self.durable = None
        self.mode = mode
        self.selected = False
        self.set_p(x, y)
    def set_p(self, x: int | float, y: int | float):
        self.x = x
        self.y = y
    
    def exchange_with(self, other: Slot):
        b, c, d = self.bid, self.count, self.durable
        self.bid, self.count, self.durable = other.bid, other.count, other.durable
        other.bid, other.count, other.durable = b, c, d
    def give_to(self, other: Slot):
        self.count -= 1
        other.count += 1
        if not other.bid:
            other.bid = self.bid
    def push_one_out(self):
        if self.count:
            self.count -= 1
            new_drop = Drop(self.bid, self.durable if self.durable else 0)
            self.update()
            return new_drop
    
    def select(self, signal: int):
        if self.mode in ['craft', 'burnable', 'fuel', 'result']:
            return
        match signal:
            case [1, 0, 0]:
                self.selected = True
            case [0, 0, 1]:
                self.selected = False
    
    def connect(self, other: Slot, signal: int) -> str | None:
        match self.mode:
            case 'craft':
                return self.connect_craft(other, signal)
            case 'normal':
                self.connect_normal(other, signal)
            case 'burnable' | 'fuel':
                if other.bid:
                    if self.bid and self.bid != other.bid:
                        return
                    if (self.mode == 'burnable') and (other.bid not in burnables):
                        return
                    if (self.mode == 'fuel') and (other.bid not in fuels):
                        return
                self.connect_normal(other, signal)
            case 'result':
                self.connect_craft(other, signal)
    
    def connect_craft(self, other: Slot, signal: int) -> str:
        res = 'failed'
        if signal == 1 and self.bid and other.count + self.count <= 64:
            if other.bid:
                if self.bid != other.bid:
                    return 'failed'
                other.count += self.count
                self.count = 0
            else:
                self.exchange_with(other)
                match other.bid:
                    case 300101:
                        record.record('进击的镐子I')
            res = 'complete'
        self.update()
        return res
    
    def connect_normal(self, other: Slot, signal: int) -> None:
        if not (self.bid or other.bid):           # 格子空，鼠标空
            return
        if self.bid and other.bid:                # 格子有，鼠标有
            if (self.bid == other.bid and self.count == 64) or (self.bid != other.bid):
                if self.mode == 'normal':
                    self.exchange_with(other)
                return
            match signal:
                case 1:
                    if other.count >= 64:
                        self.exchange_with(other)
                        return
                    self.count += other.count
                    other.count = 0
                    other.bid = 0
                    if self.count > 64:
                        other.count = self.count - 64
                        other.bid = self.bid
                        self.count = 64
                case 3:
                    other.give_to(self)
                case 4:
                    other.give_to(self)
                case 5 if other.count < 64:
                    self.give_to(other)
        elif self.bid:                            # 格子有，鼠标空
            match signal:
                case 1:
                    self.exchange_with(other)
                case 3:
                    other.bid = self.bid
                    other.count = self.count // 2
                    self.count -= other.count
                case 5:
                    self.give_to(other)
        else:                                     # 格子空，鼠标有
            match signal:
                case 1:
                    self.exchange_with(other)
                case 3:
                    other.give_to(self)
                case 4:
                    other.give_to(self)
        self.update()
        other.update()
    
    def update(self):
        if self.bid and self.count:
            if self.durable is None:
                return
            if self.durable >= 1:
                return
        self.bid = self.count = 0
        self.durable = None
    
    def show(self):
        if self.mode != 'on mouse':
            screen.blit(slotimg_selected if self.selected else slotimg, (self.x, self.y))
        if self.bid:
            screen.blit(binfo[self.bid][0], (self.x + SLOT_DROP_SPACE, self.y + SLOT_DROP_SPACE))
            if self.count > 9:
                show_text(screen, str(self.count), (255, 255, 255), (self.x + SLOT_DROP_SPACE + DROP_SIZE - 20, self.y + SLOT_DROP_SPACE + DROP_SIZE - 20), 20)
            elif self.count > 1:
                show_text(screen, str(self.count), (255, 255, 255), (self.x + SLOT_DROP_SPACE + DROP_SIZE - 10, self.y + SLOT_DROP_SPACE + DROP_SIZE - 20), 20)
            if self.bid // 100000 == 3:
                if self.durable == None:
                    self.durable = binfo[self.bid][1]
                else:
                    draw_progress(screen, self.durable, binfo[self.bid][1], self.x + SLOT_DROP_SPACE, self.y + SLOT_DROP_SPACE + DROP_SIZE, DROP_SIZE, 2, (255, 0, 0))

class Page:
    def __init__(self, x: int | float, y: int | float, w: int, h: int, mode: str = 'normal', description: Any = ''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.mode = mode
        self.showing = False
        self.items: List[Slot] = []
        self.item_extensions: List[Any] = []
        self.rect = pygame.Rect(x, y, w, h)
        self.description = description
    def tap(self):
        if self.showing:
            self.showing = False
            showing_pages.remove(self)
        else:
            self.showing = True
            showing_pages.append(self)
    def add_extension(self, ext: Any):
        self.item_extensions.append(ext)
    def append(self, item: Slot):
        self.items.append(item)
    def insert_drop(self, bid: int, durable: int | float = 0):
        empty_slot = False
        for slot in self.items:
            if slot.bid == bid and slot.count < 64:
                slot.count += 1
                return True
            if not (slot.bid or empty_slot):
                empty_slot = slot
        if empty_slot:
            empty_slot.bid = bid
            empty_slot.count = 1
            if durable:
                empty_slot.durable = durable
            return True
        return False
    def unselect_all(self):
        for item in self.items:
            item.selected = False
    def show(self):
        if self.showing:
            pygame.draw.rect(screen, (128, 128, 128), self.rect, 0, 10)
            pygame.draw.rect(screen, (0, 68, 68), self.rect, 3, 10)
            for item in self.items:
                item.show()
            for ext in self.item_extensions:
                ext.show()
        elif self.mode == 'player-bag':
            for i in range(9):
                self.items[i].show()

class Entity:
    def __init__(self, w: int, h: int):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.w = w
        self.h = h
        self.hp = -1
        self.floating = True
    def set_p(self, x: int | float | None = None, y: int | float | None = None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
    def set_v(self, vx: int | float | None = None, vy: int | float | None = None):
        if vx is not None:
            self.vx = vx
        if vy is not None:
            self.vy = vy
    def get_rect(self) -> pygame.FRect:
        return pygame.FRect(self.x, self.y, self.w, self.h)
    def collide(self, other: Entity) -> bool:
        return collision(self.x, self.y, self.w, self.h, other.x, other.y, other.w, other.h)
    
    def move(self, map: Map):
        self.floating = True

        # x方向碰撞箱处理
        if self.vx < 0:
            for row in range(self.t_bl, self.b_bl + 1):
                if self.l_bl <= 0 or map.cannot_cross_block(row, self.l_bl - 1):
                    if -self.vx > self.l_space:
                        self.vx = 0               # 碰撞失速
                        self.x -= self.l_space
                    break
        elif self.vx > 0:
            for row in range(self.t_bl, self.b_bl + 1):
                if self.r_bl >= MPW_bl - 1 or map.cannot_cross_block(row, self.r_bl + 1):
                    if self.vx > self.r_space:
                        self.vx = 0
                        self.x += self.r_space
                    break
        self.set_p(x = self.x + self.vx)             # 不先移动x的后果是，遇到左上角向右下这类情况，直接卡墙！

        # y方向碰撞箱处理
        if self.vy < 0:
            for col in range(self.l_bl, self.r_bl + 1):
                if self.t_bl <= 0 or map.cannot_cross_block(self.t_bl - 1, col):
                    if -self.vy > self.t_space:
                        self.vy = 0
                        self.y -= self.t_space
                    break
        elif self.vy > 0:
            for col in range(self.l_bl, self.r_bl + 1):
                if self.b_bl >= MPH_bl - 1 or map.cannot_cross_block(self.b_bl + 1, col):
                    if self.vy > self.b_space:
                        self.floating = False
                        '''
                        速度与扣血关系标准：
                        速度9    数值1    平方1    扣血0.5
                        速度10   数值2    平方4    扣血2.0     | 与y=x的交点（与线性速度大小的分界线）
                        速度11   数值3    平方9    扣血4.5
                        速度13   数值5    平方25   扣血12.5
                        速度15   数值7    平方49   扣血24.5
                        速度20   数值12   平方144  扣血72.0
                        速度50   数值42   平方1764 扣血882.0
                        '''
                        if self.vy > 8:       # 摔落速度>8 扣血
                            self.hp -= (self.vy - 8) ** 2 / 2
                        self.vy = 0
                        self.y += self.b_space
                    break
        self.set_p(y = self.y + self.vy)
    
    def rub_ground(self):
        if self.floating:
            return
        if abs(self.vx):
            self.vx *= GROUND_FRICTION
            if abs(self.vx) < 0.001:
                self.vx = 0.0
    
    def draw(self, x: int | float, y: int | float):
        pass
    def show(self, map: Map):
        x, y = mp_to_sc(map, (self.x, self.y))
        if -self.w <= x <= SCW_px and -self.h <= y <= SCH_px:
            self.draw(x, y)
    
    @property
    def l(self) -> int | float:
        return self.x
    @property
    def r(self) -> int | float:
        return self.x + self.w - 1
    @property
    def t(self) -> int | float:
        return self.y
    @property
    def b(self) -> int | float:
        return self.y + self.h - 1
    @property
    def cx(self) -> float:
        return self.x + self.w / 2
    @property
    def cy(self) -> float:
        return self.y + self.h / 2
    @property
    def l_bl(self) -> int:
        return int(self.l / BLOCK_SIZE)
    @property
    def r_bl(self) -> int:
        return int(self.r / BLOCK_SIZE)
    @property
    def t_bl(self) -> int:
        return int(self.t / BLOCK_SIZE)
    @property
    def b_bl(self) -> int:
        return int(self.b / BLOCK_SIZE)
    @property
    def l_space(self) -> int | float:            # 实体左边到左边block的距离(px) 下面以此类推
        return self.l % BLOCK_SIZE
    @property
    def r_space(self) -> int | float:
        return BLOCK_SIZE - 1 - self.r % BLOCK_SIZE
    @property
    def t_space(self) -> int | float:
        return self.t % BLOCK_SIZE
    @property
    def b_space(self) -> int | float:
        return BLOCK_SIZE - 1 - self.b % BLOCK_SIZE

class Drop(Entity):
    def __init__(self, bid: int, durable: int | float = 0):
        super().__init__(DROP_SIZE, DROP_SIZE)
        self.canget = True
        self.bid = bid
        self.durable = durable
    def draw(self, x: int | float, y: int | float):
        screen.blit(binfo[self.bid][0], (x, y))

class Animal(Entity):
    def __init__(self, hp: int | float, w: int, h: int):
        super().__init__(w, h)
        self.hp = hp
        self.jump_force = 5.0
        self.walkspeed = 3.0

class Player(Animal):
    def __init__(self):
        super().__init__(100, 40, 120)
        self.hunger = 0         # >100时因饥饿而扣血
        self.saturation = 150     # 饱和度（饱食度）
        self.theta = 0          # 手中物品的角度
        self.power = 5
        self.rect = self.get_rect()
        self.left_eye = pygame.FRect(-10, -10, 4, 4)
        self.right_eye = pygame.FRect(-10, -10, 4, 4)
        self.bag = Page(225, 430, 550, 260, 'player-bag', (4, 9))
        for i in range(9):
            self.bag.append(Slot(275 + i * SLOT_SIZE, 625))
        for row in range(3):
            for col in range(9):
                self.bag.append(Slot(275 + col * SLOT_SIZE, 450 + row * SLOT_SIZE))
    def control(self):
        if self.floating:
            self.vy += g
        elif event_state[pygame.K_w] and (not showing_pages):
            self.get_hunger(20)
            self.vy = -self.jump_force
            self.floating = True
        self.vx = (event_state[pygame.K_d] - event_state[pygame.K_a]) * (not showing_pages) * self.walkspeed
        self.get_hunger(abs(self.vx)*0.5)

    def get_drop(self, drop_list: List[Drop]):
        for drop in drop_list:
            if self.collide(drop):
                if drop.canget and self.bag.insert_drop(drop.bid, drop.durable):
                    drop_list.remove(drop)
            elif not drop.canget:
                drop.canget = True
    
    def get_hunger(self, speed: int | float = 1):
        if self.saturation > 0:
            self.saturation -= 0.01 * speed
        elif self.hunger >= 100:
            self.hp -= 0.1 * speed
        else:
            self.hunger += 0.003 * speed
    def next(self, map: Map):
        self.show(map)
        screen.blit(sightbg, (0, 0))
        self.bag.show()
        draw_progress(screen, self.hp, 100, 275, 615, 150, 15)
        draw_progress(screen, self.hunger, 100, 575, 615, 150, 15, (0, 0, 0), (255, 200, 111))
        draw_progress(screen, self.saturation, 150, 575, 605, 150, 6, (255, 255, 255), (0, 0, 0))
        show_text(screen, f'HP: {self.hp:.1f}/100', (255, 255, 255), (275, 607), 15)
        show_text(screen, f'HG: {self.hunger:.1f}/100', (255, 255, 255), (575, 607), 15)
        self.get_hunger()
        self.control()
        self.move(map)
        self.get_drop(map.drop_list)
        if self.hp <= 0:
            player.set_p(y=325*BLOCK_SIZE)
            self.hp = 100
            self.hunger = 0
    def draw(self, x: int | float, y: int | float):
        mpos = event_state['mpos']
        # 身体
        self.rect.topleft = (x, y)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 3)
        # 眼睛
        eyecenter = (self.rect.centerx, self.rect.top + 13)
        self.left_eye.center = self.right_eye.center = (eyecenter[0] + max(-5, (min(5, (mpos[0] - eyecenter[0]) * 0.02))),
                                                        eyecenter[1] + max(-5, (min(5, (mpos[1] - eyecenter[1]) * 0.02))))
        self.left_eye.x -= 6
        self.right_eye.x += 6
        pygame.draw.rect(screen, (0, 0, 0), self.left_eye, 0)
        pygame.draw.rect(screen, (0, 0, 0), self.right_eye, 0)
        # 手中物品
        onhand_bid = self.bag.items[inventory_chosen_index].bid
        if onhand_bid:
            onhand_pos = (self.rect.right, self.rect.centery)
            onimg = pygame.transform.scale(binfo[onhand_bid][0], (20, 20))      # 缩放
            self.theta = get_rotate_angle(*onhand_pos, *mpos)                     # 计算角度
            onimg = pygame.transform.rotate(onimg, self.theta)                       # 面向鼠标指针
            onrect = onimg.get_rect(center=onhand_pos)                          # 便于获取新位置
            screen.blit(onimg, onrect)

def get_recipe(slot_list: List[Slot], row: int, col: int) -> Tuple[int, int]:
    recipe = [[slot_list[i * col + j].bid for j in range(col)] for i in range(row)]
    top, left = row - 1, col - 1
    right = bottom = 0
    for i in range(row):
        for j in range(col):
            if recipe[i][j]:
                top = min(top, i)
                bottom = max(bottom, i)
                left = min(left, j)
                right = max(right, j)
    if top > bottom or left > right:
        return (0, 0)
    recipe_clip = tuple(tuple(recipe[i][j] for j in range(left, right + 1)) for i in range(top, bottom + 1))
    if recipe_clip in recipes:
        return recipes[recipe_clip]
    return (0, 0)

def get_burn(smelt_page: Page):
    if smelt_page in using_smelt_pages:
        return
    burn_slot, fuel_slot, res_slot = smelt_page.items
    burn, fuel, res = burn_slot.bid, fuel_slot.bid, res_slot.bid
    if (not (burn and fuel)) or (res and res != burnables[burn]):
        return
    smelt_page.item_extensions[1].set(fuels[fuel], fuels[fuel])
    fuel_slot.count -= 1
    fuel_slot.update()
    using_smelt_pages.append(smelt_page)

def sc_to_mp(map: Map, pos: Tuple[int | float, int | float]) -> Tuple[int | float, int | float]:
    x, y = pos
    return x + map.x, y + map.y
def mp_to_sc(map: Map, pos: Tuple[int | float, int | float]) -> Tuple[int | float, int | float]:
    x, y = pos
    return x - map.x, y - map.y
def px_to_bl(pos: Tuple[int | float, int | float]) -> Tuple[int | float, int | float]:
    x, y = pos
    return int(x / BLOCK_SIZE), int(y / BLOCK_SIZE)
def bl_to_px(pos: Tuple[int | float, int | float]) -> Tuple[int | float, int | float]:
    x, y = pos
    return x * BLOCK_SIZE, y * BLOCK_SIZE



event_state = {
    pygame.K_UP: 0,
    pygame.K_DOWN: 0,
    pygame.K_LEFT: 0,
    pygame.K_RIGHT: 0,
    pygame.K_w: 0,
    pygame.K_s: 0,
    pygame.K_a: 0,
    pygame.K_d: 0,
    pygame.K_SPACE: 0,
    'mb 1': 0,        # 鼠标左键 (mb = mouse button)
    'mb 2': 0,        # 鼠标中键
    'mb 3': 0,        # 鼠标右键
    'mb 4': 0,        # 鼠标滚轮向上
    'mb 5': 0,        # 鼠标滚轮向下
    'mpos': (500, 350),   # 鼠标位置 (scx, scy) (px)
}

clock = pygame.time.Clock()
mouse_slot = Slot(0, 0, 'on mouse')
total_gt = 0
game_start_time = time.time()

celestial = Celestial_motion()
record = Record()
map = Map()
map.load(save.data)
slot_select_mode = False
showing_pages: List[Page] = []
using_smelt_pages: List[Page] = []
craft_page = Page(300, 200, 400, 200, 'craft', (2, 2))
for row in range(2):
    for col in range(2):
        craft_page.append(Slot(400 + col * SLOT_SIZE, 250 + row * SLOT_SIZE))
craft_page.append(Slot(550, 275, 'craft'))
player = Player()
inventory_chosen_index = 0
inventory_chosen_rect = pygame.Rect(player.bag.items[0].x, player.bag.items[0].y, SLOT_SIZE, SLOT_SIZE)

player.set_p(y=325*BLOCK_SIZE)
player.bag.items[0].bid, player.bag.items[0].count = 200301, 20
player.bag.items[1].bid, player.bag.items[1].count = 200801, 1
player.bag.items[2].bid, player.bag.items[2].count = 200701, 1
player.bag.items[3].bid, player.bag.items[3].count = 201001, 16
player.bag.items[4].bid, player.bag.items[4].count = 200901, 8



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.MOUSEMOTION:
            event_state['mpos'] = event.pos
            if slot_select_mode:
                for page in showing_pages:
                    for slot in page.items:
                        if collision(slot.x, slot.y, SLOT_SIZE, SLOT_SIZE, *event.pos, 1, 1):
                            slot.select(event.buttons)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            event_state[f'mb {event.button}'] = 1
            if showing_pages:        # 打开背包的情况
                # 选择模式有滚轮就执行这里。但选择模式左右中键和普通模式情况一样，跳到普通模式板块。
                if slot_select_mode:
                    if event.button == 4:
                        for page in showing_pages:
                            for slot in page.items:
                                if not mouse_slot.bid:
                                    break
                                if slot.selected:
                                    if slot.bid == mouse_slot.bid and slot.count < 64:
                                        slot.count += 1
                                        mouse_slot.count -= 1
                                        mouse_slot.update()
                                    elif not slot.bid:
                                        slot.bid = mouse_slot.bid
                                        slot.count = 1
                                        mouse_slot.count -= 1
                                        mouse_slot.update()
                        continue
                    elif event.button == 5:
                        for page in showing_pages:
                            for slot in page.items:
                                if slot.selected and slot.bid:
                                    if (slot.bid == mouse_slot.bid and mouse_slot.count < 64) or (not mouse_slot.bid):
                                        slot.count -= 1
                                        mouse_slot.count += 1
                                        if not mouse_slot.bid:
                                            mouse_slot.bid = slot.bid
                                        slot.update()
                        continue
                # 普通模式
                res = crafted = False
                for page in showing_pages:
                    for slot in page.items:
                        if collision(slot.x, slot.y, SLOT_SIZE, SLOT_SIZE, *event.pos, 1, 1):
                            res = slot.connect(mouse_slot, event.button)
                            if slot.mode == 'craft' and res == 'complete':
                                crafted = True
                            break
                    if res in [None, 'complete']:      # res=False说明没有点击格子，否则都是点击了，因为res返回None或者'complete'点击了
                        break
                if crafted:      # 如果合成了物品，那么清空合成需要的物品
                    for page in showing_pages:
                        if page.mode == 'craft':
                            for slot in page.items:
                                if slot.bid:
                                    slot.count -= 1
                                    slot.update()
            else:       # 没有打开背包
                if event.button == 4:
                    inventory_chosen_index = max(0, inventory_chosen_index - 1)
                    inventory_chosen_rect.x = player.bag.items[inventory_chosen_index].x
                elif event.button == 5:
                    inventory_chosen_index = min(8, inventory_chosen_index + 1)
                    inventory_chosen_rect.x = player.bag.items[inventory_chosen_index].x
        
        elif event.type == pygame.MOUSEBUTTONUP:
            event_state[f'mb {event.button}'] = 0
            for page in showing_pages:
                if page.mode == 'craft':
                    page.items[-1].bid, page.items[-1].count = get_recipe(page.items, *page.description)
                elif page.mode == 'smelt':
                    get_burn(page)
        
        elif event.type == pygame.KEYDOWN:
            event_state[event.key] = 1
            if event.key == ord('q'):
                drop = player.bag.items[inventory_chosen_index].push_one_out()
                if drop is None:
                    continue
                vx = math.cos(math.radians(player.theta)) * player.power
                vy = -math.sin(math.radians(player.theta)) * player.power
                drop.set_p(player.r, player.cy - DROP_SIZE_HALF)
                drop.set_v(vx, vy)
                drop.canget = False
                map.drop_list.append(drop)
            if event.key == ord('e'):
                if not showing_pages:
                    player.bag.tap()
                    craft_page.tap()
                else:
                    while showing_pages:
                        showing_pages[-1].tap()
                continue
            if showing_pages:
                if event.key == ord('s'):                      # select 开关选择模式
                    slot_select_mode = not slot_select_mode
                    for page in showing_pages:
                        page.unselect_all()
                if slot_select_mode:
                    if event.key == ord('a'):                  # average 平均分配物品
                        all_put: List[Slot] = []
                        for page in showing_pages:
                            for slot in page.items:
                                if slot.selected and ((not slot.bid) or (slot.bid and slot.bid == mouse_slot.bid and slot.count < 64)):
                                    all_put.append(slot)               # 加入的选中的slot满足：1.没有物品 2.有物品且和鼠标的相同且没满
                        count = len(all_put)
                        if mouse_slot.count < count:                   # 鼠标数量不够平均分，直接跳过了
                            continue
                        adds = mouse_slot.count // count               # adds >= 1
                        overflow = mouse_slot.count % count            # 0 <= overflow数量 <= 原来数量
                        for slot in all_put:
                            slot.count += adds
                            if not slot.bid:
                                slot.bid = mouse_slot.bid
                            if slot.count > 64:
                                overflow += slot.count - 64
                                slot.count = 64
                        mouse_slot.count = overflow
                        mouse_slot.update()
                    elif event.key == ord('d'):                  # dight 整顿物品
                        ...
                    elif event.key == ord('f'):                  # fill 填充选择框到最小能容纳的矩形
                        for page in showing_pages:
                            if page.description:
                                if page.mode == 'player-bag':
                                    lis = page.items[9:] + page.items[:9]
                                elif page.mode == 'craft':
                                    lis = page.items[:-1]
                                else:
                                    lis = page.items
                                t, l = row, col = page.description
                                t -= 1; l -= 1
                                r = b = 0
                                for i in range(row):
                                    for j in range(col):
                                        if lis[i * col + j].selected:
                                            t = min(t, i)
                                            b = max(b, i)
                                            l = min(l, j)
                                            r = max(r, j)
                                if t > b or l > r:
                                    continue
                                for i in range(t, b + 1):
                                    for j in range(l, r + 1):
                                        lis[i * col + j].selected = True
            else:
                if 49 <= event.key <= 57:
                    inventory_chosen_index = event.key - 49
                    inventory_chosen_rect.x = player.bag.items[inventory_chosen_index].x
        
        elif event.type == pygame.KEYUP:
            event_state[event.key] = 0
            for page in showing_pages:
                if page.mode == 'craft':
                    page.items[-1].bid, page.items[-1].count = get_recipe(page.items, *page.description)
                elif page.mode == 'smelt':
                    get_burn(page)

    screen.fill((255, 255, 255))

    smelt_index = 0
    while smelt_index < len(using_smelt_pages):
        smelt = using_smelt_pages[smelt_index]
        progress: Progress = smelt.item_extensions[0]
        rest: Progress = smelt.item_extensions[1]
        if rest.is_empty:
            if smelt.items[1].bid:
                rest.set(fuels[smelt.items[1].bid], fuels[smelt.items[1].bid])
                smelt.items[1].count -= 1
                smelt.items[1].update()
                break
            progress.advance(-2)
            if progress.is_empty:
                using_smelt_pages.pop(smelt_index)
                smelt_index -= 1
        else:
            if smelt.items[0].bid:
                progress.advance()
            else:
                progress.clear()
            rest.advance(-1)
        if progress.is_full:
            if not smelt.items[2].bid:
                smelt.items[2].bid = burnables[smelt.items[0].bid]
                smelt.items[2].count = 1
            else:
                smelt.items[2].count += 1
            smelt.items[0].count -= 1
            smelt.items[0].update()
            progress.clear()
        smelt_index += 1

    total_gt += 1
    total_hours = total_gt / 100 / 5 + 6      # 现实5s为游戏中1h
    game_days = total_hours // 24             # 游戏内部经过的天数
    game_hours = total_hours % 24             # 游戏内部时间(小时)
    celestial.show(game_hours)

    map.set_sight(player, (SCW_px_half - player.w // 2, SCH_px_half - player.h // 2))
    map.show()
    if not showing_pages:
        map.recv(event_state, player)
    map.update_drop()
    player.next(map)
    pygame.draw.rect(screen, (33, 233, 255), inventory_chosen_rect, 3, 5)
    for page in showing_pages:
        if page.mode != 'player-bag':            # player-bag在玩家的next里面更新过了
            page.show()

    record.show(screen)
    mouse_slot.set_p(*event_state['mpos'])
    mouse_slot.show()

    pygame.display.flip()
    clock.tick(100)