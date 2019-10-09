# This is a file to test de geme's flow
import Fourinline as game
 
if __name__ == '__main__':
    state = [[-1,-1,1,1,1,-1,0],
            [1,1,-1,-1,1,1,0],
            [-1,-1,1,1,1,-1,0],
            [1,1,1,-1,-1,-1,0],
            [-1,-1,-1,1,1,-1,0],
            [-1,1,1,-1,-1,1,-1]]
    res = game.play(state)
    print res