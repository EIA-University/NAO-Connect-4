""" import getImagePhoto as take
import sendText as talk
import convertirImgToMatrix as conv
import Fourinline as games """

import sensors as todo

#nao.local 9559
 if __name__ == '__nomain__':
    IP = "nao.local"  # Replace here with your NaoQi's IP address.
    PORT = 9559
    todo.main(IP, PORT)

""" if __name__ == '__main__':
    path = "imagenes/prueba5.jpg" 
    #path = "imagenes/pruebaNao1.png" # Las fotos de Nao son .png
    print path
    matrix = conv.ejecutar(path)
    print matrix """