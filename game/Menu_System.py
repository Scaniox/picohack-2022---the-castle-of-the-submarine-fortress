from turtle import screensize
import pygame as pg
import Menu_Sprites as MS
import Sprites as sprites
import Maze_Gen as mg
import random as rng

vec2 = pg.math.Vector2
default_rect = lambda : pg.rect.Rect(0,0,1,1)

class Ui_Screen():
    def __init__(self, game):
        self.game = game

        self.elements = pg.sprite.Group()
        self.background = False

        self.screen = self.game.screen

    def tick(self, event_list, dt):
        self.elements.update(dt, event_list)
        if self.background:
            self.game.screen.blit(self.bg_img, self.bg_rect)
        self.elements.draw(self.game.screen)

    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        # rescale the background if it is present
        if self.background:
            # choose scale factor to fill screen
            match_width_SF = screen_rect.width / self.background.get_width()
            match_height_SF = screen_rect.height / self.background.get_height()
            scale_factor = max(match_height_SF, match_width_SF)
            
            # rescale image
            background_size = vec2(self.background.get_size()) * scale_factor
            self.bg_img = pg.transform.scale(self.background, background_size)
            
            # position image
            self.bg_rect = self.bg_img.get_rect()
            self.bg_rect.center = screen_rect.center

        # rescale all elements
        for elements in self.elements:
            elements.rescale()

class Main(Ui_Screen):
    def __init__(self, game):
        super().__init__(game)

        # init elements
        self.title_text = MS.Text(game, default_rect(),
                                  "The Castle of The Submarine Fortress")
        self.elements.add(self.title_text)
        self.start_b = MS.Button(game, default_rect(), "Start")
        self.elements.add(self.start_b)
        self.close_b = MS.Button(game, default_rect(), "Close")
        self.elements.add(self.close_b)
        # load background image
        self.background = game.img_loader.get("main background")

        # call rescale to render image
        self.rescale()

    def tick(self, event_list, dt):
        # call parent tick function
        super().tick(event_list, dt)
        # push tick functions onto GSS for button presses

        # start
        if self.start_b.falling_edges[0]:
            self.game.game_state_stack.append(self.game.start_screen.tick)

        # close
        elif self.close_b.falling_edges[0]:
            self.game.game_state_stack = []
    
    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        # positon title text
        self.title_text.rect.width = screen_size.x 
        self.title_text.rect.height = screen_size.y / 10
        self.title_text.rect.centerx = screen_rect.centerx
        self.title_text.rect.centery = screen_size.y / 8

        # position buttons
        button_width = screen_size.x / 3
        button_height = screen_size.y / 14
        button_spacing = screen_size.y / 12
        button_pos_y = screen_size.y * 2 / 6

        # start button
        self.start_b.rect.width = button_width
        self.start_b.rect.height = button_height
        self.start_b.rect.centerx = screen_rect.centerx
        self.start_b.rect.centery = button_pos_y
        button_pos_y += button_spacing

        # close button
        self.close_b.rect.width = button_width
        self.close_b.rect.height = button_height
        self.close_b.rect.centerx = screen_rect.centerx
        self.close_b.rect.centery = button_pos_y
        button_pos_y += button_spacing

        # call parent rescale method
        super().rescale()

class Start(Ui_Screen):
    def __init__(self, game):
        super().__init__(game)

        # init elements
        self.intro_text = MS.Text(game, default_rect(),
                                  game.config.level_win_texts[0])
        self.elements.add(self.intro_text)
        self.start_b = MS.Button(game, default_rect(), "Start")
        self.elements.add(self.start_b)

        # load background image
        self.background = game.img_loader.get("main background")

        self.rescale()

    def tick(self, event_list, dt):
        super().tick(event_list, dt)
        
        if self.start_b.falling_edges[0]:
            self.game.start_level()

    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        self.intro_text.rect.width = screen_size.x
        self.intro_text.rect.height = screen_size.y * 0.8
        self.intro_text.rect.centerx = screen_size.x * 0.5
        self.intro_text.rect.y = screen_size.y * 0.05

        self.start_b.rect.width = screen_size.x * 0.6
        self.start_b.rect.height = screen_size.y * 0.05
        self.start_b.rect.centerx = screen_size.x * 0.5
        self.start_b.rect.bottom = screen_size.y * 0.95

        super().rescale()

