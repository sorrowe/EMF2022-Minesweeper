from tidal import *
from app import App
from textwindow import TextWindow
from buttons import Buttons
from random import randrange

import vga2_8x8 as default_font
import vga2_16x16 as number_font

WIDTH=6
HEIGHT=9
COUNT=10
CELLS=WIDTH*HEIGHT

SQ_SIZE = 22
FONT_OFFSET = 3
GRIDV_OFF = 11
GRIDH = HEIGHT*SQ_SIZE
GRIDH_OFF = 1

class Game():
    def __init__(self, width, height, count):
        self.w = width
        self.h = height
        self.count = count
        self.target = (self.w * self.h) - self.count
        self.found = 0
        self.tried = []
        #self.tried = [[False for i in range(width)] for j in range(height)]
        self.flags = []
        #self.flags = [[False for i in range(width)] for j in range(height)]
        self.bombs = []

       
    def make_bombs(self, x_init, y_init):
        made = 0
        initial_pos = (x_init, y_init)
        while made < self.count:
            proposed =(randrange(self.w), randrange(self.h))
            if proposed not in self.bombs and proposed != initial_pos:
                self.bombs.append(proposed)
                made += 1
    
    def get_tried(self, x, y):
        return (x,y) in self.tried
        #return self.tried[y][x]

    def set_tried(self, x, y):
        if (x,y) not in self.tried:
            self.tried.append((x,y))

    def get_flag(self, x,y):
        return (x,y) in self.flags
        #return self.flags[y][x]

    def toggle_flag(self, x, y):
        if (x,y) in self.flags:
            self.flags.remove((x,y))
        else:
            self.flags.append((x,y))

    def get_is_bomb(self, x,y):
        if len(self.bombs) == 0:
            self.make_bombs(x,y)
        return (x,y) in self.bombs

    def get_state(self, x, y):
        pos = (x,y)
        return (
            pos in self.tried,
            pos in self.flags,
            pos in self.bombs,
        )
    
    def is_won(self):
        return len(self.tried) == self.target


class CursorManager():
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self._x = 0
        self._y = 0

    @property
    def X(self):
        return self._x
    
    @property
    def Y(self):
        return self._y
    
    def move(self, x=0, y=0):
        self._x = (self._x + x) % self.w
        self._y = (self._y + y) % self.h

    def zero(self):
        self._x = 0
        self._y = 0

class Minesweeper(App):

    def __init__(self):
        super().__init__()
        window = MSWindow("Minesweeper")
        self.push_window(window, activate=False)

