from kivy.config import Config
Config.set('graphics','width','900')
Config.set('graphics','height','400')

import random
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import NumericProperty, ObjectProperty
from kivy.properties import Clock
from kivy.core.window import Window
from kivy import platform

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transfrorm_prespective
    from user_inputs import keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up
    menu_widget = ObjectProperty()
    prespective_point_x = NumericProperty(0)
    prespective_point_y = NumericProperty(0)
    
    V_NUM_LINES = 8
    V_LINES_SPACING = .6
    vertical_lines=[]

    H_NUM_LINES = 15
    H_LINES_SPACING = .2
    horizontal_lines=[]

    speed = 0.6
    current_offset_value= 0
    current_y_loop = 0

    speed_x = 1.6
    current_speed_x = 0
    current_offset_x = 0

    NUM_TILES = 12
    tiles = []
    tiles_coordinate = []

    ship_width = .1
    ship_height = 0.035
    ship_base_y = 0.04
    ship = None
    ship_coordinates = [(0, 0) ,(0, 0) ,(0, 0)]

    state_game_over = False
    state_game_has_started = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinate()

        if self.is_desktop():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down = self.on_keyboard_down)
            self.keyboard.bind(on_key_up = self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1/60)
 
    def init_ship(self):
        with self.canvas:
            Color(0,0,0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width/2
        base_y = self.ship_base_y * self.height
        ship_width = self.ship_width * self.width/2
        ship_height= self.ship_height * self.height

        self.ship_coordinates[0] = (center_x - ship_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range (0, len(self.tiles_coordinate)):
            ti_x, ti_y = self.tiles_coordinate[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range (0,3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(1,1,1)
            for i in range (0, self.NUM_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(10):
            self.tiles_coordinate.append((0,i))

    def generate_tiles_coordinate(self):
        last_y = 0
        last_x = 0
        for i in range (len(self.tiles_coordinate)-1, -1, -1):
            if self.tiles_coordinate[i][1]<self.current_y_loop:
                del self.tiles_coordinate[i]

        if len(self.tiles_coordinate)>0:
            last_coordinate = self.tiles_coordinate[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1

        for i in range (len(self.tiles_coordinate), self.NUM_TILES):
            r = random.randint(0, 2)
            start_index = -int(self.V_NUM_LINES/2) + 1
            end_index = start_index + self.V_NUM_LINES - 2
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2
            self.tiles_coordinate.append((last_x, last_y))
            if (r == 1):
                last_x += 1
                self.tiles_coordinate.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinate.append((last_x, last_y))
            if (r == 2):
                last_x -= 1
                self.tiles_coordinate.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinate.append((last_x, last_y))
            last_y += 1

    def init_vertical_lines(self):
        with self.canvas:
            Color(1,1,1)
            for i in range (0, self.V_NUM_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):    
        center_x = self.prespective_point_x
        spacing = self.V_LINES_SPACING*self.width
        offset =  index - 0.5
        line_x = center_x + offset * spacing + self.current_offset_x
        return line_x
    
    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING*self.height
        line_y = int(index*spacing_y - self.current_offset_value)
        return line_y
    
    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x,y
    
    def update_tiles(self):
        for i in range (0, self.NUM_TILES):
            tile = self.tiles[i]    
            tile_coordinates = self.tiles_coordinate[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)

            x1,y1 = self.transform(xmin, ymin)
            x2,y2 = self.transform(xmin, ymax)
            x3,y3 = self.transform(xmax, ymax)    
            x4,y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NUM_LINES/2)+1
        for i in range (start_index, start_index + self.V_NUM_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x,0)
            x2, y2 = self.transform(line_x,self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1,1,1)
            for i in range (0, self.H_NUM_LINES):
                self.horizontal_lines.append(Line())
        
    def update_horizontal_lines(self):
        start_index = -int(self.V_NUM_LINES/2) + 1
        end_index = start_index + self.V_NUM_LINES - 1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)

        for i in range (0, self.H_NUM_LINES):
            line_y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(xmin,line_y)
            x2, y2 = self.transform(xmax,line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2] 

    
    def is_desktop(self):
        if platform in ('linux','win','macosx'):
            return True
        return False
    
    def update(self,dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.speed *self.height / 100
            self.current_offset_value += speed_y * time_factor
        
            spacing_y = self.H_LINES_SPACING*self.height
            while self.current_offset_value >= spacing_y:
                self.current_offset_value -= spacing_y
                self.current_y_loop += 1
                self.generate_tiles_coordinate()

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_widget.opacity = 1
            print('Game Over')

    def on_menu_button_pressed(self):
        print("start")
        self.state_game_has_started = True
        self.menu_widget.opacity = 0

class GameApp(App):
    pass

GameApp().run()