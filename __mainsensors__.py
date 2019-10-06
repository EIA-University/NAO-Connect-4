# # -*- encoding: UTF-8 -*-
# """ Say `My {Body_part} is touched` when receiving a touch event
# """

# import sys
# import time

# from naoqi import ALProxy
# from naoqi import ALBroker
# from naoqi import ALModule
# import argparse

# # Global variable to store the ReactToTouch module instance
# ReactToTouch = None
# memory = None

# class ReactToTouch(ALModule):
#     """ A simple module able to react
#         to touch events.
#     """
#     def __init__(self, name):
#         ALModule.__init__(self, name)
#         # No need for IP and port here because
#         # we have our Python broker connected to NAOqi broker

#         # Create a proxy to ALTextToSpeech for later use
#         self.tts = ALProxy("ALTextToSpeech")

#         # Subscribe to TouchChanged event:
#         global memory
#         memory = ALProxy("ALMemory")
#         memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")

#     def onTouched(self, strVarName, value):
#         """ This will be called each time a touch
#         is detected.

#         """
#         # Unsubscribe to the event when talking,
#         # to avoid repetitions
#         memory.unsubscribeToEvent("TouchChanged", "ReactToTouch")

#         # Aqui empieza a hacer cualquier cosa
#         touched_bodies = []
#         for p in value:
#             if p[1]:
#                 touched_bodies.append(p[0])

#         self.say(touched_bodies)

#         # Aqui acaba de hacer cualquier cosa

#         # Subscribe again to the event
#         memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")

#     def say(self, bodies):
#         if (bodies == []):
#             return

#         sentence = "My " + bodies[0]

#         for b in bodies[1:]:
#             sentence = sentence + " and my " + b

#         if (len(bodies) > 1):
#             sentence = sentence + " are"
#         else:
#             sentence = sentence + " is"
#         sentence = sentence + " touched."

#         self.tts.say(sentence)
    
#     def tocado(self):
#         pass


# def main(ip, port):
#     """ Main entry point
#     """
#     # We need this broker to be able to construct
#     # NAOqi modules and subscribe to other modules
#     # The broker must stay alive until the program exists
#     myBroker = ALBroker("myBroker",
#        "0.0.0.0",   # listen to anyone
#        0,           # find a free port and use it
#        ip,          # parent broker IP
#        port)        # parent broker port


#     global ReactToTouch
#     ReactToTouch = ReactToTouch("ReactToTouch")
#     print "Sali de aca"
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print
#         print "Interrupted by user, shutting down"
#         myBroker.shutdown()
#         sys.exit(0)

# -------------------Métodos auxiares--------------------------

# Compara el estado actual un estado anterior
def aceptarEstado(st1, st2):
    dif = 0 # Cuenta las diferencias entre los tableros
    for i in range(0, len(st1)):
        for j in range(0, len(st1[0])):
            if st1[i][j] != st2[i][j]:
                dif += 1
    # La diferencia solo debe ser de 1 fichas
    if dif != 1:
        return False
    return True

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
    while (i<len(estado) and (not flag)):
        if estado[i][jugada] != 0:
            estado[i-1][jugada] = 1 # Se asume que estamos poniendo una jugada de la IA
            flag = True
        i += 1
    if i == len(estado): # Es necesario poner en la ultima fila
        estado[i-1][jugada] = 1
    return estado

primeraJugada = True # Se asume que la primera jugada siempre es del enemigo
# Supongamos que este es el método jugar
if __name__ == "__main__":
    # Supongamos que es el estado que devuelve el método convertir
    estadoActual=[[0,0,0,0,0,0,0],
            [1,0,0,0,0,0,0],
            [1,0,0,0,0,0,0],
            [1,0,0,0,0,0,0],
            [1,0,0,0,0,0,0],
            [1,-1,1,-1,1,1,1],]
    if primeraJugada:
        estadoAnterior = estadoAnteriorInicial()
        jugada = 0 # Supongamos que esta es la jugada que nos devuelve la IA
        # Hablar
        estadoAnterior = ponerNuevaFicha(estadoActual, jugada)
        primeraJugada = False
    else: # Si ya no es la primera jugada
        if aceptarEstado(estadoAnterior, estadoActual): # Se puede seguir jugando
            print "Se puede seguir jugando"
            # jugada = Esta es la jugada que nos devuelve la IA
            # Hablar
            estadoAnterior = ponerNuevaFicha(estadoAnterior)
        else: # Es necesario tomar otra foto
            print "Es necesario tomar otra foto"