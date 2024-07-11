import pygame

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
recipe = {
    (
        (1004,),
    ): (1005,4),
    (
        (1011,),
    ): (2003,9),
    (
        (1012,),
    ): (2003,16),
    (
        (1005,),
        (1005,),
    ): (2001,4),
    (
        (1005,1005),
        (1005,1005),
    ): (1006,1),
    (
        (1003,1003,1003),
        (1003,1006,1003),
        (1003,1003,1003),
    ): (1007,1),
    (
        (1003,1003,1003),
        (1003,0,1003),
        (1003,1003,1003),
    ): (1010,1),
    (
        (1005,1005,1005),
        (0,2001,0),
        (0,2001,0),
    ): (3001,1),
    (
        (1003,1003,1003),
        (0,2001,0),
        (0,2001,0),
    ): (3002,1),
    (
        (2003,2003,2003),
        (0,2001,0),
        (0,2001,0),
    ): (3003,1),
    (
        (2004,2004,2004),
        (0,2001,0),
        (0,2001,0),
    ): (3004,1),
    (
        (2005,2005,2005),
        (0,2001,0),
        (0,2001,0),
    ): (3005,1),
    (
        (2003,2003,2003),
        (2003,2003,2003),
        (2003,2003,2003),
    ): (1011,1),
    (
        (2003,2003,2003,2003),
        (2003,1011,1011,2003),
        (2003,1011,1011,2003),
        (2003,2003,2003,2003),
    ): (1012,1),
}
record_color = {
    '新手': (0,0,0),
    '入门': (88,88,88),
    '初级': (100,100,255),
    '中级': (100,255,100),
    '高级': (255,100,100),
    '特级': (200,100,255),
    '史诗': (100,255,200),
    '传说': (255,255,100),
}
record_dict = {
    '挖掘！': [0,'新手','完成第一个方块的挖掘'],
    '伐木工': [0,'新手','砍一下木头'],
    '背包！': [0,'新手','按下[E]打开背包'],
    '是时候开始工作了': [0,'新手','合成3*3木工作台'],
    '进击的镐子I': [0,'入门','合成第一个木镐'],
    '进击的镐子II': [0,'入门','合成第一个石镐'],
    '进击的镐子III': [0,'初级','合成第一个铁镐'],
    '进击的镐子IV': [0,'初级','合成第一个金镐'],
    '进击的镐子V': [0,'中级','合成第一个钻石镐'],
    '石器时代': [0,'入门','完成第一个石块的挖掘'],
    '一起燃烧吧': [0,'入门','合成第一个熔炉，这玩意应该需要点燃料。'],
    '铁器时代': [0,'入门','完成第一个铁矿的挖掘，铁是很重要的物质。'],
    '燃料！': [0,'入门','完成第一个煤矿的挖掘，煤炭可以在熔炉中使用。（其实木头也可以当燃料）'],
    '土产过多': [0,'入门','一个物品格子中放满了土方块'],
    '砖家': [0,'初级','一个物品格子中放满了石块'],
    '铁锭！': [0,'初级','熔炉煅烧出来的东西往往很有用，比如制作一些工具、防具、攻击器具等。'],
    '铁饭碗': [0,'初级','在5*5铁工作台上工作'],
}



# 两点距离公式
def get_distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2) ** 0.5

# 碰撞箱
def collision(x1, y1, w1, h1, x2, y2, w2, h2):
    l1, r1, t1, b1 = x1, x1 + w1, y1, y1 + h1
    l2, r2, t2, b2 = x2, x2 + w2, y2, y2 + h2
    return not (l1 < r1 < l2 < r2 or 
                l2 < r2 < l1 < r1 or 
                t1 < b1 < t2 < b2 or 
                t2 < b2 < t1 < b1)

# 滑块
class Slider:
    def __init__(self,value,full,digit=1):
        self.value = value
        self.full = full
        self.digit = digit
    def __iadd__(self,n):
        self.value = max(0, min(self.value + n, self.full))
        return self
    def __isub__(self,n):
        self.value = max(0, min(self.value - n, self.full))
        return self
    def __imul__(self,n):
        self.value = max(0, min(self.value * n, self.full))
        return self
    def __itruediv__(self,n):
        self.value = max(0, min(self.value / n, self.full))
        return self
    def __add__(self,n):
        return round(max(0, min(self.value + n, self.full)), self.digit)
    def __sub__(self,n):
        return round(max(0, min(self.value - n, self.full)), self.digit)
    def __mul__(self,n):
        return round(max(0, min(self.value * n, self.full)), self.digit)
    def __truediv__(self,n):
        return round(max(0, min(self.value / n, self.full)), self.digit)
    def __lt__(self,n):
        return self.value < n
    def __le__(self,n):
        return self.value <= n
    def __gt__(self,n):
        return self.value > n
    def __ge__(self,n):
        return self.value >= n
    def clear(self):
        self.value = 0
    def fill(self):
        self.value = self.full
    def set(self,n):
        self.value = n
    def change_full(self,n):
        self.full = n
    @property
    def v(self):
        return round(self.value,self.digit)
    @property
    def f(self):
        return round(self.full,self.digit)
    @property
    def part(self):
        return self.value / self.full
    @property
    def isf(self):
        return self.v >= self.f