import getImagePhoto as take
#import convertirImgToMatrix as conv


if __name__ == '__main__':
    IP = "nao.local"  # Replace here with your NaoQi's IP address.
    PORT = 9559
    #while True:
    path = take.sinNAO(IP, PORT)
    
    print path

    
    
