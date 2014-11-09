import time
import errno
import Queue
import multiprocessing
import subprocess
from pprint import pprint

from audcast.config import settings
import logging
log = logging.getLogger(__name__)

from audcast.buttons import buttons
from audcast.database import Session
from audcast.models import Episode


## Messages

def nl2spc(msg):
    return msg.replace('\n', ' ')

MESSAGE_RESUME = nl2spc("""Last time, you were listening to {title} from
{podcast}. To resume, press the play button. To pick something else, press any
other button.
""")

MESSAGE_LISTINTRO = nl2spc("""There are {count} available things to listen to.
Let me read you their titles, starting with the most recent episodes.
""")

## Player States

class State(object):
    def __init__(self, player):
        # debug_state_history.append(self.__class__.__name__)
        self.player = player
    def enter(self):
        """
        Subclasses may implement this to trigger certain behavior upon
        the player entering this state
        """

    def exit(self):
        """
        Subclasses may implement this to trigger certain behavior upon
        the player exiting this state
        """

    def dispatch(self, event):
        raise NotImplementedError("Your state subclass must implement the "
                                  "dispatch() method")

class Asleep(State):
    def dispatch(self, event):
        self.player.set_state(ResumeIfPossible)

class ResumeIfPossible(State):
    def __init__(self, player):
        super(ResumeIfPossible, self).__init__(player)

    def enter(self):
        if self.player.now_playing is not None:
            speech = MESSAGE_RESUME.format(
                title=now_playing.title,
                podcast=now_playing.podcast
            )
            self.player.speak(speech)
        else:
            self.player.set_state(ListIntro)

    def dispatch(self, event):
        if event:
            if event.body['button'] == BUTTON_PLAY:
                self.player.set_state(Playing)
            else:
                self.player.set_state(ListIntro)

class ListIntro(State):
    def enter(self):
        speech = MESSAGE_LISTINTRO.format(count=self.player.episode_count())
        self.player.speak(speech, block=True)
        self.player.set_state(ListItem)

class ListItem(State):
    def __init__(self, *args, **kwargs):
        super(ListItem, self).__init__(*args, **kwargs)
        self.tick_count = 0
    def enter(self):
        self.player.speak("Press the green play button to hear Episode Title Here", block=True)
    def dispatch(self, event):
        event_type, event_data = event
        if event_type == 'tick':
            self.tick_count += 1
            # TODO: progress to next ListItem

# Speech

class SpeechRequest(object):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    
    def __init__(self, msg):
        self.msg = msg
        self.ref = None
    def play(self):
        self.ref = subprocess.Popen((settings['speech.helper'], self.msg))
    def wait(self):
        if self.ref is None:
            return
        while self.status() != SpeechRequest.COMPLETED:
            time.sleep(0.2)
    def stop(self):
        if self.ref:
            try:
                self.ref.terminate()
            except OSError as e:
                if e.errno == errno.ESRCH:
                    pass # race condition where pid might be cleaned up before
                         # we try to kill it
                else:
                    raise
    def status(self):
        if self.ref is None:
            return SpeechRequest.NOT_STARTED
        else:
            if self.ref.poll() is None:
                return SpeechRequest.IN_PROGRESS
            else:
                return SpeechRequest.COMPLETED
    @classmethod
    def test(cls):
        a = cls("Hello Mr. User. Please select an action to continue.")
        a.play()
        print "Playing..."
        a.wait()
        print "Completed!"

# Player Thread & Event Loop

class Player(multiprocessing.Process):
    def __init__(self):
        self.running = True
        self._current_speech = None
        self.now_playing = None
        super(Player, self).__init__()
        
        self._state = Asleep(self)
        self.event_queue = multiprocessing.Queue()

    def speak(self, message, block=False):
        if self._current_speech is not None:
            self._current_speech.stop()
        self._current_speech = SpeechRequest(message)
        self._current_speech.play()
        if block:
            self._current_speech.wait()

    def set_state(self, state_class):
        self._state.exit()
        self._state = state_class(self)
        self._state.enter()

    def dispatch(self, event):
        if event[0] == 'quit':
            self.running = False
        else:
            self._state.dispatch(event)

    def episode_count(self):
        return Episode.query.count()
    
    def run(self):
        while self.running:
            try:
                event = self.event_queue.get(block=True, timeout=1.0)
                self.dispatch(event)
            except Queue.Empty:
                pass # try again for another second
                     # (prevents waiting forever on quit for a blocking get())
        # clean up SQLAlchemy connection
        Session.bind.dispose()
