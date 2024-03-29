# -*- encoding: UTF-8 -*-


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

primeraJugada = True # Se asume que la primera jugada siempre es del enemigo
estadoActual = None
estadoAnterior = None
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
        #         jugar(IP1, PORT1)

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
                self.jugar(IP1, PORT1)
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

    def jugar(self, IP, PORT):

        global primeraJugada, estadoAnterior

        path = take.showNaoImage(IP, PORT)
        # print path
        # primeraJugada = False
        print "Toma foto"
        estadoActual = conv.ejecutar(path)
        # print estadoActual
        print "Saca estado actual"

        # Revisa si es la primera jugada
        if primeraJugada:
            print "Entro en primera jugada"
            estadoAnterior = estadoAnteriorInicial()
            print "1-----"
            (heu, jugada) = games.play(estadoActual) # Esta es la jugada que nos devuelve la IA
            print heu, jugada

            # Logica
            estadoAnterior = ponerNuevaFicha(estadoActual, jugada)
            primeraJugada = False
            # Hablar
            talk.talk("Put the piece in the colum " + str(jugada), IP, PORT)
            time.sleep(0.8)
            talk.talk("It's your turn, when you finish, touch me some sensor to play", IP, PORT)
        
        else:
            print "Entra en No es primera jugada"
            (acepta, i, j) = aceptarEstado(estadoAnterior, estadoActual)
            print "Saca aceptarEstado"
            print acepta, i, j
            if acepta: # Se puede seguir jugando
                print "Entra en acepta"
                # Verifica si gana el otro
                ganarOtro = comprobarGanador(estadoActual, i, j)
                print "Saca comprobarGanado"

                if ganarOtro: # Si el otro gana
                    talk.talk("Oh shit, i've lost, teacher, please, forgive us, we are mortals, we aren't perfects", IP, PORT)
                    sys.exit(0)
                else: # Si nadie gana, juega normal
                    (heu, jugada) = games.play(estadoActual) # Esta es la jugada que nos devuelve la IA
                    estadoAnterior = ponerNuevaFicha(estadoActual, jugada)
                    # Hablar
                    talk.talk("Put the piece in the column " + str(jugada), IP, PORT)
                    # Comprobar si ganamos
                    if heu == 50:
                        talk.talk("I win, we derserve a 5", IP, PORT)
                        sys.exit(0)
                    time.sleep(1)
                    talk.talk("It's your turn", IP, PORT)
                    

            else: # Es necesario tomar otra foto
                talk.talk("It's necesary take another photo", IP, PORT)
            
            print "Sali de Jugar"

# -------------------Métodos auxiares--------------------------

# Compara el estado actual un estado anterior  de una diferencia
def aceptarEstado(st1, st2):
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

# Devuelve un estado anterior inicial en caso de ser la primera jugada
def estadoAnteriorInicial():
    s =   [[0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],]
    return s

# Actualiza un estado poniendo una nueva ficha
def ponerNuevaFicha(estado, jugada):
    i = 0
    flag = False # Indica si la ficha ya fue puesta
    while (i < len(estado) and (not flag)):
        if estado[i][jugada] != 0:
            estado[i-1][jugada] = 1 # Se asume que estamos poniendo una jugada de la IA
            flag = True
        else:
            i += 1
    if i == len(estado): # Es necesario poner en la ultima fila
        estado[i-1][jugada] = 1
    return estado

# Verifica si alguien gano, y retorna quien gano
def comprobarGanador(estado, i, j):
    n = -1 # Marca del enemigo
    operators = [0,1,2,3,4,5,6]
    m = n
    br = games.Board(mark=m, i=i, j=j, state=estado, value="1",operators=operators, operator=None, parent=None,objective=None)
    return br.isWinner()

# def jugar(IP, PORT):

#     global primeraJugada, estadoActual, estadoAnterior

#     path = take.showNaoImage(IP, PORT)
#     # print path
#     primeraJugada = False
#     estadoActual = conv.ejecutar(path)

#     # print estadoActual

#     # Revisa si es la primera jugada
#     if primeraJugada:
#         estadoAnterior = estadoAnteriorInicial()
#         (heu, jugada) = games.play(estadoActual) # Esta es la jugada que nos devuelve la IA
#          # Logica
#         estadoAnterior = ponerNuevaFicha(estadoActual, jugada)
#         primeraJugada = False
#         # Hablar
#         talk.talk("Put the piece in the colum " + str(jugada), IP, PORT)
#         time.sleep(1)
#         talk.talk("It's your turn, when you finish, touch me some sensor to play", IP, PORT)
       
#     else:
#         (acepta, i, j) = aceptarEstado(estadoAnterior, estadoActual)
#         if acepta: # Se puede seguir jugando

#             # Verifica si gana el otro
#             ganarOtro = comprobarGanador(estadoActual, i, j)

#             if ganarOtro: # Si el otro gana
#                 talk.talk("Oh shit, i've lost, teacher, please, forgive us, we are mortals, we aren't perfects", IP, PORT)
#                 sys.exit(0)
#             else: # Si nadie gana, juega normal
#                 (heu, jugada) = games.play(estadoActual) # Esta es la jugada que nos devuelve la IA
#                 estadoAnterior = ponerNuevaFicha(estadoActual, jugada)
#                 # Hablar
#                 talk.talk("Put the piece in the column " + str(jugada), IP, PORT)
#                 # Comprobar si ganamos
#                 if heu == 50:
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