#import getImagePhoto as take
#import sendText as talk
import convertirImgToMatrix as conv
#import time
#from naoqi import ALProxy
#import Fourinline as games
#desktop-keel9jm.local.:54103
#nao.local 9559
if __name__ == '__nomain__':
    IP = "nao.local"  # Replace here with your NaoQi's IP address.
    PORT = 9559
    while True:
        path = take.sinNAO(IP, PORT)
        #path = "imagenes/foto.jpg"
        print path
        matrix = conv.ejecutar(path)
        print matrix
        if matrix != False:
            jugada = games.play(matrix)
            talk.talkSinNAO("Put the piece in the colum " + str(jugada), IP, PORT)
            talk.talkSinNAO("It is your turn", IP, PORT)
            time.sleep(10)
        else:
            talk.talkSinNAO("I can't see right the game", IP, PORT)
            time.sleep(5)

if __name__ == '__main__':
    path = "imagenes/prueba5.jpg" 
    #path = "imagenes/pruebaNao1.png" # Las fotos de Nao son .png
    print path
    matrix = conv.ejecutar(path)
    print matrix