class Level_clear(Ui_Screen):
    def __init__(self, game, level_no):
        super().__init__(game)

        # init elements
        self.intro_text = MS.Text(game, default_rect(),
                                  game.config.level_win_texts[level_no])
        self.elements.add(self.intro_text)
        self.start_b = MS.Button(game, default_rect(), "Next Level")
        self.elements.add(self.start_b)

        # load background image
        self.background = game.img_loader.get("main background")

        self.rescale()

    def tick(self, event_list, dt):
        super().tick(event_list, dt)
        
        if self.start_b.falling_edges[0]:
            self.game.start_level()

    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        self.intro_text.rect.width = screen_size.x
        self.intro_text.rect.height = screen_size.y * 0.8
        self.intro_text.rect.centerx = screen_size.x * 0.5
        self.intro_text.rect.y = screen_size.y * 0.05

        self.start_b.rect.width = screen_size.x * 0.6
        self.start_b.rect.height = screen_size.y * 0.05
        self.start_b.rect.centerx = screen_size.x * 0.5
        self.start_b.rect.bottom = screen_size.y * 0.95

        super().rescale()

class Fail(Ui_Screen):
    def __init__(self, game):
        super().__init__(game)

        # init elements
        self.intro_text = MS.Text(game, default_rect(),
                                  game.config.level_fail_text)
        self.elements.add(self.intro_text)
        self.start_b = MS.Button(game, default_rect(), "Main menu")
        self.elements.add(self.start_b)

        # load background image
        self.background = game.img_loader.get("main background")

        self.rescale()

    def tick(self, event_list, dt):
        super().tick(event_list, dt)
        
        if self.start_b.falling_edges[0]:
            self.game.game_state_stack = [self.game.main_screen.tick]

    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        self.intro_text.rect.width = screen_size.x
        self.intro_text.rect.height = screen_size.y * 0.8
        self.intro_text.rect.centerx = screen_size.x * 0.5
        self.intro_text.rect.y = screen_size.y * 0.05

        self.start_b.rect.width = screen_size.x * 0.6
        self.start_b.rect.height = screen_size.y * 0.05
        self.start_b.rect.centerx = screen_size.x * 0.5
        self.start_b.rect.bottom = screen_size.y * 0.95

        super().rescale()

class End(Ui_Screen):
    def __init__(self, game):
        super().__init__(game)

        # init elements
        self.intro_text = MS.Text(game, default_rect(),
                                  game.config.level_win_texts[3])
        self.elements.add(self.intro_text)
        self.start_b = MS.Button(game, default_rect(), "Main menu")
        self.elements.add(self.start_b)

        # load background image
        self.background = game.img_loader.get("main background")

        self.rescale()

    def tick(self, event_list, dt):
        super().tick(event_list, dt)
        
        if self.start_b.falling_edges[0]:
            self.game.game_state_stack = [self.game.main_screen.tick]

    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        self.intro_text.rect.width = screen_size.x
        self.intro_text.rect.height = screen_size.y * 0.8
        self.intro_text.rect.centerx = screen_size.x * 0.5
        self.intro_text.rect.y = screen_size.y * 0.05

        self.start_b.rect.width = screen_size.x * 0.6
        self.start_b.rect.height = screen_size.y * 0.05
        self.start_b.rect.centerx = screen_size.x * 0.5
        self.start_b.rect.bottom = screen_size.y * 0.95

        super().rescale()

class Pause(Ui_Screen):
    def __init__(self, game):
        super().__init__(game)

        # init elements
        self.pause_text = MS.Text(game, default_rect(), "Pause")
        self.elements.add(self.pause_text)
        self.resume_b = MS.Button(game, default_rect(), "Resume")
        self.elements.add(self.resume_b)
        self.exit_b = MS.Button(game, default_rect(), "Main Menu")
        self.elements.add(self.exit_b)

        # load background
        self.background = game.img_loader.get("menu background")

        # call rescale to render image
        self.rescale()

    def tick(self, events, dt):
        # call parent tick method
        super().tick(events, dt)

        # resume button
        if self.resume_b.falling_edges[0]:
            self.game.game_state_stack.pop(-1)
        # ESC key
        for event in events:
            if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
                self.game.game_state_stack.pop(-1)
                break

        # exit button
        if self.exit_b.falling_edges[0]:
            self.game.game_state_stack = [self.game.main_screen.tick]
    
    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        # positon title text
        self.pause_text.rect.width = screen_size.x
        self.pause_text.rect.height = screen_size.y / 10
        self.pause_text.rect.centerx = screen_rect.centerx
        self.pause_text.rect.centery = screen_size.y / 8

        # position buttons
        button_width = screen_size.x / 3
        button_height = screen_size.y / 14
        button_spacing = screen_size.y / 12
        button_pos_y = screen_size.y / 4

        # resume button
        self.resume_b.rect.width = button_width
        self.resume_b.rect.height = button_height
        self.resume_b.rect.centerx = screen_rect.centerx
        self.resume_b.rect.centery = button_pos_y
        button_pos_y += button_spacing

        # exit button
        self.exit_b.rect.width = button_width
        self.exit_b.rect.height = button_height
        self.exit_b.rect.centerx = screen_rect.centerx
        self.exit_b.rect.centery = button_pos_y
        button_pos_y += button_spacing

        # call parent rescale method
        super().rescale()

