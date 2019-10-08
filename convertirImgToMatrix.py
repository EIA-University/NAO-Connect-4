import math
import numpy as np
import cv2

# Espacio: 0
# Fichas blancas (IA): 1
# Fichas Negras (Enemigo): -1
# NOTA: OpenCV2 does not use RBG, use BGR (Blue, Green, Red)

# Vuelve la foto blanco y negro sacando los promedios de RGB
def binarizarImg(img):
    imgB, imgG, imgR = cv2.split(img) # Blue, Green, Red
    _,threshold = cv2.threshold(imgR, 120, 255, cv2.THRESH_BINARY_INV)
    return threshold

# Retorna la posicion del pixel inicial y final en donde se encuentra el tablero (Verticalmente)
def delimitarAlto(img, w, h):
    posIni = -1
    posFin = -1
    middle = math.trunc(w / 2)
    cont = 0 # 3 pixeles consecutivos seran la sennal
    i = 0
    stop = False # Indicacion de parada
    while (i < h and (not stop)): # Buscar la posicion inicial
        c = img[i, middle]
        if c == 0: # Si es negro
            cont += 1
        elif c == 255 and cont > 0: # Si se danna la fila consecutiva
            cont = 0
        if cont == 3: # Si existen 3 negros seguidos
            posIni = i
            stop = True # Detener el ciclo
        i += 1 # Avanzar en el ciclo
    cont = 0
    i = h-1
    stop = False
    while ( i > 0 and (not stop)): # Buscar la posicion final
        c = img[i, middle]
        if c == 0: # Si es negro
            cont += 1
        elif c == 255 and cont > 0: # Si se danna la fila consecutiva
            cont = 0
        if cont == 3: # Si existen 3 negros seguidos
            posFin = i
            stop = True
        i -= 1 # Avanzar en el ciclo
    return(posIni, posFin)

# Retorna la posicion del pixel inicial y final en donde se encuentra el tablero (Horizontalmente)
def delimitarAncho(img, w, h):
    posIni = -1
    posFin = -1
    middle = math.trunc(h/2)
    cont = 0 # 3 pixeles consecutivos seran la sennal
    i = 0
    stop = False # Indicacion de parada
    while (i < w and (not stop)): # Buscar la posicion inicial
        c = img[middle, i]
        if c == 0: # Si es negro
            cont += 1
        elif c == 255 and cont > 0: # Si se danna la fila consecutiva
            cont = 0
        if cont == 3: # Si existen 3 negros seguidos
            posIni = i
            stop = True # Detener el ciclo
        i += 1 # Avanzar en el ciclo
    cont = 0
    i = w-1
    stop = False
    while (i > 0 and (not stop)): # Buscar la posicion final
        c = img[middle, i]
        if c == 0: # Si es negro
            cont += 1
        elif c == 255 and cont > 0: # Si se danna la fila consecutiva
            cont = 0
        if cont == 3: # Si existen 3 negros seguidos
            posFin = i
            stop = True
        i -= 1 # Avanzar en el ciclo
    return(posIni + 10, posFin)

# Genera una subimagen basado en ciertas posiciones
def cortarImg(img, xMin, yMin, xMax, yMax):
    crop_img = img[yMin:yMax, xMin:xMax]
    return crop_img

# Dibuja la cuadricula de la foto
def dibujarCuadricula(img, w, h):
    # Dibujar rayas Verticales
    space = math.trunc(w/7)
    for j in range(1, 7): # Generar 6 lineas
        for i in range(0, h): # Toda la profundidad
            img[i, space * j] = [128, 0, 255] # Lineas en (BGA)
    # Dibujar rayas Horizontales
    space = math.trunc(h/6)
    for i in range(1, 6): # Generar 5 lineas
        for j in range(0, w): # Todo el ancho
            img[i * space, j] = [128, 0, 255]
    return img

# Retorna el numero del color identificado: 0 Negro, 1 Blanco, 2 Verde
def getColor(color):
    # Valores promedio tomados de varias fotos
    avgBlack = 63.30769231
    avgWhite = 210.5897436
    avgGreen = 113.8717949
    c1 = int(color[0])
    c2 = int(color[1])
    c3 = int(color[2])
    c = (c1+c2+c3)/3 # RGB Promedio
    distancias = [] # Distancia del color al promedio de cada uno
    distancias.append(abs(c - avgBlack))
    distancias.append(abs(c - avgWhite))
    distancias.append(abs(c - avgGreen))
    mini = min(distancias) # Distancia minima
    i = 0
    while i < 3:
        if distancias[i] == mini:
            return i
        i += 1

