from __future__ import annotations
from typing import Any
import pygame, sys

class Font:
    def __init__(self, font_name, size):
        self.font = pygame.font.Font(font_name, size)

class Text:
    def __init__(self, text, font: Font):
        self.text = text
        self.font = font
        ...

class Frame:
    def __init__(self, master: Frame | Page | Any = None, w = 0, h = 0, x = 0, y = 0, **styles):
        self.master = master
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, w, h)
        if master is None:
            self.flip = lambda: None
        self.styles = {
            "bg_color": False,
            "border": 0,
            "border_color": False,
            "border_radius": 0,
        }
        self.set_style(**styles)
        self.bound_events = {}
        self.show()
    def __str__(self):
        return f"Frame(w={self.w}, h={self.h}, x={self.x}, y={self.y})"
    def __repr__(self):
        return f"Frame(w={self.w}, h={self.h}, x={self.x}, y={self.y})"
    
    def set_style(self, **styles):
        self.styles.update(styles)
    def get_style(self, key):
        if key == "all":
            return self.styles
        return self.styles.get(key, None)
    
    def get_surface(self):
        return self.surface
    def get_rect(self):
        return self.rect
    
    def move(self, x, y):
        self.rect.move_ip(x, y)
    def set_pos(self, x, y):
        self.rect.topleft = (x, y)
    
    def show(self):
        self.showing = True
    def hide(self):
        self.showing = False
    def switch(self):
        self.showing = not self.showing
    
    def appoint_surface(self, surface: pygame.Surface):
        self.surface = surface
        self.rect = surface.get_rect(topleft=self.rect.topleft)
    def flip(self):
        if self.showing:
            self.surface.fill((0, 0, 0, 0))
            if self.styles["bg_color"]:
                pygame.draw.rect(self.surface, self.styles["bg_color"], (0, 0, self.w, self.h), 0, self.styles["border_radius"])
            if self.styles["border"] and self.styles["border_color"]:
                pygame.draw.rect(self.surface, self.styles["border_color"], (0, 0, self.w, self.h), self.styles["border"], self.styles["border_radius"])
            self.master.surface.blit(self.surface, self.rect)
    
    def bind_event(self, event_type, func):
        self.bound_events[event_type] = func
    def unbind_event(self, event_type):
        if event_type in self.bound_events:
            del self.bound_events[event_type]
    def handle_event(self, event):
        if event.type in self.bound_events:
            self.bound_events[event.type](event)

    @property
    def x(self):
        return self.rect.x
    @x.setter
    def x(self, value):
        self.rect.x = value
    @property
    def y(self):
        return self.rect.y
    @y.setter
    def y(self, value):
        self.rect.y = value
    @property
    def w(self):
        return self.rect.w
    @w.setter
    def w(self, value):
        self.rect.w = value
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
    @property
    def h(self):
        return self.rect.h
    @h.setter
    def h(self, value):
        self.rect.h = value
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
    
    @property
    def left(self):
        return self.rect.left
    @left.setter
    def left(self, value):
        self.rect.left = value
    @property
    def right(self):
        return self.rect.right
    @right.setter
    def right(self, value):
        self.rect.right = value
    @property
    def top(self):
        return self.rect.top
    @top.setter
    def top(self, value):
        self.rect.top = value
    @property
    def bottom(self):
        return self.rect.bottom
    @bottom.setter
    def bottom(self, value):
        self.rect.bottom = value
    
    @property
    def midleft(self):
        return self.rect.midleft
    @midleft.setter
    def midleft(self, value):
        self.rect.midleft = value
    @property
    def midright(self):
        return self.rect.midright
    @midright.setter
    def midright(self, value):
        self.rect.midright = value
    @property
    def midtop(self):
        return self.rect.midtop
    @midtop.setter
    def midtop(self, value):
        self.rect.midtop = value
    @property
    def midbottom(self):
        return self.rect.midbottom
    @midbottom.setter
    def midbottom(self, value):
        self.rect.midbottom = value
    
    @property
    def center(self):
        return self.rect.center
    @center.setter
    def center(self, value):
        self.rect.center = value
    @property
    def centerx(self):
        return self.rect.centerx
    @centerx.setter
    def centerx(self, value):
        self.rect.centerx = value
    @property
    def centery(self):
        return self.rect.centery
    @centery.setter
    def centery(self, value):
        self.rect.centery = value
    
    @property
    def topleft(self):
        return self.rect.topleft
    @topleft.setter
    def topleft(self, value):
        self.rect.topleft = value
    @property
    def topright(self):
        return self.rect.topright
    @topright.setter
    def topright(self, value):
        self.rect.topright = value
    @property
    def bottomleft(self):
        return self.rect.bottomleft
    @bottomleft.setter
    def bottomleft(self, value):
        self.rect.bottomleft = value
    @property
    def bottomright(self):
        return self.rect.bottomright
    @bottomright.setter
    def bottomright(self, value):
        self.rect.bottomright = value

class Page(Frame):
    def __init__(self, master: Frame | Page | Any = None, w = 0, h = 0, x = 0, y = 0, **styles):
        super().__init__(master, w, h, x, y, **styles)
        self.children = {}
    def __str__(self):
        return f"Page(w={self.w}, h={self.h}, x={self.x}, y={self.y})"
    def __repr__(self):
        return f"Page(w={self.w}, h={self.h}, x={self.x}, y={self.y})"
    def __getitem__(self, name):
        return self.children[name]
    def __setitem__(self, name, child):
        self.children[name] = child
    def __delitem__(self, name):
        del self.children[name]

    def add_child(self, name, child):
        self.children[name] = child
    def remove_child(self, name):
        if name in self.children:
            del self.children[name]
    def child(self, name):
        return self.children.get(name, False)
    def flip(self):
        self.surface.fill((0, 0, 0, 0))
        if self.styles["bg_color"]:
            pygame.draw.rect(self.surface, self.styles["bg_color"], (0, 0, self.w, self.h), 0, self.styles["border_radius"])
        if self.styles["border"] and self.styles["border_color"]:
            pygame.draw.rect(self.surface, self.styles["border_color"], (0, 0, self.w, self.h), self.styles["border"], self.styles["border_radius"])
        for child in self.children:
            self.children[child].flip()
        self.master.surface.blit(self.surface, self.rect)

def generate_frame_of(surface):
    frame = Frame()
    frame.appoint_surface(surface)
    return frame

screen = pygame.display.set_mode((800, 600))
scframe = generate_frame_of(screen)
myframe = Page(master = scframe, w = 200, h = 200, x = 100, y = 100)
myframe.set_style(bg_color = (0, 255, 0), border = 5, border_color = (0, 0, 255), border_radius = 10)

def func(event):
    global myframe
    myframe.center = event.pos
myframe.bind_event(pygame.MOUSEMOTION, func)

while True:
    for event in pygame.event.get():
        myframe.handle_event(event)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    screen.fill((255, 255, 255))
    myframe.flip()

    pygame.display.update()