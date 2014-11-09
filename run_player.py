from audcast.player import Player
from audcast.buttons import buttons

player_process = Player()

def button_handler(channel):
    player_process.event_queue.put(('button', channel))

if __name__ == '__main__':
    player_process.start()

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
        elif input_txt == 't':
            player_process.event_queue.put(('tick', None))
        print
        print '[e] escape'
        print '[p] previous'
        print '[.] play/pause'
        print '[n] next'
        print '[t] tick'
        input_txt = raw_input('> ')
    
    print 'quitting...'
    player_process.event_queue.put(('quit', None))
    player_process.join()
