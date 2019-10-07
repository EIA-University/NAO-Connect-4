import math
import numpy as np
import cv2

# Espacio: 0
# Fichas blancas (IA): 1
# Fichas Negras (Enemigo): -1
# NOTA: OpenCV2 does not use RBG, use BGR (Blue, Green, Red)

# Retorna el numero del color identificado: 0 Negro, 1 Blanco, 2 Verde
def getColor(color):
    # Valores promedio tomados de varias fotos
    avgBlack = 68.67619048
    avgWhite = 216.3619048
    avgGreen = 109.4
    c = (color[0] + color[1] + color[2]) / 3 # RGB Promedio
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

# Retorna el tipo de estado de la ficha, segun el color del centro de su delimitacion
def getPoints(img, w, h):
    # Sacamos la mitad de los cuadros
    ySpace = math.trunc(w / 7) # n
    yCenter = math.trunc(ySpace / 2) # m
    xSpace = math.trunc(h / 6) 
    xCenter = math.trunc(xSpace / 2)
    # Matriz de puntos de los centros
    puntos = []
    for i in range(1, 15, 2):
        p = []
        for j in range(1, 13, 2):
            p.append((yCenter * i, xCenter * j))
        puntos.append(p)
    return puntos

# Dibuja una linea sobre los centros de la cuadricula horizontalmente
def drawPoints(img, w, h, matriz):
    draw = ImageDraw.Draw(img)
    for i in range(0, len(matriz)):
        draw.line(matriz[i],  (255, 215, 0, 255))
    img.save("editadas/centros.jpg")

# Vuelve la foto blanco y negro sacando los promedios de RGB
def binarizarImg(img):
    imgB, imgG, imgR = cv2.split(img) # Blue, Green, Red
    retval, threshold = cv2.threshold(imgR, 120, 255, cv2.THRESH_BINARY_INV)
    return threshold

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

# Saca los estados de la imagen
def getStates(img, puntos):
    matrix = []
    for i in range(0, len(puntos)):
        aux = []        
        flagSpace = False
        for j in reversed(range(0, len(puntos[0]))):
            c = img.getpixel(puntos[i][j])
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
def testCV2(img_color): # frame = img
    cv2.imshow('Original', img_color)
    #colores
    img_r=img_color[:,:,2]
    img_g=img_color[:,:,1]
    img_b=img_color[:,:,0]
    rojo=restarImagen(img_r, img_g)
    # cv2.imshow('Rojo', img_r)
    # cv2.imshow('Verde', img_g)
    # cv2.imshow('Azul', img_b)
    cv2.imshow('Final', rojo)
    cv2.waitKey(0)

# Restar dos colores en una img
def restarImagen(img1, img2):
    return cv2.subtract(img1, img2)

# Funcion principal que ejecuta todo
def ejecutar(path, path2):
    try: # Cargar la imagen
        img = cv2.imread(path)
        h, w, c = img.shape # Sacar tamanno a la imagen (ignorar c)
        imgB = binarizarImg(img) # Binarizar imagen
        # Delimitar el tablero
        (yMin, yMax) = delimitarAlto(imgB, w, h) # Delimitar el tablero verticalmente
        imgB = cortarImg(imgB, 0, yMin, w-1, yMax)
        h, w = imgB.shape # Esta foto ya no contiene canales
        (xMin, xMax) = delimitarAncho(imgB, w, h) # Delimitar el tablero horizontalmente
        # Cortar foto
        imgC = cortarImg(img, xMin, yMin, xMax, yMax)   
        # Dibuja la cuadricula
        h, w, c = imgC.shape
        imgCuad = dibujarCuadricula(imgC, w, h)
        cv2.imwrite(path2, imgCuad)
        # Saca los centros la cuadricula
        centros = getPoints(imgC, w, h)
        # Sacar los estados de la cuadricula
        matrix = getStates(imgC, centros)
        return matrix
    except IOError:
        print "No se encontro la imagen"