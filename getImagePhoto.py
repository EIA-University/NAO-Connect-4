# Get an image from NAO. Display it and save it.

import sys
import time
import random
import os, random 
from naoqi import ALProxy
from PIL import Image

def showNaoImage(IP, PORT):
  """
  First get an image from Nao, then show it on the screen with PIL.
  """

  camProxy = ALProxy("ALVideoDevice", IP, PORT)
  resolution = 2    # VGA
  colorSpace = 11   # RGB

  videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

  #t0 = time.time()

  # Get a camera image.
  # image[6] contains the image data passed as an array of ASCII chars.
  naoImage = camProxy.getImageRemote(videoClient)

  #t1 = time.time()

  # Time the image transfer.
  #print "acquisition delay ", t1 - t0

  camProxy.unsubscribe(videoClient)

  # Now we work with the image returned and save it as a PNG  using ImageDraw
  # package.

  # Get the image size and pixel array.
  imageWidth = naoImage[0]
  imageHeight = naoImage[1]
  array = naoImage[6]

  # Create a PIL Image from our pixel array.
  im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

  name = ""
  i = 0
  while i < 10:
    num = random.randint(97,122)
    name = name + chr(num)
    i += 1
  name = name + ".png"
  path = "images/" + name
  # Save the image.
  im.save(path, "PNG")

  #im.show()
  return path

def sinNAO(IP, PORT):
  file1 = random.choice(os.listdir("images/"))
  path = "images/" + file1
  return  path