# Retorna el tipo de estado de la ficha, segun el color del centro de su delimitacion
def getPoints(img, w, h):
    # Sacamos la mitad de los cuadros
    ySpace = math.trunc(w / 7) # n
    yCenter = math.trunc(ySpace / 2) # m
    xSpace = math.trunc(h / 6) 
    xCenter = math.trunc(xSpace / 2)
    # Matriz de puntos de los centros
    puntos = []
    for i in range(1, 15, 2): # 7 iteraciones
        p = []
        for j in range(1, 13, 2): # 6 iteraciones
            p.append((yCenter * i, xCenter * j))
        puntos.append(p)
    return puntos

# Saca los estados de la imagen
def getStates(img, puntos):
    matrix = []
    for i in range(0, len(puntos)):
        aux = []        
        flagSpace = False # Indica si algun punto es verde
        for j in reversed(range(0, len(puntos[0]))):
            px = puntos[i][j][0]
            py = puntos[i][j][1]
            c = img[py, px]
            index = getColor(c)   
            if not flagSpace:
                if index == 0:
                    # Si es Negro
                    aux.append(-1)
                elif index == 1:
                    # Si es Blanco
                    aux.append(1)
                elif index == 2:
                    # Si es Verde
                    flagSpace = True
                    aux.append(0)
            else:
                aux.append(0)
        aux.reverse()
        matrix.append(aux)
    matrix = np.transpose(matrix)    
    return matrix

# Pruebas con OpenCV
def testCV2(img): # frame = img
    # img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    # blue, green, red = cv2.split(img) # Blue, Green, Red

    # cv2.namedWindow("ventana")
    # cv2.createTrackbar("Green", "ventana", 0, 255, nothing)
    # cv2.createTrackbar("Blue", "ventana", 0, 255, nothing)
    # cv2.createTrackbar("Red", "ventana", 0, 255, nothing)

    # while True:
    #     cv2.imshow("ventana", img)
    #     r = cv2.getTrackbarPos("Red", "ventana")
    #     g = cv2.getTrackbarPos("Green", "ventana")
    #     b = cv2.getTrackbarPos("Blue", "ventana")
    #     _, rt = cv2.threshold(red, r, 255, cv2.THRESH_BINARY)
    #     _, gt = cv2.threshold(green, g, 255, cv2.THRESH_BINARY)
    #     _, bt = cv2.threshold(blue, b, 255, cv2.THRESH_BINARY)
    #     final = cv2.bitwise_and(rt, gt)
    #     final = cv2.bitwise_and(final, bt)
    #     cv2.imshow("Final", final)
    #     k = cv2.waitKey(1)
    #     if k == 27:
    #         break

    # img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    # blue, green, red = cv2.split(img) # Blue, Green, Red
    # # imgC = cv2.cvtColor(imgC, cv2.COLOR_RGB2GRAY)
    # retval, threshold = cv2.threshold(green, 180, 255, cv2.THRESH_BINARY)
    # kernel = np.ones((5,5), np.uint8)
    # mask = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
    
    # contorno, _ = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for i in contorno:
    #     m = cv2.moments(i)
    #     if int(m["m00"])!=0:
    #         cx = int(m["m10"]/m["m00"])
    #         cy = int(m["m01"]/m["m00"])
    #         # area = cv2.contounrArea(i)
    #         cv2.circle(mask, (cx, cy), 5, (0, 255, 0), 2)
    # #im3 = cv2.drawContours(mask, contorno[4], -1, (0, 255, 0), 3)
    # cv2.imshow("sdf", mask)
    # cv2.waitKey(0)
    pass

