import sys
import time
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import getImagePhoto as take
import sendText as talk
import getStateFromImage as getState
import connect_four as game

# Global variable to store the ReactToTouch module instance
ReactToTouch = None
memory = None

firstMove = True # Se asume que la primera move siempre es del enemigo
actualState = None
previousState = None
IP1 = None
PORT1 = None

class ReactToTouch(ALModule):
    """ A simple module able to react
        to touch events.
    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to TouchChanged event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("TouchChanged",
            "ReactToTouch",
            "onTouched")

    def onTouched(self, strVarName, value):
        """ This will be called each time a touch
        is detected.

        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        memory.unsubscribeToEvent("TouchChanged",
            "ReactToTouch")

        global IP1, PORT1

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
                self.play(IP1, PORT1)
                break

        # Subscribe again to the event
        memory.subscribeToEvent("TouchChanged",
            "ReactToTouch",
            "onTouched")

    def say(self, bodies):
        if (bodies == []):
            return

        sentence = "My " + bodies[0]

        for b in bodies[1:]:
            sentence = sentence + " and my " + b

        if (len(bodies) > 1):
            sentence = sentence + " are"
        else:
            sentence = sentence + " is"
        sentence = sentence + " touched."

        self.tts.say(sentence)

    def play(self, IP, PORT):

        global firstMove, previousState

        path = take.showNaoImage(IP, PORT)
        # print path
        # firstMove = False
        print "Take photo"
        actualState = getState.ejecutar(path)
        # print actualState
        print "Get actual state"

        # Check if it's the first move
        if firstMove:
            print "It's the first move"
            previousState = previousStateInicial()
            print "------"
            (h, move) = game.play(actualState) # AI move
            print h, move

            # Logic
            previousState = putNewPiece(actualState, move)
            firstMove = False
            # Talk
            talk.talk("Put the piece in the colum " + str(move), IP, PORT)
            time.sleep(0.8)
            talk.talk("It's your turn, when you finish, touch me some sensor to play", IP, PORT)
        
        else:
            print "It is not the first move"
            (accept, i, j) = acceptState(previousState, actualState)
            print accept, i, j
            if accept: # The lecture photo is OK
                print "The state is accepted"
                # Check if the enemy already win
                checkLose = checkWinner(actualState, i, j)
                if checkLose:
                    talk.talk("I've lost", IP, PORT)
                    sys.exit(0)
                else: # Can continiue playing
                    (h, move) = game.play(actualState) # IA Move
                    previousState = putNewPiece(actualState, move)
                    # Talk
                    talk.talk("Put the piece in the column " + str(move), IP, PORT)
                    # Check if we win
                    if h == 50:
                        talk.talk("I win", IP, PORT)
                        sys.exit(0)
                    time.sleep(1)
                    talk.talk("It's your turn", IP, PORT)
            else:
                talk.talk("It's necesary take another photo", IP, PORT)
            print "Exit from play"

# -----------------------------------------------------
# Count the diferencces between the states, if is only 1 the state is correct
def acceptState(st1, st2):
    dif = 0
    reti = -1 # Position i where the difference was found
    retj = -1 # Position j where the difference was found
    print st1 # Previous
    print "-----------"
    print st2 # Actual
    for i in range(0, len(st1)):
        for j in range(0, len(st1[0])):
            if st1[i][j] != st2[i][j]:
                dif += 1
                reti = i
                retj = j
    if dif != 1:
        return (False, reti, retj)
    return (True, reti, retj)

# Returns an initial state in case it is the first move
def previousStateInicial():
    s =   [[0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],]
    return s

# Update the state where the AI wants to play
def putNewPiece(state, move):
    i = 0
    flag = False # Indicate if the piece was put
    while (i < len(state) and (not flag)):
        if state[i][move] != 0:
            state[i-1][move] = 1
            flag = True
        else:
            i += 1
    if i == len(state): # If is necessary put the piece in the last row
        state[i-1][move] = 1
    return state

# Check if someone win and tell who
def checkWinner(state, i, j):
    n = -1 # Enemy mark
    operators = [0,1,2,3,4,5,6]
    m = n
    br = game.Board(mark=m, i=i, j=j, state=state, value="1",operators=operators, operator=None, parent=None,objective=None)
    return br.isWinner()

def main(ip, port):
    """ Main entry point
    """
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    global IP1, PORT1
    IP1 = ip
    PORT1 = port
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

# Check if a IP is valid
def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

if __name__ == '__main__':
    IP = "nao.local"  # Replace here with your NaoQi's IP address.
    PORT = 9559
    # Read IP address from first argument if any.
    if len(sys.argv) > 1:
        validate = sys.argv[1]
        if validate_ip(validate):
            IP = validate
        else:
            print "IP Invalid, It will be use the nao.local IP"

    # Execute the program
    main(IP, PORT)