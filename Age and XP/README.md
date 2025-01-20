# Pwnagotchi EXP & Age Plugin

This plugin tracks the EXP (experience points) and age of your Pwnagotchi. It calculates experience points based on associations, deauths, and handshakes and increments your Pwnagotchi's age based on the number of days passed since it was started.

## Features

- **EXP Tracking**: Tracks the EXP earned through associations, deauths, and handshakes.
- **Age Tracking**: Tracks the age of the Pwnagotchi in days, starting from when it was first initialized.
- **Leveling System**: Pwnagotchi levels up based on EXP, with each level requiring more EXP to reach.
- **Strength Calculation**: Calculates the "strength" of the Pwnagotchi based on its level and experience.
- **UI Integration**: Displays the Pwnagotchi's level, EXP progress, and age on the screen.
  
## Installation

1. Clone this repository to your Pwnagotchi plugins directory.
```bash
   git clone https://github.com/Dcnigma/pwnagotchi-exp-age-plugin.git
```
## Ensure your config.toml file includes the plugin:

/etc/pwnagotchi/config.toml

main.plugins.age2.enabled = true
main.plugins.age2.age_x_coord = 10
main.plugins.age2.age_y_coord = 100
main.plugins.age2.int_x_coord = 67
main.plugins.age2.int_y_coord = 100
main.plugins.age2.lvl_x_coord = 10
main.plugins.age2.lvl_y_coord = 110
main.plugins.age2.exp_x_coord = 38
main.plugins.age2.exp_y_coord = 110
main.plugins.age2.bar_symbols_count = 12
main.plugins.age2.levelup = "/custom-faces/LEVELUP.png"
# or use this for the default faces: 
main.plugins.age2.levelup = "(≧◡◡≦)"  # Default face

## Configuration

- **EXP Calculation:** The EXP is calculated based on the number of associations, deauths, and handshakes:

- **ASSOCIATION:** +1 EXP per association.
- **DEAUTHENTICATION:** +2 EXP per deauthentication.
- **HANDSHAKE:** +3 EXP per handshake.
- **Level System:** Each level requires a progressively higher amount of EXP. The required EXP for each level is calculated using the formula (level^3) / 2.

- **Age Calculation:** The age is calculated as the number of days since the plugin was first initialized. Each new day will add 1 day to the age.

## Usage
After installing the plugin, the following information will be displayed on your Pwnagotchi screen:

- **Lv:** The current level of your Pwnagotchi.
- **Exp:** A progress bar showing the current EXP progress toward the next level.
- **Age:** The age of your Pwnagotchi in days.

## Events
- **on_association:** Triggers when a new association is made, adding EXP.
- **on_deauthentication:** Triggers when a deauthentication occurs, adding EXP.
- **on_handshake:** Triggers when a handshake is captured, adding EXP.
- **on_ready:** Runs when the Pwnagotchi is ready and ensures the initial EXP calculation is performed.

## Logging
The plugin logs important events such as loading errors and updates to the age and EXP. You can view the logs using the following command:
```bash
tail -f /etc/pwnagotchi/log/pwnagotchi.log
```
## Known Issues
- The age calculation may have issues with time zone changes.
- Ensure the system clock is accurate, as the age is determined by the current date.

## Acknowledgments
Pwnagotchi: The Pwnagotchi project is the core of this plugin.
Base on the plugins of hannadiamond
The XP plugin broke on the Pwnagotchi version made by jayofelony
because there is no brain.json anymore jayofelony removed the AI.
