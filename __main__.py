import getImagePhoto as take
import sendText as talk
import convertirImgToMatrix as conv
import os
import time
from naoqi import ALProxy
import Fourinline as games
# desktop-keel9jm.local.:54103
# nao.local 9559
# if __name__ == '__main__':
#     IP = "nao.local"  # Replace here with your NaoQi's IP address.
#     PORT = 9559
#     #while True:
#     path = take.showNaoImage(IP, PORT)
#     #print path
#     matrix = conv.ejecutar(path)
#         # print matrix

#         # if matrix != False:
#         #     jugada = games.play(matrix)
#         #     talk.talkSinNAO("Put the piece in the colum " + str(jugada), IP, PORT)
#         #     talk.talkSinNAO("It is your turn", IP, PORT)
#         #     time.sleep(10)
#         # else:
#         #     talk.talkSinNAO("I can't see right the game", IP, PORT)
#         #     time.sleep(5)

if __name__ == '__main__':
    # path1 = "editadas/cuadricula"
    # stri = "imagenes/prueba"
    # matrix = conv.ejecutar(path)
    # matrix.save(path1)
    for i in range(1,20):
        stri = "imagenes/prueba"
        path1 = "cuadricula/prueba"
        stri = stri + str(i)
        stri = stri + ".png"
        path1 = path1 + str(i)
        path1 = path1 + ".png"
        path = stri

        print path
        matrix = conv.ejecutar(path)
        matrix.save(path1)
    # print path
    # matrix = conv.ejecutar(path)
    #path = "imagenes/pruebaNao1.png" # Las fotos de Nao son .png