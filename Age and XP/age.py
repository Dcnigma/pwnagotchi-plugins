import logging
import os
import random
import json
from datetime import datetime

import pwnagotchi
import pwnagotchi.agent
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi import utils

# Static Variables
MULTIPLIER_ASSOCIATION = 1
MULTIPLIER_DEAUTH = 2
MULTIPLIER_HANDSHAKE = 3
MULTIPLIER_AI_BEST_REWARD = 5
TAG = "[EXP & AGE Plugin]"
FACE_LEVELUP = '(≧◡◡≦)'  # Default face
BAR_ERROR = "|   error  |"
FILE_SAVE_EXP = "exp_stats.json"
FILE_SAVE_AGE = "age_stats.json"
JSON_KEY_LEVEL = "level"
JSON_KEY_EXP = "exp"
JSON_KEY_EXP_TOT = "exp_tot"
JSON_KEY_STRENGTH = "strength"
JSON_KEY_AGE_DAYS = "age_days"


class ExpAndAgePlugin(plugins.Plugin):
    __author__ = 'DcNigma'
    __version__ = '1.0'
    __license__ = 'GPL3'
    __description__ = 'Tracks EXP and Age for your pwnagotchi.'

    def __init__(self):
#        self.face_levelup = "(≧◡◡≦)"  # Default face for fallback
        self.percent = 0
        self.strength = 1
        self.calculateInitialXP = False
        self.exp = 0
        self.lv = 1
        self.exp_tot = 0
        self.expneeded = 0
        self.face_levelup = FACE_LEVELUP

        # Age Initialization
        self.age_days = 0
        self.birth_date = None

        # Load EXP Data
        if os.path.exists(FILE_SAVE_EXP):
            try:
                self.load_exp_data(FILE_SAVE_EXP)
            except:
                logging.error(TAG + " Failed to load EXP data. 
Recalculating.")
                self.calculateInitialXP = True
        else:
            self.save_exp_data(FILE_SAVE_EXP)

        # Load Age Data
        if os.path.exists(FILE_SAVE_AGE):
            try:
                self.load_age_data(FILE_SAVE_AGE)
            except:
                logging.error(TAG + " Failed to load AGE data. Resetting 
age.")
                self.reset_age()
        else:
            self.reset_age()

        # EXP Setup
        if self.lv == 1 and self.exp == 0:
            self.calculateInitialXP = True
        if self.exp_tot == 0:
            logging.info(TAG + " Calculating Total EXP")
            self.exp_tot = self.calc_actual_sum(self.lv, self.exp)
            self.save_exp_data(FILE_SAVE_EXP)
        self.expneeded = self.calc_exp_needed(self.lv)

    # Age Helper Functions
    def reset_age(self):
        """Resets the age data."""
        self.birth_date = self.get_current_date()
        self.age_days = 0
        self.save_age_data(FILE_SAVE_AGE)

    def update_age(self):
        """Updates the age based on the current date."""
        current_date = self.get_current_date()
        if self.birth_date:
            age_difference = (current_date - self.birth_date).days
            self.age_days = max(0, age_difference)
            self.save_age_data(FILE_SAVE_AGE)

    def get_current_date(self):
        """Returns the current date as a datetime object."""
        return datetime.now()

    # EXP Calculation Functions
    def calc_exp_needed(self, level):
        """Calculates the EXP needed to reach the next level."""
        if level == 1:
            return 5
        return int((level ** 3) / 2)

    def calc_actual_sum(self, level, exp):
        """Calculates the total EXP from level and EXP."""
        total = exp
        for lvl in range(1, level):
            total += self.calc_exp_needed(lvl)
        return total

    def calc_strength(self):
        """Calculates strength based on EXP and level."""
        self.strength = self.exp * self.lv * 0.05

    def calculate_initial_exp(self, agent):
        """Calculates initial EXP based on saved access points and 
handshakes."""
        initial_exp = 0
        try:
            unique_aps = agent.aps.get_unique()
            unique_handshakes = len(agent.aps.handshakes())
            initial_exp += unique_aps * MULTIPLIER_ASSOCIATION
            initial_exp += unique_handshakes * MULTIPLIER_HANDSHAKE
        except Exception as e:
            logging.error(TAG + f" Error calculating initial EXP: {e}")
        return initial_exp

    def exp_check(self, agent):
        """Checks if the pwnagotchi has leveled up."""
        if self.exp >= self.expneeded:
            self.exp = 1
            self.lv += 1
            self.expneeded = self.calc_exp_needed(self.lv)
            self.display_level_up(agent)

    def display_level_up(self, agent):
        """Displays the level-up message on the screen."""
        view = agent.view()
        # Ensure the face is loaded correctly
        try:
            view.set('face', self.face_levelup)
        except Exception as e:
            logging.error(TAG + f" Error displaying level-up face: {e}")
            view.set('face', FACE_LEVELUP)  # Fallback to default face if 
there's an error
     
        view.set('status', "Level Up!")
        view.update(force=True)

    # Event Handling
    def on_association(self, agent, access_point):
        self.exp += MULTIPLIER_ASSOCIATION
        self.exp_tot += MULTIPLIER_ASSOCIATION
        self.exp_check(agent)
        self.save_exp_data(FILE_SAVE_EXP)

    def on_deauthentication(self, agent, access_point, client_station):
        self.exp += MULTIPLIER_DEAUTH
        self.exp_tot += MULTIPLIER_DEAUTH
        self.exp_check(agent)
        self.save_exp_data(FILE_SAVE_EXP)

    def on_handshake(self, agent, filename, access_point, client_station):
        self.exp += MULTIPLIER_HANDSHAKE
        self.exp_tot += MULTIPLIER_HANDSHAKE
        self.exp_check(agent)
        self.save_exp_data(FILE_SAVE_EXP)

    def on_ready(self, agent):
        if self.calculateInitialXP:
            logging.info(TAG + " Calculating initial EXP.")
            sum_exp = self.calculate_initial_exp(agent)
            self.exp_tot = sum_exp
            self.lv = 1
            while sum_exp > self.calc_exp_needed(self.lv):
                sum_exp -= self.calc_exp_needed(self.lv)
                self.lv += 1
            self.exp = sum_exp
            self.save_exp_data(FILE_SAVE_EXP)

        self.update_age()

    # Save and Load Functions
    def save_exp_data(self, file_path):
        """Saves EXP data to a file."""
        data = {
            JSON_KEY_LEVEL: self.lv,
            JSON_KEY_EXP: self.exp,
            JSON_KEY_EXP_TOT: self.exp_tot,
            JSON_KEY_STRENGTH: self.strength
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_exp_data(self, file_path):
        """Loads EXP data from a file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.lv = data[JSON_KEY_LEVEL]
            self.exp = data[JSON_KEY_EXP]
            self.exp_tot = data[JSON_KEY_EXP_TOT]
            self.strength = data[JSON_KEY_STRENGTH]

    def save_age_data(self, file_path):
        """Saves AGE data to a file."""
        data = {
            JSON_KEY_AGE_DAYS: self.age_days,
            "birth_date": self.birth_date.strftime("%Y-%m-%d") if 
self.birth_date else None
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_age_data(self, file_path):
        """Loads AGE data from a file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.age_days = data[JSON_KEY_AGE_DAYS]
            self.birth_date = datetime.strptime(data["birth_date"], 
"%Y-%m-%d") if data["birth_date"] else None

    # UI Integration
    def on_ui_setup(self, ui):
        # Access the configuration after plugin setup
        self.face_levelup = self.options["levelup"] if "levelup" in 
self.options else FACE_LEVELUP

        ui.add_element('Lv', LabeledValue(color=BLACK, label='Lv', 
value="0",
                                          
position=(int(self.options["lvl_x_coord"]),
                                                    
int(self.options["lvl_y_coord"])),
                                          label_font=fonts.Bold, 
text_font=fonts.Medium))
        ui.add_element('Exp', LabeledValue(color=BLACK, label='Exp', 
value="0",
                                           
position=(int(self.options["exp_x_coord"]),
                                                     
int(self.options["exp_y_coord"])),
                                           label_font=fonts.Bold, 
text_font=fonts.Medium))
        ui.add_element('Age', LabeledValue(color=BLACK, label='Age', 
value="0",
                                           
position=(int(self.options["age_x_coord"]),
                                                     
int(self.options["age_y_coord"])),
                                           label_font=fonts.Bold, 
text_font=fonts.Medium))
    def on_unload(self, ui):
            ui.remove_element('Lv')
            ui.remove_element('Exp')
            ui.remove_element('Age')

    def on_ui_update(self, ui):
        self.expneeded = self.calc_exp_needed(self.lv)
        self.percent = int((self.exp / self.expneeded) * 100)
        bar = self.bar_string(int(self.options["bar_symbols_count"]), 
self.percent)
        self.calc_strength()

        ui.set('Lv', "%d" % self.lv)
        ui.set('Exp', "%s" % bar)
        ui.set('Age', "%d days" % self.age_days)

    def bar_string(self, symbols_count, percentage):
        if percentage > 100:
            return BAR_ERROR
        bar_char = '▥'
        blank_char = ' '
        bar_length = int(round((symbols_count / 100) * percentage))
        return '|' + (bar_char * bar_length) + (blank_char * 
(symbols_count - bar_length)) + '|'
