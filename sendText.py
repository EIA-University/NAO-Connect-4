from naoqi import ALProxy


def talk(mensaje, IP, PORT):
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    # Example: Sends a string to the text-to-speech module
    tts.say(mensaje)

def talkSinNAO(mensaje, IP, PORT):
    print mensaje