# Test 2
def testCV22(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hue, saturation, value = cv2.split(img) # HSV

    # cv2.namedWindow("Ventana")
    # cv2.createTrackbar("Hue", "Ventana", 0, 255, nothing)
    # cv2.createTrackbar("Saturation", "Ventana", 0, 255, nothing)
    # cv2.createTrackbar("Value", "Ventana", 0, 255, nothing)

    # while True:
        # cv2.imshow("Ventana", img)
        # h = cv2.getTrackbarPos("Hue", "Ventana")
        # s = cv2.getTrackbarPos("Saturation", "Ventana")
        # v = cv2.getTrackbarPos("Value", "Ventana")
    _, ht = cv2.threshold(hue, 50, 255, cv2.THRESH_BINARY)
        # _, ht = cv2.threshold(hue, h, 255, cv2.THRESH_BINARY)
    _, st = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY)
    _, vt = cv2.threshold(value, 0, 255, cv2.THRESH_BINARY)
    final = cv2.bitwise_and(ht, st)
    final = cv2.bitwise_and(final, vt)
        # cv2.imshow("Final", final)
        # k = cv2.waitKey(1)
        # if k == 27:
        #     break
    
    # _, hue_t = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY) # Hue Threshold
    # _, saturation_t = cv2.threshold(saturation, 150, 255, cv2.THRESH_BINARY) # Saturation Threshold
    # _, value_t = cv2.threshold(value, 0, 255, cv2.THRESH_BINARY) # Value Threshold
    # imgFinal = cv2.bitwise_and(hue_t, saturation_t)
    # imgFinal = cv2.bitwise_and(imgFinal, value_t)
    imgFinal = final
    # Invertir foto en open CV
    imgFinal = cv2.bitwise_not(imgFinal)
    cv2.imshow("Final", imgFinal)
    k = cv2.waitKey(0)
    kernel = np.ones((5,5), np.uint8)
    mascara = cv2.morphologyEx(imgFinal, cv2.MORPH_OPEN, kernel)
    contorno, _ = cv2.findContours(mascara.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contorno:
        m = cv2.moments(c)
        if int(m["m00"])!=0:
            cx = int(m["m10"]/m["m00"])
            cy = int(m["m01"]/m["m00"])
            # area = cv2.contounrArea(i)
            cv2.circle(mascara, (cx, cy), 3, (0, 255, 0), 2)
            print "Area: ", cv2.contourArea(c)
            cv2.imshow("sdf", mascara)
            cv2.waitKey(0)
    

def nothing(x):
    pass

# Funcion principal que ejecuta todo
def ejecutar(path):
    try: # Cargar la imagen
        img = cv2.imread(path)
        h, w, _ = img.shape # Sacar tamanno a la imagen (ignorar c)
        imgB = binarizarImg(img) # Binarizar imagen
        # Delimitar el tablero
        (yMin, yMax) = delimitarAlto(imgB, w, h) # Delimitar el tablero verticalmente
        imgB = cortarImg(imgB, 0, yMin, w-1, yMax)
        h, w = imgB.shape # Esta foto ya no contiene canales
        (xMin, xMax) = delimitarAncho(imgB, w, h) # Delimitar el tablero horizontalmente
        # Cortar foto
        imgC = cortarImg(img, xMin, yMin, xMax, yMax)
        h, w, _ = imgC.shape
        # # Saca los centros la cuadricula
        centros = getPoints(imgC, w, h)
        # Sacar los estados de la cuadricula
        matrix = getStates(imgC, centros)
        #print matrix
        # return matrix


        testCV22(imgC)







        # img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        # blue, green, red = cv2.split(imgC) # Blue, Green, Red
        # # imgC = cv2.cvtColor(imgC, cv2.COLOR_RGB2GRAY)
        # retval, threshold = cv2.threshold(green, 130, 255, cv2.THRESH_BINARY)
        # kernel = np.ones((5,5), np.uint8)
        # mask = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        
        # contorno, _ = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # for i in contorno:
        #     m = cv2.moments(i)
        #     if int(m["m00"])!=0:
        #         cx = int(m["m10"]/m["m00"])
        #         cy = int(m["m01"]/m["m00"])
        #         area = cv2.contounrArea(i)
        #         cv2.circle(mask, (cx, cy), 5, (0, 255, 0), 2)
        # #im3 = cv2.drawContours(mask, contorno[4], -1, (0, 255, 0), 3)
        # cv2.imshow("sdf", mask)
        # cv2.waitKey(0)
    except IOError:
        print "No se encontro la imagen"