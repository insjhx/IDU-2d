import random
import math
import time

random.seed(114514)

def move(x, y, steps, radians):
    x += steps * math.cos(radians)
    y += steps * -math.sin(radians)
    return (round(x, 12), round(y, 12))

def noise(basicx=0, basicy=0, times=1000, steep=40, amplitude1=105, amplitude2=105, rough=6):
    '''
    basic: 地基高度
    times: 至少操作次数（描点数量）
    steep: 陡峭程度限制（角度）
    amplitude1: 上振幅限制
    amplitude2: 下振幅限制
    rough: 粗糙度
    '''
    x = basicx
    y = basicy
    angle = 0

    l = []

    while times:
        if angle <= -random.randint(steep - 10, steep + 10) or y >= basicy + random.randint(amplitude1 - 5, amplitude1 + 10):
            angle += random.uniform(0, rough / 2)
        elif angle >= random.randint(steep - 10, steep + 10) or y <= basicy - random.randint(amplitude2 - 5, amplitude2 + 10):
            angle -= random.uniform(0, rough / 2)
        else:
            angle += random.uniform(-rough, rough)

        radians = math.radians(angle)
        x, y = move(x, y, 1, radians)

        l.append((round(x), round(y)))
        times -= 1
    
    return l

def connect_noise(length):
    line = []
    l = random.randint(256, 512)
    n = noise(0, -15, l, 15, 40, 40, 5)   # 平原
    line += n
    x, y = n[-1]
    while l < length:
        if y <= -30:
            nxt_w = random.randint(89, 256)
            n = noise(x, y, nxt_w, 30, 80, 10, 6)    # 低->高
        elif -30 <= y <= 10:
            nxt_w = random.randint(384, 1280)
            n = noise(x, y, nxt_w, 15, 40, 15, 5)    # 平原
        elif 11 <= y <= 52:
            nxt_w = random.randint(128, 1024)
            n = noise(x, y, nxt_w, 45, 85, 60, 6)    # 丘陵
        elif 88 <= y <= 130:
            nxt_w = random.randint(256, 832)
            n = noise(x, y, nxt_w, 25, 95, 35, 6)    # 高原
        elif 53 <= y <= 87:
            nxt_w = random.randint(128, 832)
            n = noise(x, y, nxt_w, 75, 135, 45, 8)   # 山地
        elif 66 <= y:
            nxt_w = random.randint(89, 256)
            n = noise(x, y, nxt_w, 60, 0, 150, 8)    # 高->低
        line += n
        x, y = n[-1]
        l += nxt_w
    return line

