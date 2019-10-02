from PIL import Image
import math
import PIL

# Espacio: 0
# Fichas blancas (IA): 1
# Fichas Negras (Enemigo): -1

def isBlack(r, g, b):
    if r < 110 and r > 15 and g < 80 and g > 40 and b < 110 and b > 60:
        return True
    return False

def isWhite(r, g, b):
    if r > 140 and g > 220 and b > 220:
        return True
    return False

def isRed(r, g, b):
    if r < 200 and r >= 90 and g < 110 and g > 50 and b < 110 and b > 45:
        return True
    return False

def isFondo(r, g, b):
    if r > 25 and r < 50 and g > 145 and g < 215 and b > 128 and b < 195:
        return True
    return False

# Retorna la posicion del pixel inicial y final en donde se encuentra el tablero (Verticalmente)
def delimitarAlto(img, w, h):
    posIni = -1
    posFin = -1
    middle = math.trunc(w/2)
    cont = 0 # 3 pixeles consecutivos seran la sennal
    i = 0
    stop = False # Indicacion de parada
    while (i<h and (not stop)): # Buscar la posicion inicial
        c = img.getpixel((middle, i))
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
    while (not stop): # Buscar la posicion final
        c = img.getpixel((middle, i))
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
    while (i<w and (not stop)): # Buscar la posicion inicial
        c = img.getpixel((i, middle))
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
    while (not stop): # Buscar la posicion final
        c = img.getpixel((i, middle))
        if c == 0: # Si es negro
            cont += 1
        elif c == 255 and cont > 0: # Si se danna la fila consecutiva
            cont = 0
        if cont == 3: # Si existen 3 negros seguidos
            posFin = i
            stop = True
        i -= 1 # Avanzar en el ciclo
    return(posIni, posFin)

def getStates(img2, L):
    #Variables necesarias
    countR = 0
    countB = 0
    countW = 0
    countE = 0
    flagE = False
    flagW = False
    flagB = False
    flagR = False
    flagF = False
    v = []
    i = 100
    k = 0
    #Recorro la imagen
    while i < 640:
        (r,g,b) = img2.getpixel((i, L))
        #Determino si ya estoy en la parte roja del tablero
        if flagR is not True:
            if isRed(r,g,b):
                countR = countR + 1
            if countR > 5:
                countR = 0
                flagR = True
        else:
            if flagF is not True:
                if isRed(r,g,b) is not True:
                    if isFondo(r,g,b):
                        countE = countE + 1
                    elif isBlack(r,g,b):
                        countB = countB + 1
                    elif isWhite(r,g,b):
                        countW = countW + 1 
                    if countE > 5:
                        flagE = True
                        flagF = True
                    elif countB > 5:
                        flagB = True
                        flagF = True
                    elif countW > 5:
                        flagW = True
                        flagF = True
            else:
                if k <= 6:
                    if flagB:
                        v.append(-1)
                        flagB = False
                        flagF = False
                        flagR = False
                        countB = 0
                        k = k + 1
                    elif flagW:
                        v.append(1)
                        flagW = False
                        flagF = False
                        flagR = False
                        countW = 0
                        k = k + 1
                    elif flagE:
                        v.append(0)
                        flagE = False
                        flagF = False
                        flagR = False
                        countE = 0
                        k = k + 1
        i = i + 1
    return v
    
def createMatrix(V1, V2, V3, V4, V5, V6):
    mat = [V1, V2, V3, V4, V5, V6]
    #print len(mat)
    return mat

def validarMatrix(matrix):
    for i in range(0,len(matrix) - 1):
        if len(matrix[i]) < 7:
            return False
    return matrix

# Vuelve la foto blanco y negro sacando los promedios de RGB
def binarizarImg(img):
    img = img.convert("L") # Convierte la foto a blanco y negro
    threshold = 110 # Cualquier valor por debajo de este numero sera negro
    img = img.point(lambda p: p > threshold and 255) # Binarizar
    #img.save("editadas/binarizada.jpg") # Guarda la foto en la carpeta
    return img

# Genera una subimagen basado en ciertas posiciones
def cortarImg(img, xMin, yMin, xMax, yMax):
    img = img.crop((xMin, yMin, xMax, yMax))
    #img.save("editadas/cortada.jpg")
    return img

def dibujarCuadricula(img, w, h):
    # Dibujar rayas Verticales
    space = math.trunc(w/7)
    for i in range(1, 7): # Generar 6 lineas
        for y in range(0, h): # Toda la profundidad
            img.putpixel((space*i, y), (255, 215, 0, 255)) # Lineas en (RGBA)
    # Dibujar rayas Horizontales
    space = math.trunc(h/6)
    for i in range(1, 6): # Generar 5 lineas
        for x in range(0, w): # Todo el ancho
            img.putpixel((x, space*i), (255, 215, 0, 255))
    img.save("editadas/cuadricula.jpg")

def ejecutar(path):
    # Cargar la imagen
    try:  
        img = Image.open(path)
    except IOError:
        print "No se encontro la imagen"
    # Si la foto cargo exitosamente
    (w, h) = img.size # Sacar tamanno a la imagen
    imgB = binarizarImg(img) # Binarizar imagen
    # Delimitar el tablero
    (yMin, yMax) = delimitarAlto(imgB, w, h) # Delimitar el tablero verticalmente
    (xMin, xMax) = delimitarAncho(imgB, w, h) # Delimitar el tablero horizontalmente
    # Cortar foto
    imgC = cortarImg(img, xMin,yMin, xMax, yMax)
    # Dibuja la cuadricula
    (w, h) = imgC.size # Sacar tamanno a la imagen
    dibujarCuadricula(imgC, w, h)

    return True