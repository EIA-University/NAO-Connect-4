# -*- encoding: UTF-8 -*-
""" Say `My {Body_part} is touched` when receiving a touch event
"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

import getImagePhoto as take
import sendText as talk
import convertirImgToMatrix as conv
import Fourinline as games

# Global variable to store the ReactToTouch module instance
ReactToTouch = None
memory = None
IP = None
PORT = None

class ReactToTouch(ALModule):
    """ A simple module able to react
        to touch events.
    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        # self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to TouchChanged event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")

    def onTouched(self, strVarName, value):
        """ This will be called each time a touch
        is detected.

        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        memory.unsubscribeToEvent("TouchChanged", "ReactToTouch")

        # Aqui empieza a hacer cualquier cosa

        for p in value:
            if p[1]:
                jugar(self.IP, self.PORT)
                break
        # Aqui acaba de hacer cualquier cosa, reparar sin break :(

        # Subscribe again to the event
        memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")

    
def jugar(IP, PORT):
    path = take.showNaoImage(IP, PORT)
    print path
    matrix = conv.ejecutar(path)
    print matrix
    jugada = games.play(matrix)
    talk.talk("Put the piece in the colum " + str(jugada), IP, PORT)
    time.sleep(1)
    talk.talk("It's your turn, when you finish, touch some sensor for me to play", IP, PORT)



def main(ip, port):
    """ Main entry point
    """
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       ip,          # parent broker IP
       port)        # parent broker port


    global ReactToTouch
    ReactToTouch = ReactToTouch("ReactToTouch")


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    IP = "nao.local"  # Replace here with your NaoQi's IP address.
    PORT = 9559

    main(IP, PORT)