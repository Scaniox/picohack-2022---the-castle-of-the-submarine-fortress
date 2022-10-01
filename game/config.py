import re
from pathlib import Path
import sys


class Config():
    def __init__(self):

        # get file paths
        if getattr(sys, 'frozen', False):
            # is running in exe
            if hasattr(sys, '_MEIPASS'):
                app_path = Path(sys._MEIPASS)
                exe_parent_path = Path(sys.executable).parent
            else:
                print("can't find local path")
                input()
        else:
            # is running in python interpreter
            app_path = Path(__file__).parent
            exe_parent_path = app_path

            
        print(f"local path: {app_path}, exe parent path: {exe_parent_path}")

        # file paths: they are in reference to the game root foolder
        self.img_pathX = (app_path / 'img').as_posix()
        self.snd_pathX = (app_path / 'snd').as_posix()
        self.scoreboard_pathX = (exe_parent_path / 'scoreboard.csv').as_posix()
        self.settings_save_pathX = (exe_parent_path / 'settings.set')

        # graphics config
        self.resolution = [1366, 768]
        self.rescaleable = False
        self.fullscreen = False
        self.vsync = True
        self.camera_zoom = 2

        # sound
        self.game_vol = 1
        self.music_vol = 0.25
        self.player_step_snd_delay = 300

        # fonts
        self.text_colour = (0xb3,0x7d,0x2e)

        # asteroids
        self.asteroid_counts = [8, 10, 14, 16]
        self.asteroid_speed_range = (1,3)

        # cannon speed
        self.cannon_speed = 5

        # win conditions
        self.level_hit_requirements = [5, 7, 9, 11]
        self.level_win_texts = [
"""In a galaxy far, far away,
There was a tiny town on a tiny spaceship,
The tiny town had tiny people who had a lot gold
 
The tiny people were travelling through space to find metal,
They needed metal to repair their ship, for without the metal, they would surely die
 
They searched,
And they searched,
And searched,
 
Until one day, they finally found a spaceship
The spaceship also had a tiny town with tiny people
The tiny people had a lot of coal, but no gold
 
So an agreement was reached between the two tiny towns
They would exchange what they needed for what they had so they could both be on their way to find more tiny towns
 
Instructions- throw the gold your town has to the other towns spaceship to receive coal 
""",



"""Congratulations! You have received coal and saved the tiny town!

Now that the tiny people had repaired the ship, they were tired and hungry
But they had no food to fill their empty stomachs
 
So they searched,
And they searched,
And searched some more,
 
Until one day they finally found yet another spaceship
This spaceship also had a tiny town with tiny people
These tiny people had a lot of non-disclosed food items, but no coal for their furnaces
 
So an agreement was reached between the two tiny towns
They would exchange what they needed for what they had so they could both be on their way to find more tiny towns
 
 
Instructions- throw the remainder of your coal to obtain 
a non-disclosed food item to prevent your town from starvation
""",




"""Congratulations! You had received a non-disclosed food item and avoided a famine!

After eating all the non-disclosed food items, the tiny people of the tiny town were feeling thirsty,
But the tiny people did not have any water,
 
So they searched,
And they searched,
And searched some more,
 
Until one day they finally found yet another spaceship
This spaceship also had a tiny town with tiny people
These tiny people had a lot ice, but  no food to fill their empty stomachs,
 
So an agreement was reached between the two tiny towns
They would exchange what they needed for what they had so they could both be on their way to find more tiny towns
 
 
Instructions- throw the remainder of your  non-disclosed food items 
to obtain ice to save the tiny people of your town from dehydration and death
""",


"""you now have ice, and the peeps are hydrated, they lived happily ever after
















""",]

        self.level_fail_text = """Oh no! All the people in your tiny town have died as a result of your negligence.
 Do better next time!!
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 """




        self.load()

    def save(self):
        """saves settings"""
        save_file_str = ""
        for identifier, val in self.__dict__.items():
            if identifier[-1] != "X":
                save_file_str += f"{identifier}|{repr(val)}\n"

        save_file = open(self.settings_save_pathX, "w")
        save_file.write(save_file_str)
        save_file.close()

    def load(self):
        """loads settings"""
        try:
            save_file = open(self.settings_save_pathX, "r")
        except:
            return

        for line in save_file.readlines():
            if "|" in line:
                id, val = line.strip().split("|")
                exec(f"self.{id} = {val}")

        save_file.close()