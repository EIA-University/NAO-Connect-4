from PIL import Image
from PIL import ImageEnhance
#Imagen de 640x480
#Metodos para comprobar colores
#0 Espacio, -1 B, 1 W
def isBlack(r, g, b):
    if r < 110 and r > 15 and g < 80 and g > 40 and b < 110 and b > 60:
        return True
    return False

def isWhite(r, g, b):
    if r > 140 and g > 220 and b > 220:
        return True
    return False

def isRed(r, g, b):
    if r < 200 and r > 95 and g < 110 and g > 50 and b < 110 and b > 45:
        return True
    return False

def isFondo(r, g, b):
    if r > 25 and r < 50 and g > 145 and g < 215 and b > 128 and b < 195:
        return True
    return False

def sacarAncho(img):
    #Sacar el ancho de la imagen
    pixini = -1
    pixfin = -1

    for i in range(0, 480):
        (r,g,b) = img.getpixel((330, i))
        if isRed(r, g, b) and pixini == -1:
            pixini = i

        (r,g,b) = img.getpixel((330, 479 - i))
        if isRed(r, g, b) and pixfin == -1:
            pixfin = 479 - i
    return(pixini,pixfin)

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
    i = 0
    k = 0
    #Recorro la imagen
    while i < 640:
        (r,g,b) = img2.getpixel((i, L))
        #Determino si ya estoy en la parte roja del tablero
        if flagR is not True:
            if isRed(r,g,b):
                countR = countR + 1
            if countR > 10:
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
                    if countE > 10:
                        flagE = True
                        flagF = True
                    elif countB > 10:
                        flagB = True
                        flagF = True
                    elif countW > 10:
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
                    if flagW:
                        v.append(1)
                        flagW = False
                        flagF = False
                        flagR = False
                        countW = 0
                        k = k + 1
                    if flagE:
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
    print len(mat)
    return mat

def validarMatrix(matrix):
    for i in range(0,len(matrix) - 1):
        if len(matrix[i]) < 7:
            return False
    return matrix

def ejecutar(path):
    #Cargar la imagen y resaltar colores
    try:  
        img = Image.open(path)  
        #converter = ImageEnhance.Color(img)
        #img2 = converter.enhance(3)
        #img2.save("saturadas/lleno.png", "PNG")
    except IOError:
        print "No se encontro la imagen"

    (pixin, pixfn) =  sacarAncho(img)
    rangoT = pixfn - pixin
    # print rangoT
    # print "\n"
    # print pixin, pixfn
    #Saco las lineas del tablero
    L1 = pixin + (rangoT * 0.145)
    L2 = L1 + (rangoT * 0.155)
    L3 = L2 + (rangoT * 0.155)
    L4 = L3 + (rangoT * 0.155)
    L5 = L4 + (rangoT * 0.155)
    L6 = L5 + (rangoT * 0.155)

    L1 = int(L1 + 1)
    L2 = int(L2 + 1)
    L3 = int(L3 + 1)
    L4 = int(L4 + 1)
    L5 = int(L5 + 1)
    L6 = int(L6 + 1)
    #print L1, L2, L3, L4, L5, L6
    #Vectores para sacar los estadoss

    V1 = getStates(img, L1)
    V2 = getStates(img, L2)
    V3 = getStates(img, L3)
    V4 = getStates(img, L4)
    V5 = getStates(img, L5)
    V6 = getStates(img, L6)

    matrix = createMatrix(V1, V2, V3, V4, V5, V6)

    matrix = validarMatrix(matrix)

    return matrix

    