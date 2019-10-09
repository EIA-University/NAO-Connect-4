# Import the necessary libraries
import math
import numpy as np
import cv2
import Queue

""" 
The game works with the follow conventions: 
Space: 0
White pieces (AI): 1
BLack pieces (Enemy): -1
 """

# Return the image with the red specter binarizate
def binarizateImg(img):
    imgB, imgG, imgR = cv2.split(img) # Blue, Green, Red
    _,threshold = cv2.threshold(imgR, 120, 255, cv2.THRESH_BINARY_INV)
    return threshold

# Return two positions with the min and max height that contain the board
def getNewHeight(img, w, h):
    initPos = -1
    finalPos = -1
    middle = math.trunc(w / 2)
    cont = 0 # 3 consecutive pixels will make a call
    i = 0
    stop = False # Indicate when to stop
    while (i < h and (not stop)): # Find the initial position
        c = img[i, middle]
        if c == 0: # if is black
            cont += 1
        elif c == 255 and cont > 0: # We need a consecutive line
            cont = 0
        if cont == 3: # If the cont met the goal
            initPos = i
            stop = True
        i += 1
    cont = 0
    i = h-1
    stop = False
    while ( i > 0 and (not stop)): # Find the final position
        c = img[i, middle]
        if c == 0:
            cont += 1
        elif c == 255 and cont > 0:
            cont = 0
        if cont == 3:
            finalPos = i
            stop = True
        i -= 1
    return(initPos, finalPos)

# Return two positions with the min and max width that contain the board
def getNewWidth(img, w, h):
    initPos = -1
    finalPos = -1
    middle = math.trunc(h/2)
    cont = 0 # 3 consecutive pixels will make a call
    i = 0
    stop = False # Indicate when to stop
    while (i < w and (not stop)): # Find the initial position
        c = img[middle, i]
        if c == 0: # Si es negro
            cont += 1
        elif c == 255 and cont > 0: # We need a consecutive line
            cont = 0
        if cont == 3:# If the cont met the goal
            initPos = i
            stop = True
        i += 1
    cont = 0
    i = w-1
    stop = False
    while (i > 0 and (not stop)): # Find the final position
        c = img[middle, i]
        if c == 0:
            cont += 1
        elif c == 255 and cont > 0:
            cont = 0
        if cont == 3:
            finalPos = i
            stop = True
        i -= 1
    return(initPos, finalPos)

# Genera a sub image
def cortarImg(img, xMin, yMin, xMax, yMax):
    crop_img = img[yMin:yMax, xMin:xMax]
    return crop_img

# Based on two images and one position, return the color of the position 
def getColor(i, j, imgWhitePieces, imgSpaceHoles):
    white = imgWhitePieces[i, j]
    space = imgSpaceHoles[i, j]
    if space == 255:
        return 0
    elif white == 255:
        return 1
    else:
        return -1

# Return the (x,y) coordinates of the centroids
def getCentroids(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) # Conver the img to SHV
    hue, saturation, value = cv2.split(img)
    _, ht = cv2.threshold(hue, 50, 255, cv2.THRESH_BINARY) # Hue Threshold
    _, st = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY) # Saturation Threshold
    _, vt = cv2.threshold(value, 0, 255, cv2.THRESH_BINARY) # Value Threshold
    # Combine the thresholds
    finalImg = cv2.bitwise_and(ht, st)
    finalImg = cv2.bitwise_and(finalImg, vt)
    # Invert the image. OpenCV needs white areas to find centroids
    finalImg = cv2.bitwise_not(finalImg)
    # Makes the image softer
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(finalImg, cv2.MORPH_OPEN, kernel)
    contorn, _ = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    points = [] # Save x,y and area  
    for c in contorn:
        m = cv2.moments(c)
        if int(m["m00"])!=0:
            cx = int(m["m10"]/m["m00"])
            cy = int(m["m01"]/m["m00"])
            area = cv2.contourArea(c)
            points.append((cx, cy, area))
    return points   

# Return the points that we need based on the average
def getpoints(centroids):
    q = Queue.PriorityQueue()
    areaPromedio = 1652
    for i in range(0, len(centroids)):
        a = centroids[i][2]
        q.put((abs(areaPromedio-a), centroids[i]))
    # Get the 42 points
    cont = 0
    points = []
    while not q.empty() and cont<42:
        points.append(q.get()[1])
        cont += 1
    return points

# Sort the points in a bidimensional array
def sortPoints(points):
    queueY = Queue.PriorityQueue()
    for i in range(0, len(points)):
        y = points[i][1]
        queueY.put((y, points[i]))
    matrix = []
    for i in range(0, 6):
        queueX = Queue.PriorityQueue()
        for j in range(0, 7):
            p = queueY.get()[1]
            queueX.put((p[0], p))
        row = []
        for j in range(0, 7):
            row.append(queueX.get()[1])
        matrix.append(row)
    return matrix

# Return a binarizate image with all the white pieces
def getWhitePieces(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hue, saturation, value = cv2.split(img)
    _, ht = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY)
    _, st = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY)
    _, vt = cv2.threshold(value, 230, 255, cv2.THRESH_BINARY)
    finalImg = cv2.bitwise_and(ht, st)
    finalImg = cv2.bitwise_and(finalImg, vt)
    kernel = np.ones((5,5), np.uint8)
    finalImg = cv2.morphologyEx(finalImg, cv2.MORPH_OPEN, kernel)
    return finalImg

# Return a binarizate image with only the spaces holes on the board
def getHoles(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) # Convertir imagen a HSV
    hue, saturation, value = cv2.split(img) # Extraer valores de img
    _, ht = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY) # Hue Threshold
    _, st = cv2.threshold(saturation, 190, 255, cv2.THRESH_BINARY) # Saturation Threshold
    _, vt = cv2.threshold(value, 0, 255, cv2.THRESH_BINARY) # Value Threshold
    # Combinar los thresholds
    finalImg = cv2.bitwise_and(ht, st)
    finalImg = cv2.bitwise_and(finalImg, vt)
    # Suavizar la imagen
    kernel = np.ones((5,5), np.uint8)
    finalImg = cv2.morphologyEx(finalImg, cv2.MORPH_OPEN, kernel)
    return finalImg

# Get the state based on the original image and the points matrix
def getState(img, points):
    imgWhitePieces = getWhitePieces(img)
    imgSpaceHoles = getHoles(img)
    # Define the initial state
    matriz=[[0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0]]
    for j in range(0, len(matriz[0])):
        i = len(matriz)-1
        flag = False
        while i>=0 and (not flag):
            p = points[i][j]
            index = getColor(p[1], p[0], imgWhitePieces, imgSpaceHoles)
            if index == -1:
                matriz[i][j] = -1
            elif index == 1:
                matriz[i][j] = 1
            else:
                flag = True
            i -= 1
    return matriz

# Main function
def ejecutar(path):
    try:
        img = cv2.imread(path)
        h, w, _ = img.shape # Get width and height
        imgB = binarizateImg(img)
        # Crop board image
        (yMin, yMax) = getNewHeight(imgB, w, h)
        imgB = cortarImg(imgB, 0, yMin, w-1, yMax)
        h, w = imgB.shape
        (xMin, xMax) = getNewWidth(imgB, w, h)
        imgC = cortarImg(img, xMin, yMin, xMax, yMax)
        # Get the state
        centroids = getCentroids(imgC)
        points = getpoints(centroids)
        points = sortPoints(points)
        matriz = getState(imgC, points)
        # Print the state in every move
        print ""
        for i in range(0, len(matriz)):
            print matriz[i]
        return matriz
    except IOError:
        print "Cannot open the file"