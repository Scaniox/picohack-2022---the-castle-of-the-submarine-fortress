import math
import random as rng
import time
from numpy import size
import pygame as pg

vec2 = pg.math.Vector2

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect)


class Renderable_Sprite(pg.sprite.Sprite):
    def __init__(self, game, start_pos=(0,0), start_rot=0):
        super().__init__()

        # initialise 
        self.game = game
        self.camera = self.game.level.camera
        self.pos = vec2(start_pos)
        self.rot = start_rot
        self.layer = int(self.pos.y)
        self.zoom_scaler = 1

        # animations:
        self.imgs = []
        self.frame_index = 0
        self.frame_time = 100
        self.frame_countdown = 0
        self.culling = True

        
    def update(self, dt):
        pass

    def render(self, dt):
        # decrease frame_countdown 
        self.frame_countdown -= dt
        # advance to next frame if less than 0
        if self.frame_countdown < 0:
            self.frame_countdown = self.frame_time
            self.frame_index = (self.frame_index + 1) % len(self.imgs)

        screen_pos = self.camera.wrld_2_scrn_coord(self.pos)

        # retrieve correct img from imgs
        self.image = self.imgs[self.frame_index]
        
        # rotating and scaling images is expensive; only do it if the sprite
        # is visible on screen; this makes the game faster at higher zooms
        if self.culling == False or \
           screen_pos.x-300 < (ssize := self.game.screen.get_size())[0] and \
           screen_pos.x+300 > 0 and \
           screen_pos.y-300 < ssize[1] and \
           screen_pos.y+300 > 0:
            # rotate and scale image 
            self.image = pg.transform.scale(self.image, [oord*self.camera.zoom*self.zoom_scaler
                                            for oord in self.image.get_size()])
            self.image = pg.transform.rotate(self.image, self.rot)

        # set rect position correctly
        self.rect = self.image.get_rect()
        self.rect.center = screen_pos

        # place hit_rect position correctly
        opp_corner = self.camera.wrld_2_scrn_coord(self.pos + vec2(1,-1))
        self.hit_rect = pg.rect.Rect(0,0,self.rect[2], self.rect[2])
        self.hit_rect.bottomleft = screen_pos

        # circle collisions radius
        self.radius = (min(self.rect.width, self.rect.height) / 2 ) * 0.6



class Player_ship(Renderable_Sprite):
    def __init__(self, game, start_pos):
        # call parent constructor
        super().__init__(game, start_pos, 0)

        # kinematics
        self.vel = vec2(0,0)
        
        # load animation frames

        self.imgs = [self.game.img_loader.get("spaceship1.png")]
        self.zoom_scaler = 0.05
        # sounds

        # set up other mechanics
        # stores the previous key state for edge detection

        # render once to set up rect for collisions
        self.render(0)
        
    def update(self, dt):
        # acceleration due to wasd
        keys = pg.key.get_pressed()


class Cannon(Renderable_Sprite):
    def __init__(self, game, start_pos):
        super().__init__(game, start_pos)

        # load assets
        self.imgs = [game.img_loader.get("Cannon.png")]
        self.imgs[0] = pg.transform.rotate(self.imgs[0], 180)
        self.zoom_scaler = 0.09

        self.prev_mouse_states = [False] * 3
        
        self.render(0)

    def update(self, dt):
        # position on the ship
        self.pos = self.game.level.ship_1.pos + vec2(0.12,0)

        # get direction towards mouse cursor
        mouse_pos = pg.mouse.get_pos()
        vec_to_mouse = vec2(mouse_pos) - vec2(self.rect.center)
        self.rot = vec_to_mouse.angle_to(vec2(0,1))


        # shoot of left click falling edge
        mouse_button_states = pg.mouse.get_pressed()
        if mouse_button_states[0] and not self.prev_mouse_states[0]:
            # create resource:
            reso = Resource(self.game, self.pos)
            reso.vel = vec_to_mouse.normalize() * self.game.config.cannon_speed
            self.game.level.all_sprites.add(reso)
            self.game.level.resources.add(reso)
        self.prev_mouse_states = mouse_button_states
        

    def render(self, dt):
        super().render(dt)



class Other_ship(Renderable_Sprite):
    def __init__(self, game, start_pos):
        # call parent constructor
        super().__init__(game, start_pos, 0)

        # kinematics
        self.vel = vec2(0,0)
        self.target_pos = (0,0)
        self.new_target()
        
        # load animation frames
        self.imgs = [self.game.img_loader.get("spaceship2.png")]
        self.zoom_scaler = 0.05
        # sounds

        # render once to set up rect for collisions
        self.render(0)
        
    def update(self, dt):
        # accelerate towards target_pos
        acc = (self.target_pos - self.pos)
        self.pos += acc * (dt /1000)

        # get new target when close enough to old one
        if acc.length() < 0.01:
            self.new_target()
    
    def new_target(self):
        self.target_pos = rng.random() * 2 + 7, rng.random() * 2 + 2
    
        
        

