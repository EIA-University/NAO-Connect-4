#import getImagePhoto as take
#import sendText as talk
import convertirImgToMatrix as conv
# import time
# from naoqi import ALProxy
# import Fourinline as games
# desktop-keel9jm.local.:54103
# nao.local 9559

# Main para utilizar con NAO
# if __name__ == '__main__':
#     IP = "nao.local"  # Replace here with your NaoQi's IP address.
#     PORT = 9559
#     while True:
#         path = take.showNaoImage(IP, PORT)
#         print path
#         matrix = conv.ejecutar(path)
#         print matrix
#         jugada = games.play(matrix)
#         talk.talk("Put the piece in the colum " + str(jugada), IP, PORT)
#         time.sleep(1)
#         talk.talk("It's your turn, in 10 seconds, i'm going to play", IP, PORT)
#         time.sleep(10)

if __name__ == '__main__':
    import os
    for file in os.listdir("imagenes/"):
        if file.endswith(".png"):
            path =  os.path.join("imagenes/", file)
            path2 =  os.path.join("cuadricula/", file)
            imgB = conv.ejecutar(path, path2)

    # path = "imagenes/eaycoixynf.png"
    # conv.ejecutar(path, "cuad.png")