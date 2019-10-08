import math
import numpy as np
import cv2
import Queue

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

# Retorna el numero del color identificado: -1 Negro, 1 Blanco, 0 Verde
def getColor(i, j, imgBlancas, imgEspacios):
    blanco = imgBlancas[i, j]
    espacio = imgEspacios[i, j]
    if espacio == 255: # Si la ficha es un espacio
        return 0
    elif blanco == 255: # Si la ficha es blanca
        return 1
    else: # Es una ficha negra
        return -1

# Devuelve las coordenadas (X,Y) de los centros de las fichas y su area
def getCentros(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) # Convertir imagen a HSV
    hue, saturation, value = cv2.split(img) # Extraer valores de img
    _, ht = cv2.threshold(hue, 50, 255, cv2.THRESH_BINARY) # Hue Threshold
    _, st = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY) # Saturation Threshold
    _, vt = cv2.threshold(value, 0, 255, cv2.THRESH_BINARY) # Value Threshold
    # Combinar los thresholds
    imgFinal = cv2.bitwise_and(ht, st)
    imgFinal = cv2.bitwise_and(imgFinal, vt)
    # Invertir foto en open CV
    imgFinal = cv2.bitwise_not(imgFinal)
    # Suavizar la imagen y sacarle los centros
    kernel = np.ones((5,5), np.uint8)
    mascara = cv2.morphologyEx(imgFinal, cv2.MORPH_OPEN, kernel)
    contorno, _ = cv2.findContours(mascara.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    puntos = [] # Guarda X,Y,Area  
    for c in contorno:
        m = cv2.moments(c)
        if int(m["m00"])!=0:
            cx = int(m["m10"]/m["m00"]) # Coordenada X de un centro
            cy = int(m["m01"]/m["m00"]) # Coordenada Y de un centro
            area = cv2.contourArea(c)
            puntos.append((cx, cy, area)) # Guarda los datos de un centro
    return puntos   

# Devuelve las coordenadas de los puntos de interes
def getPuntos(centros):
    q = Queue.PriorityQueue() # Queue para ordenar las areas
    areaPromedio = 1652 # Area promedio de huecos del tablero
    for i in range(0, len(centros)):
        a = centros[i][2] # Area de un punto
        q.put((abs(areaPromedio-a), centros[i]))
    # Extraer los 42 puntos utiles
    cont = 0
    puntos = []
    while not q.empty() and cont<42:
        puntos.append(q.get()[1])
        cont += 1
    return puntos

# Organiza los puntos en sus coordenadas (X,Y)
def organizarPuntos(puntos):
    queueY = Queue.PriorityQueue() # Queue para ordenar las coordenadas Y
    for i in range(0, len(puntos)):
        y = puntos[i][1] # Valor Y del punto
        queueY.put((y, puntos[i]))
    puntosMatriz = []
    for i in range(0, 6):
        queueX = Queue.PriorityQueue() # Queue para ordenar las coordenadas X
        for j in range(0, 7):
            p = queueY.get()[1] # Punto actual
            queueX.put((p[0], p))
        fila = []
        for j in range(0, 7):
            fila.append(queueX.get()[1])
        puntosMatriz.append(fila)
    return puntosMatriz

# Devuelve la foto con solo fichas blancas
def fotoBlancas(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) # Convertir imagen a HSV
    hue, saturation, value = cv2.split(img) # Extraer valores de img
    _, ht = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY) # Hue Threshold
    _, st = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY) # Saturation Threshold
    _, vt = cv2.threshold(value, 230, 255, cv2.THRESH_BINARY) # Value Threshold
    # Combinar los thresholds
    imgFinal = cv2.bitwise_and(ht, st)
    imgFinal = cv2.bitwise_and(imgFinal, vt)
    # Suavizar la imagen
    kernel = np.ones((5,5), np.uint8)
    imgFinal = cv2.morphologyEx(imgFinal, cv2.MORPH_OPEN, kernel)
    return imgFinal

# Devuelve la foto con solo espacios
def fotoEspacios(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) # Convertir imagen a HSV
    hue, saturation, value = cv2.split(img) # Extraer valores de img
    _, ht = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY) # Hue Threshold
    _, st = cv2.threshold(saturation, 190, 255, cv2.THRESH_BINARY) # Saturation Threshold
    _, vt = cv2.threshold(value, 0, 255, cv2.THRESH_BINARY) # Value Threshold
    # Combinar los thresholds
    imgFinal = cv2.bitwise_and(ht, st)
    imgFinal = cv2.bitwise_and(imgFinal, vt)
    # Suavizar la imagen
    kernel = np.ones((5,5), np.uint8)
    imgFinal = cv2.morphologyEx(imgFinal, cv2.MORPH_OPEN, kernel)
    return imgFinal

# Saca los estados de la imagen
def getEstado(img, puntos):
    imgBlancas = fotoBlancas(img)
    imgEspacios = fotoEspacios(img)
    # Definir un estado inicial
    matriz=[[0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0]]
    for j in range(0, len(matriz[0])):
        i = len(matriz)-1 # Para recorrer de abajo hacia arriba
        flag = False # Indica si existe un espacio en la columna     
        while i>=0 and (not flag):
            p = puntos[i][j] # Punto actual
            index = getColor(p[1], p[0], imgBlancas, imgEspacios)
            if index == -1: # Ficha Negra
                matriz[i][j] = -1 # Indicador de la ficha negra
            elif index == 1: # Ficha Blanca
                matriz[i][j] = 1 # Indicador de la ficha blanca
            else: # Ficha Verde
                flag = True
            i -= 1
    return matriz

# Pruebas con OpenCV
def testCV2(img): # frame = img
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    blue, green, red = cv2.split(img) # Blue, Green, Red

    cv2.namedWindow("ventana")
    cv2.createTrackbar("Green", "ventana", 0, 255, nothing)
    cv2.createTrackbar("Blue", "ventana", 0, 255, nothing)
    cv2.createTrackbar("Red", "ventana", 0, 255, nothing)

    while True:
        cv2.imshow("ventana", img)
        r = cv2.getTrackbarPos("Red", "ventana")
        g = cv2.getTrackbarPos("Green", "ventana")
        b = cv2.getTrackbarPos("Blue", "ventana")
        _, rt = cv2.threshold(red, r, 255, cv2.THRESH_BINARY)
        _, gt = cv2.threshold(green, g, 255, cv2.THRESH_BINARY)
        _, bt = cv2.threshold(blue, b, 255, cv2.THRESH_BINARY)
        final = cv2.bitwise_and(rt, gt)
        final = cv2.bitwise_and(final, bt)
        # Invertir foto en open CV
        # final = cv2.bitwise_not(final)
        cv2.imshow("Final", final)
        k = cv2.waitKey(1)
        if k == 27:
            break

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
    # cv2.imshow("Final", imgFinal)
    # k = cv2.waitKey(0)
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
    print "-----------------------"
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
        # Sacar los centros la cuadricula con el area
        centros = getCentros(imgC)
        # Sacar los puntos que nos interesan
        puntos = getPuntos(centros)
        puntos = organizarPuntos(puntos)
        # Sacar los estados de la cuadricula
        matriz = getEstado(imgC, puntos)
        print ""
        for i in range(0, len(matriz)):
            print matriz[i]
        return matriz

        # ---- PRUEBAS

        # imgB = fotoBlancas(imgC)
        # imgE = fotoEspacios(imgC)
        # cv2.imshow("Blancas", imgB)
        # cv2.imshow("Espacios", imgE)
        # cv2.waitKey(0)
        # testCV2(imgC)
    except IOError:
        print "No se encontro la imagen"