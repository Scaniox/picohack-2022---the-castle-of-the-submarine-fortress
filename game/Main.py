import pygame as pg
import config as cfg
import Asset_Loader as AL
import Menu_System as MSYS

class Game():
    def __init__(self):
        self.game_state_stack = []

        # init pygame env
        pg.init()
        pg.mixer.init()

        # init config
        self.config = cfg.Config()

        # init video
        self.set_screen()

        # init loaders
        self.img_loader = AL.Img_Loader(self)
        self.snd_loader = AL.Snd_Loader(self)

        # add screen's window name and icon
        pg.display.set_caption("Let's Make A Game provides the title for: The Castle of The Submarine Fortress")
        #pg.display.set_icon(self.img_loader.get("icon"))

        # init screens other than level
        self.main_screen = MSYS.Main(self)
        self.start_screen = MSYS.Start(self)
        self.pause_screen = MSYS.Pause(self)
        self.fail_screen = MSYS.Fail(self)
        self.level_clear_screen = False
        self.end_screen = MSYS.End(self)
        self.level = False

        self.level_no = 1

        # load and play background music
        self.music = self.snd_loader.get("Vexento - Lotus.mp3")
        self.load_snd_vol()
        self.music.play(loops = -1)

        # # push main menu onto game state stack
        self.game_state_stack.append(self.main_screen.tick)
        #self.start_level()

        # call run
        self.run()

        # after running terminates, close
        pg.quit()

    def run(self):
        # main loop
        clock = pg.time.Clock()
        while len(self.game_state_stack) > 0:
            # calculate dt
            if self.config.vsync:
                # delay to achieve correct frame rate
                dt = clock.tick(60)
            else:
                dt = clock.tick()

            # event collect events
            event_list = list(pg.event.get())

            # check events
            for event in event_list:
                # close event: close the game
                if event.type == pg.QUIT:
                    pass#return
                
                # rescale events: change size of the screen
                elif event.type == pg.VIDEORESIZE:
                    if self.config.rescaleable:
                        self.config.resolution = event.size
                        self.rescale()

            self.screen.fill((255,255,255))
            # call correct tick function
            self.game_state_stack[-1](event_list, dt)

            pg.display.flip()

    def start_level(self):

        # initialise new level
        self.level = MSYS.Level(self, self.level_no)
        self.level.setup()

        # push tick function to game state stack
        self.game_state_stack.append(self.level.tick)

    def level_clear(self):
        if self.level_no >= 3:
            # end screen
            self.game_state_stack.append(self.end_screen.tick)
            self.level = 1
        else:
            # next level screen
            self.level_clear_screen = MSYS.Level_clear(self, self.level_no)
            self.level_no += 1
            self.game_state_stack.append(self.level_clear_screen.tick)

    def load_snd_vol(self):
        # change game volume
        self.snd_loader.set_all_vol()
        # change music volume
        self.music.set_volume(self.config.music_vol)

    def set_screen(self):
        """sets the display mode based on parameters in config"""
        # fullscreen
        if self.config.fullscreen:
            desired_res = pg.display.get_desktop_sizes()[0]
            self.screen = pg.display.set_mode(desired_res, flags=pg.FULLSCREEN)            

        # rescale screen
        elif self.config.rescaleable:
            self.screen = pg.display.set_mode(self.config.resolution,
                                              pg.RESIZABLE)
        else:
            self.screen = pg.display.set_mode(self.config.resolution)

    def rescale(self):
        self.set_screen()

        pg.display.set_caption("Colour Between The Lines")
        pg.display.set_icon(self.img_loader.get("icon"))

        # call rescale method of all screens
        self.main_screen.rescale()
        self.start_screen.rescale()
        self.pause_screen.rescale()
        self.fail_screen.rescale()
        if self.end_screen:
            self.end_screen.rescale()
        if self.level:
            self.level.rescale()


Game()