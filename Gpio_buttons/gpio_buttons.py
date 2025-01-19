import logging
import RPi.GPIO as GPIO
import subprocess
import pwnagotchi.plugins as plugins


class GPIOButtons(plugins.Plugin):
    __author__ = 'ratmandu@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'GPIO Button support plugin'

    def __init__(self):
        self.running = False
        self.ports = {}
        self.commands = None
        self.options = dict()

    def runcommand(self, channel):
        command = self.ports[channel]
        logging.info(f"Button Pressed! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None,
                                   executable="/bin/bash")
        process.wait()

    def on_loaded(self):
        logging.info("GPIO Button plugin loaded.")

        # Reset GPIO state to avoid conflicts
        GPIO.cleanup()

        # Get list of GPIOs from options
        gpios = self.options['gpios']

        # Set GPIO numbering
        GPIO.setmode(GPIO.BCM)

        for gpio, command in gpios.items():
            gpio = int(gpio)
            self.ports[gpio] = command
            GPIO.setup(gpio, GPIO.IN, GPIO.PUD_UP)
            GPIO.add_event_detect(gpio, GPIO.FALLING, callback=self.runcommand, bouncetime=600)
            logging.info("Added command: %s to GPIO #%d", command, gpio)

        # If not using Pimoroni Display Hat Mini, remove this section
        # GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