class Level(Ui_Screen):
    def __init__(self, game, level_no):
        super().__init__(game)

        
        # init UI elements
        self.level_text = MS.Text(game, default_rect(), f"LEVEL : {level_no}")
        self.elements.add(self.level_text)
        self.hits_text = MS.Text(game, default_rect(), f"resources delivered: 0")
        self.elements.add(self.hits_text)
        self.time_text = MS.Text(game, default_rect(), f"time left: 0")
        self.elements.add(self.time_text)

        self.timer = sprites.Timer(self.game)
        self.level_no = level_no
        self.hits = 0
        self.time_left = 30
        self.win_snd = game.snd_loader.get("winfretless.ogg")
    
    def setup(self):
        """sets up the level"""
        # initialise camera
        self.camera = sprites.Camera(self.game)

        # initialise sprite groups
        self.all_sprites = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.resources = pg.sprite.Group()

        # initalise player spaceship
        self.ship_1 = sprites.Player_ship(self.game, (2, 2.5))
        self.all_sprites.add(self.ship_1)
        # and player cannon
        self.cannon = sprites.Cannon(self.game, (0,0))
        self.all_sprites.add(self.cannon)

        # initialise other spaceship
        self.ship_2 = sprites.Other_ship(self.game, (8, 2.5))
        self.all_sprites.add(self.ship_2)
        # initialise asteroids
        for _ in range(self.game.config.asteroid_counts[self.level_no-1]):
            ast = sprites.Asteroid(self.game)
            self.asteroids.add(ast)
            self.all_sprites.add(ast)

        self.rescale()

    def tick(self, events, dt):
        self.time_left -= dt/1000
        self.time_text.text = f"time left: {round(self.time_left)}s"
        self.time_text.rescale()

        for event in events:
            if event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    self.game.game_state_stack.append(
                        self.game.pause_screen.tick)

            # zoom debug
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.camera.zoom = min(self.camera.zoom+1, 20)
                if event.button == 5:
                    self.camera.zoom = max(self.camera.zoom-1 , 1)
                self.rescale()

        # update all sprites
        self.all_sprites.update(dt)
        self.camera.update(dt)
        self.timer.update(dt)

        # end game if they run out of time
        if self.time_left <=0:
            self.game.game_state_stack.append(self.game.fail_screen.tick)

        # collide resources with asteroids:
        for ast in self.asteroids:
            pg.sprite.spritecollide(ast, self.resources, True, pg.sprite.collide_circle)
        
        # collide ship with resources
        for hit in pg.sprite.spritecollide(self.ship_2, self.resources, True):
            self.hits += 1
            # update hits text
            self.hits_text.text = f"resources delivered: {self.hits}"
            self.hits_text.rescale()

            if self.hits >= self.game.config.level_hit_requirements[self.level_no-1]:
                # move onto next level
                # remove old level from stack
                self.game.game_state_stack.pop(-1)
                self.game.game_state_stack.pop(-1)

                # open level cleared dialogue
                self.game.level_clear()

        # call all sprites render method
        for sprite in self.all_sprites:
            sprite.render(dt)


        self.game.screen.fill((32,32,32))
        self.all_sprites.draw(self.game.screen)
        super().tick(events, dt)

        if False: # debug col rects
            for sprite in self.all_sprites:
                pg.draw.rect(self.game.screen, (0,0,255), sprite.rect, 1)
                pg.draw.circle(self.game.screen, (0,255,0), sprite.rect.center, sprite.radius, 1)

    def rescale(self):
        screen_rect = pg.rect.Rect(0, 0, *self.screen.get_size())
        screen_size = vec2(screen_rect.size)

        # level number:
        self.level_text.rect.width = screen_size.x * 0.15
        self.level_text.rect.height = screen_size.y * 0.05
        self.level_text.rect.left = 0
        self.level_text.rect.bottom = screen_size.y

        # hit number:
        self.hits_text.rect.width = screen_size.x * 0.3
        self.hits_text.rect.height = screen_size.y * 0.05
        self.hits_text.rect.right = screen_size.x 
        self.hits_text.rect.bottom = screen_size.y

        # time left:
        self.time_text.rect.width = screen_size.x * 0.3
        self.time_text.rect.height = screen_size.y * 0.05
        self.time_text.rect.right = screen_size.x 
        self.time_text.rect.top = 0

        # rescale background
        floor = self.game.img_loader.get("Background.png")
        floor_size = self.camera.wrld_2_scrn_coord((5,5)) - \
                     self.camera.wrld_2_scrn_coord((0,0))
        self.floor = pg.transform.scale(floor, floor_size)
        self.floor_rect = self.floor.get_rect()


        super().rescale()