class MSWindow(TextWindow):

    def __init__(self, name):
        super().__init__(bg=BRAND_NAVY, fg=WHITE, title=name, buttons=Buttons(), font=default_font)
        self.name = name

        self.cursor = CursorManager(WIDTH, HEIGHT)
        self.game = Game(WIDTH, HEIGHT, COUNT)

        self.main_buttons = self.buttons
        self.buttons.on_press(JOY_CENTRE, lambda: self.check_square())
        self.buttons.on_press(JOY_LEFT, lambda: self.move_cursor(x=-1))
        self.buttons.on_press(JOY_RIGHT, lambda: self.move_cursor(x=1))
        self.buttons.on_press(JOY_UP, lambda: self.move_cursor(y=-1))
        self.buttons.on_press(JOY_DOWN, lambda: self.move_cursor(y=1))
        self.buttons.on_press(BUTTON_A, lambda: self.toggle_flag())

        self.game_over_buttons = Buttons()
        self.game_over_buttons.on_press(JOY_CENTRE, self.reset_game)

    def redraw(self):
        super().redraw()

        self.draw_grid()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.fill_square(x,y)
        
        self.draw_cursor()

        self.clr_text()
        self.set_text("Find 10")
        self.set_text("A BTN: flag", line=1)

    def draw_grid(self):
        display.rect(0, GRIDV_OFF -1, 135, GRIDH +1, WHITE) # outer frame
        for i in range(0,WIDTH+1):
            display.vline(self.x_coord(i), GRIDV_OFF, GRIDH, WHITE)
        for j in range(0,HEIGHT+1):
            display.hline(0, self.y_coord(j), 135, WHITE)
    
    def clr_text(self):
        display.fill_rect(0, 220, 135, 20, WHITE) 
    
    def set_text(self, text, line=0):
        display.text(self.font, text, 1, 221 + 10*line, BLACK, WHITE)

    def move_cursor(self, x=0, y=0):
        old_x = self.cursor.X
        old_y = self.cursor.Y
        self.clear_square(old_x, old_y)
        self.fill_square(old_x, old_y)
        self.cursor.move(x, y)
        self.draw_cursor()
    
    def fill_square(self, x, y):
        state = self.game.get_state(x,y)
        if state[0]:
            if state[2]:
                self.draw_bomb(x,y)
            else:
                self.draw_ok(x,y)
        elif state[1]:
            self.draw_flag(x,y)
    
    def clear_square(self, x, y):
        x = self.x_coord(x)
        y = self.y_coord(y)
        display.fill_rect(x + 1, y + 1, SQ_SIZE -2, SQ_SIZE -2, self.bg)

    def draw_cursor(self):
        x = self.x_coord(self.cursor.X)
        y = self.y_coord(self.cursor.Y)
        display.rect(x + 1, y + 1, SQ_SIZE -2, SQ_SIZE -2, YELLOW)
        display.rect(x + 2, y + 2, SQ_SIZE -4, SQ_SIZE -4, YELLOW)

    def draw_ok(self,x,y):
        x_coord = self.x_coord(x)
        y_coord = self.y_coord(y)

        x_start = max(0, x -1)
        x_end = min(x+2,WIDTH)
        x_range = range(x_start,x_end)

        y_start = max(0, y -1)
        y_end = min(y+2,HEIGHT)
        y_range = range(y_start,y_end)
        
        count = 0
        for check_x in x_range:
            for check_y in y_range:
                if check_x == x and check_y == y:
                    continue
                if self.game.get_is_bomb(check_x, check_y):
                    count += 1

        display.fill_rect(x_coord + 3, y_coord + 3, SQ_SIZE -6, SQ_SIZE -6, GREEN)
        display.text(number_font, "%d"%count, x_coord + FONT_OFFSET, y_coord + FONT_OFFSET, BLACK, GREEN)

    def draw_flag(self,x,y):
        x = self.x_coord(x)
        y = self.y_coord(y)
        display.fill_rect(x + 3, y + 3, SQ_SIZE -6, SQ_SIZE -6, BLUE)

    def draw_bomb(self,x,y):
        x = self.x_coord(x)
        y = self.y_coord(y)
        display.fill_rect(x + 3, y + 3, SQ_SIZE -6, SQ_SIZE -6, RED)

    def x_coord(self, i):
        return SQ_SIZE*i + GRIDH_OFF

    def y_coord(self, j):
        return SQ_SIZE*j + GRIDV_OFF

    def check_square(self):
        x = self.cursor.X
        y = self.cursor.Y

        if self.game.get_flag(x,y):
            return
        
        self.game.set_tried(x,y)

        if self.game.get_is_bomb(x,y):
            self.do_game_over(x,y)
            return

        self.draw_ok(x,y)
        
        if self.game.is_won():
            self.do_game_won()
            return

    def toggle_flag(self):
        x = self.cursor.X
        y = self.cursor.Y
        if not self.game.get_tried(x,y):
            self.game.toggle_flag(x,y)
            self.clear_square(x,y)
            self.fill_square(x,y)
            self.draw_cursor()
    
    def do_game_over(self,x,y):
        self.clr_text()
        self.set_text("BANG!")
        self.set_text("JOY PRESS: reset", line=1)

        for bomb in self.game.bombs:
            self.draw_bomb(*bomb)

        self.buttons.deactivate()
        self.buttons = self.game_over_buttons
        self.buttons.activate()
    
    def do_game_won(self):
        self.clr_text()
        self.set_text("CONGRATULATIONS")
        self.set_text("JOY PRESS: reset", line=1)

        self.buttons.deactivate()
        self.buttons = self.game_over_buttons
        self.buttons.activate()

    def reset_game(self):
        self.game = Game(WIDTH, HEIGHT, COUNT)
        self.cursor.zero()
        self.buttons.deactivate()
        self.buttons = self.main_buttons
        self.buttons.activate()
        self.redraw()


main = Minesweeper
