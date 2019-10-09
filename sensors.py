import sys
import time
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import getImagePhoto as take
import sendText as talk
import getStateFromImage as getState
import Fourinline as game

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
        # for p in value:
        #     if p[1]:
        #         play(IP1, PORT1)

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
                self.play(IP1, PORT1)
                break

        # self.say(touched_bodies)

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
                checkLose = comprobarGanador(actualState, i, j)
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

def acceptState(st1, st2):
    dif = 0 # Cuenta las diferencias entre los tableros
    reti = -1
    retj = -1
    print st1 # Anterior
    print "-----------"
    print st2 # Actual
    for i in range(0, len(st1)):
        for j in range(0, len(st1[0])):
            if st1[i][j] != st2[i][j]:
                dif += 1
                reti = i
                retj = j
    # La diferencia solo debe ser de 1 fichas
    if dif != 1:
        return (False, reti, retj)
    return (True, reti, retj)

# Devuelve un estado anterior inicial en caso de ser la primera move
def previousStateInicial():
    s =   [[0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],]
    return s

# Actualiza un estado poniendo una nueva ficha
def putNewPiece(estado, move):
    i = 0
    flag = False # Indica si la ficha ya fue puesta
    while (i < len(estado) and (not flag)):
        if estado[i][move] != 0:
            estado[i-1][move] = 1 # Se asume que estamos poniendo una move de la IA
            flag = True
        else:
            i += 1
    if i == len(estado): # Es necesario poner en la ultima fila
        estado[i-1][move] = 1
    return estado

# Verifica si alguien gano, y retorna quien gano
def comprobarGanador(estado, i, j):
    n = -1 # Marca del enemigo
    operators = [0,1,2,3,4,5,6]
    m = n
    br = game.Board(mark=m, i=i, j=j, state=estado, value="1",operators=operators, operator=None, parent=None,objective=None)
    return br.isWinner()

# def play(IP, PORT):

#     global firstMove, actualState, previousState

#     path = take.showNaoImage(IP, PORT)
#     # print path
#     firstMove = False
#     actualState = getState.ejecutar(path)

#     # print actualState

#     # Revisa si es la primera move
#     if firstMove:
#         previousState = previousStateInicial()
#         (h, move) = game.play(actualState) # Esta es la move que nos devuelve la IA
#          # Logica
#         previousState = putNewPiece(actualState, move)
#         firstMove = False
#         # Hablar
#         talk.talk("Put the piece in the colum " + str(move), IP, PORT)
#         time.sleep(1)
#         talk.talk("It's your turn, when you finish, touch me some sensor to play", IP, PORT)
       
#     else:
#         (accept, i, j) = acceptState(previousState, actualState)
#         if accept: # Se puede seguir jugando

#             # Verifica si gana el otro
#             checkLose = comprobarGanador(actualState, i, j)

#             if checkLose: # Si el otro gana
#                 talk.talk("Oh shit, i've lost, teacher, please, forgive us, we are mortals, we aren't perfects", IP, PORT)
#                 sys.exit(0)
#             else: # Si nadie gana, juega normal
#                 (h, move) = game.play(actualState) # Esta es la move que nos devuelve la IA
#                 previousState = putNewPiece(actualState, move)
#                 # Hablar
#                 talk.talk("Put the piece in the column " + str(move), IP, PORT)
#                 # Comprobar si ganamos
#                 if h == 50:
#                     talk.talk("I win, we derserve a 5", IP, PORT)
#                     sys.exit(0)
#                 time.sleep(1)
#                 talk.talk("It's your turn", IP, PORT)
                

#         else: # Es necesario tomar otra foto
#             talk.talk("It's necesary take another photo", IP, PORT)

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


if __name__ == '__main__':
    IP = "192.168.43.219"  # Replace here with your NaoQi's IP address.
    PORT = 9559
    main(IP, PORT)