class Resource(Renderable_Sprite):
    def __init__(self, game, start_pos=(0, 0), start_rot=0):
        super().__init__(game, start_pos, start_rot)

        # choose random rotation
        self.vel = vec2(0,0)
        self.rot_vel = rng.randint(-90, 90)

        # choose random image
        img_names = ["Gold.png", "Coal.png", "Apple.png", "Ice.png" ]
        self.imgs = [game.img_loader.get(img_names[self.game.level.level_no-1])]
        self.zoom_scaler = 0.2

        self.render(0)
    
    def update(self, dt):
        self.pos += self.vel * (dt/1000)
        self.rot += self.rot_vel * (dt/1000)

        # destroy if off screen
        if  not  (0 < self.pos.x < 10 and 0 < self.pos.y < 5): 
            self.kill()

    def render(self, dt):
        super().render(dt)


class Asteroid(Renderable_Sprite):
    def __init__(self, game):
        super().__init__(game, (0,0), 0)

        # load assets with weighting by number
        img_names = ["Evil Asteroid.png"]   * 1 + \
                    ["Girder Deb.png"]      * 1 + \
                    ["Minidebs.png"]        * 2 + \
                    ["Ministorid.png"]      * 3 
        self.possible_imgs = [game.img_loader.get(img_name) for img_name in img_names]
        self.zoom_scaler = 0.2

        self.respawn()
    
    def respawn(self):
        self.pos = (rng.random()* 2 + 4, -1)
        self.vel = vec2(0, rng.random() * 2 + 1)
        self.rot_vel = rng.randrange(-90, 90)
        
        self.imgs = [rng.choice(self.possible_imgs)]
        self.render(0)



    def update(self, dt):
        self.pos += self.vel * (dt/1000)
        self.rot += self.rot_vel * (dt/1000)

        # respawn when off screen:
        if(self.pos[1] > 6):
            self.respawn()


class Camera():
    def __init__(self, game, target = False):
        self.game = game
        self.target = target
        self.pos = vec2(0,0) # this location is the centre of the screen
        self.zoom = 10#self.game.config.camera_zoom

        # invisible default image to support being part of all sprites
        self.img = pg.surface.Surface((1,1))
        self.img.fill((0,0,0))
        self.rect = self.img.get_rect()
        self.rect.topleft = (-1000,-1000)

    
    def update(self, dt):

        # adjust the camera pos
        # target_pos = (5,4)
        # target_pos_delta = -(target_pos - self.pos)
        self.pos = vec2(5,2.5)#self.pos - 0.1*target_pos_delta 

        # ensure camera never goes of screen
        # unscaled_scrn_size = vec2(self.game.config.resolution)/ self.zoom / 16
        # wrld_size = vec2(10,5)

        # left_edge = unscaled_scrn_size.x/2
        # right_edge = wrld_size.x - unscaled_scrn_size.x/2
        # top_edge = unscaled_scrn_size.y/2 - 1.4
        # bottom_edge = wrld_size.y - unscaled_scrn_size.y/2 - 1.3

        # self.pos.x = min(max(left_edge, self.pos.x), right_edge)
        # self.pos.y = min(max(top_edge, self.pos.y), bottom_edge)

    def wrld_2_scrn_coord(self, wrld_coord):
        """takes a world space coordinate and converts it to screenspace"""
        scrn_size = vec2(self.game.config.resolution)

        # ensures that the cameras position ends up at the centre of the screen
        scaled_wrld_coord = vec2(wrld_coord) * self.zoom * 16
        scaled_pos = self.pos * self.zoom * 16
        ss_coord = scaled_wrld_coord + scrn_size/2 - scaled_pos
        return ss_coord


class Timer():
    def __init__(self, game):
        self.game = game
        self.reset()

        # invisible default image to support being part of all sprites
        self.img = pg.surface.Surface((1,1))
        self.img.fill((0,0,0))
        self.rect = self.img.get_rect()
        self.rect.topleft = (-1000,-1000)

    def update(self, dt):
        # dt is in ms, but total time is in s so dt is scalled correctly
        self.total_time += dt/1000

    def reset(self):
        self.total_time = 0.0
        self.start_time = time.time()