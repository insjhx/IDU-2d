from __future__ import annotations

import pygame
import random
import time
import math
import sys

''' 游戏编写设定
量词使用:
  sc: screen量词 (相对于screen而言)
  mp: map量词 (相对于map而言)
  px: pixel量词 (像素单位)
  bl: block量词 (方块单位)
  aa: area量词 (区块单位)
  * example: mp_bl意思是相对map的以block为单位的量词
'''

class Api:
    def __init__(self):
        self.name = 'api'

f = pygame.FRect(0.5, 0.5, 6.89, 10.7)