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

primeraJugada = True # Se asume que la primera jugada siempre es del enemigo
estadoActual = None
estadoAnterior = None

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


# -------------------Métodos auxiares--------------------------

# Compara el estado actual un estado anterior  de una diferencia
def aceptarEstado(st1, st2):
    dif = 0 # Cuenta las diferencias entre los tableros
    reti = -1
    retj = -1
    for i in range(0, len(st1)):
        for j in range(0, len(st1[0])):
            if st1[i][j] != st2[i][j]:
                dif += 1
                reti = i
                retj = j
    # La diferencia solo debe ser de 1 fichas
    if dif > 1:
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
        i += 1
    if i == len(estado): # Es necesario poner en la ultima fila
        estado[i-1][jugada] = 1
    return estado

# Verifica si alguien gano, y retorna quien gano
def comprobarGanador(estado, i, j):
    n = -1 # Marca del enemigo
    operators = [0,1,2,3,4,5,6]
    m = n
    br = games.Board(m, i, j, estado, "1",operators=operators, operator=None, parent=None,objective=None)
    return br.isWinner()



def jugar(IP, PORT):
    global primeraJugada, estadoActual, estadoAnterior

    path = take.showNaoImage(IP, PORT)
    print path
    primeraJugada = False
    #estadoActual = conv.ejecutar(path)
    estadoActual = [[0,0,0,0,0,0,0],
                    [1,0,0,0,0,0,0],
                    [1,0,0,0,0,0,0],
                    [1,0,0,0,0,0,0],
                    [1,0,0,0,0,0,0],
                    [1,-1,1,-1,1,1,1],]
    print estadoActual

    # Revisa si es la primera jugada
    if primeraJugada:
        estadoAnterior = estadoAnteriorInicial()
        (heu, jugada) = games.play(estadoActual) # Esta es la jugada que nos devuelve la IA
         # Logica
        estadoAnterior = ponerNuevaFicha(estadoActual, jugada)
        primeraJugada = False
        # Hablar
        talk.talk("Put the piece in the colum " + str(jugada), IP, PORT)
        time.sleep(1)
        talk.talk("It's your turn, when you finish, touch me some sensor to play", IP, PORT)
       
    else:
        (acepta, i, j) = aceptarEstado(estadoAnterior, estadoActual)
        if acepta: # Se puede seguir jugando

            # Verifica si gana el otro
            ganarOtro = comprobarGanador(estadoActual, i, j)

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
                talk.talk("It's your turn, when you finish, touch me some sensor to play", IP, PORT)
                

         else: # Es necesario tomar otra foto
            talk.talk("It's necesary take another photo", IP, PORT)


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
    IP = "nao.local"
    PORT = 9559