# from RPi import GPIO

BUTTON_ESCAPE = 17
BUTTON_PREVIOUS = 18
BUTTON_PLAYPAUSE = 22
BUTTON_NEXT = 19

class Buttons(object):
    def __init__(self, button_names):
        self._lookup = {}
        for identifier, channel_number in button_names.items():
            setattr(self, identifier, channel_number)
            self._lookup[channel_number] = identifier
    
    def __getitem__(self, channel_number):
        return self._lookup[channel_number]
    
    def channels(self):
        return self._lookup.keys()
    
    def initialize(self, callback):
        GPIO.setmode(GPIO.BCM)
        for channel in self.channels():
            GPIO.setup(channel, GPIO.IN)
            GPIO.add_event_detect(
                channel,
                GPIO.FALLING, # buttons pulled down, falling == when button released
                callback=callback,
                bouncetime=100
            )

buttons = Buttons({
    'ESCAPE': 17,
    'PREVIOUS': 18,
    'PLAYPAUSE': 22,
    'NEXT': 19,
})