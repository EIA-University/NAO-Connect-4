import Fourinline as games


 
if __name__ == '__main__':
    state = [[-1,-1,1,1,1,-1,0],
            [1,1,-1,-1,1,1,0],
            [-1,-1,1,1,1,-1,0],
            [1,1,1,-1,-1,-1,0],
            [-1,-1,-1,1,1,-1,0],
            [-1,1,1,-1,-1,1,-1]]

    hola = games.play(state)

    print hola