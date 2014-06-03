from audcast.player import Player
from audcast.buttons import buttons

player_thread = Player()

def button_handler(channel):
    player_thread.event_queue.put(channel)

if __name__ == '__main__':
    player_thread.start()
    # buttons.initialize(callback=button_handler)
    input_txt = ''
    while input_txt != 'q':
        if input_txt == 'e':
            button_handler(buttons.ESCAPE)
        elif input_txt == 'p':
            button_handler(buttons.PREVIOUS)
        elif input_txt == '.':
            button_handler(buttons.PLAYPAUSE)
        elif input_txt == 'n':
            button_handler(buttons.NEXT)
        print
        print '[e] escape'
        print '[p] previous'
        print '[.] play/pause'
        print '[n] next'
        input_txt = raw_input('> ')
    
    print 'quitting...'
    player_thread.running = False
    print 'player_thread.running', player_thread.running
    player_thread.join()
