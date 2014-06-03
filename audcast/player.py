import time
import Queue
import threading
from pprint import pprint
from audcast.buttons import buttons
from audcast.database import db_session

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

    def dispatch(self, event):
        raise NotImplementedError("Your state subclass must implement the "
                                  "dispatch() method")

class Asleep(State):
    def dispatch(self, event):
        self.player.state = ResumeIfPossible(self.player)


class ResumeIfPossible(State):
    def __init__(self, player):
        super(ResumeIfPossible, self).__init__(player)
        if self.player.now_playing is not None:
            speech = MESSAGE_RESUME.format(
                title=now_playing.title,
                podcast=now_playing.podcast
            )
            self.player.speak(speech)
        else:
            self.player.state = ListIntro(self.player)

    def dispatch(self, event):
        if event:
            if event.body['button'] == BUTTON_PLAY:
                self.player.state = Playing(self.player)
            else:
                self.player.state = ListIntro(self.player)

class ListIntro(State):
    def __init__(self, player):
        super(ListIntro, self).__init__(player)
        speech = MESSAGE_LISTINFO.format(count=player.episode_count())
        self.player.speak(speech, block=True)
        self.player.state = ListItem(self.player)

# Speech

class SpeechRequest(object):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    
    def __init__(self, msg):
        self.msg = msg
        self.ref = None
    def play(self):
        self.ref = subprocess.Popen(('speak', self.msg)) # TODO: switch back to flite for linux
    def wait(self):
        if self.ref is None:
            return
        while self.status() != SpeechRequest.COMPLETED:
            time.sleep(0.2)
    def stop(self):
        if self.ref:
            self.ref.terminate()
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
        a = cls("Hello, user. Please select an action to continue.")
        a.play()
        print "Playing..."
        a.wait()
        print "Completed!"

# Player Thread & Event Loop

class Player(threading.Thread):
    def __init__(self):
        self.running = True
        self._current_speech = None
        self.now_playing = None
        super(Player, self).__init__()
        
        self.state = Asleep(self)
        self.event_queue = Queue.Queue()
    
    def speak(self, message):
        if self._current_speech is not None:
            self._current_speech.stop()
        self._current_speech = SpeechRequest(message)
        self._current_speech.play()
    
    def run(self):
        while self.running:
            try:
                event = self.event_queue.get(block=True, timeout=1.0)
                self.state.dispatch(event)
                event_queue.task_done()
            except Queue.Empty:
                pass # try again for another second
                     # (prevents waiting forever on quit for a blocking get())
            

# player_thread = Player()
# 
# def button_handler(channel):
#     event_queue.put(channel)
# 
# if __name__ == '__main__':
#     player_thread.start()
#     
#     input_txt = ''
#     while input_txt != 'q':
#         if input_txt == 'e':
#             button_handler(buttons.ESCAPE)
#         elif input_txt == 'p':
#             button_handler(buttons.PREVIOUS)
#         elif input_txt == '.':
#             button_handler(buttons.PLAYPAUSE)
#         elif input_txt == 'n':
#             button_handler(buttons.NEXT)
#         pprint(debug_state_history)
#         print
#         print '[e] escape'
#         print '[p] previous'
#         print '[.] play/pause'
#         print '[n] next'
#         input_txt = raw_input('> ')
#     
#     print 'quitting...'
#     player_thread.running = False
#     event_queue.join()
#     print 'player_thread.running', player_thread.running
#     player_thread.join()
