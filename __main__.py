import getImagePhoto as take
import sendText as talk
import convertirImgToMatrix as conv
#import Fourinline as games
#desktop-keel9jm.local.:54103
#nao.local 9559
if __name__ == '__main__':
    IP = "127.0.0.1"  # Replace here with your NaoQi's IP address.
    PORT = 54103
    
    while True:
        path = take.sinNAO(IP, PORT)
        print path
        matrix = conv.ejecutar(path)
        if matrix != False:
            pass
        else:
            talk.talk("I can't see right the game", IP, PORT)
    
    
