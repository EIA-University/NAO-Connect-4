import getImagePhoto as take
import sendText as talk
import convertirImgToMatrix as conv
import Fourinline as games

import sensors as todo

#nao.local 9559

 
if __name__ == '__main__':
    # import os
    # for file in os.listdir("imagenes/"):
    #     if file.endswith(".png"):
    #         path =  os.path.join("imagenes/", file)
    #         path2 =  os.path.join("cuadricula/", file)
    #         imgB = conv.ejecutar(path, path2)
    path = "imagenes/bkqwnlccjr.png"
    m = conv.ejecutar(path)
    print m
