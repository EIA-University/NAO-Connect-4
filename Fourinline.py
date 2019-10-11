import pydot
try: 
    import queue
except ImportError:
    import Queue as queue
import numpy as np
import copy

import convertirImgToMatrix as conv

# Basic class for every node in the search tree
class Node(object):
  def __init__(self, state,value,operators, operator=None, parent=None,objective=None):
    self.state= state
    self.value = value
    self.children = []
    self.parent=parent
    self.operator=operator
    self.operators=operators
    self.objective=objective
    self.level=0
 
  def add_child(self, value, state, operator):
    node=type(self)(value=value, state=state, operator=operator,parent=self, operators=self.operators)
    node.level=node.parent.level+1
    self.children.append(node)
    return node

  # Return a list of states (And None if is the case) where the node father apply every operator
  def getchildrens(self):
    listChildren = []
    for k, op in enumerate(self.operators):
      state = self.getState(k)
      if state == None:
        listChildren.append(None)
      else: 
        if not self.repeatStatePath(state[0]):
          listChildren.append(state)
        else: 
          listChildren.append(None)
    return listChildren

  def getState(self, index):
    pass

  # Check if one state is already in the search tree
  def repeatStatePath(self, state):
      n = self
      while n is not None and n.state is not state:
          n = n.parent
      return n is not None
    
  def heuristic(self):
    return 0

# More specific class for the board
class Board(Node):
  # mark = 1 -> IA
  # mark = -1 -> Enemigo
  # i : Last move row
  # j : Last move column
  # h : Heuristic's state
  
  def __init__(self, mark, i, j, **kwargs):
    self.mark = mark
    self.i = i
    self.j = j
    self.h = None
    super(Board, self).__init__(**kwargs)

  def add_child(self, mark, i, j, value, state, operator):
    node=type(self)(mark=mark, i=i, j=j, value=value, state=state, operator=operator,parent=self, operators=self.operators)
    node.level=node.parent.level+1
    self.children.append(node)
    return node

  # Apply the 7 operators (Play in one column)
  def getState(self, i):
    state = copy.deepcopy(self.state)
    nextState = copy.deepcopy(state)
    mark = self.mark*-1 # The children's states has the opposite mark
    if (state[0][i] == 0): # If its possible to play
      for k in reversed(range(0,6)):
        if (state[k][i] == 0):
          nextState[k][i] = mark
          return (nextState, k, i)
    else:
      return None

  # Return a vector of heuristic values, the higher is the best move
  def chooseBestMove(self):
    heuristicValues = []
    for i, child in enumerate(self.children):
      h = child.heuristic()
      heuristicValues.append(h)
    if(len(heuristicValues)==0):
      return heuristicValues
    (iMax, cont, maxHeuristic) = self.findMax(heuristicValues)
    if maxHeuristic==50 or maxHeuristic==40 or maxHeuristic==-1: # Cases where is not necessary continue evaluating
      return heuristicValues
    # Best Move
    if cont < 2: # Step 1: The move that block more enemy moves
      return heuristicValues
    # If there a heuristic draw
    # Step 2: The move that generate more possible moves in the next turn
    for i in range(iMax, len(heuristicValues)):
      if heuristicValues[i] == maxHeuristic:
        h = self.children[i].getHorizontalState(self.children[i].i)
        v = self.children[i].getVerticalState(self.children[i].j)
        (d1, d2, posD1, posD2) = self.children[i].getDiagonalState(self.children[i].i, self.children[i].j)
        heuristicValues[i] += self.countOpenMovesVer(v, self.children[i].i, self.children[i].mark) + self.countOpenMovesHorDia(h, self.children[i].j, self.children[i].mark) + self.countOpenMovesHorDia(d1, posD1, self.children[i].mark) + self.countOpenMovesHorDia(d2, posD2, self.children[i].mark)
    (iMax, cont, maxHeuristic) = self.findMax(heuristicValues)
    if cont < 2:
      return heuristicValues
    # If there a heuristic draw
    # Step 3: The move that generate less possible moves for the enemy in the next turn
    for i in range(iMax, len(heuristicValues)):
      if heuristicValues[i] == maxHeuristic:
        if(self.children[i].i == 0): # If we put in the first row we do not generate moves
          heuristicValues[i] += 15
        if(self.children[i].i >0): # If the enemy put his piece above us
          h = self.children[i].getHorizontalState(self.children[i].i-1)
          v = self.children[i].getVerticalState(self.children[i].j)
          (d1, d2, posD1, posD2) = self.children[i].getDiagonalState(self.children[i].i-1, self.children[i].j)
          heuristicValues[i] += 15 - (self.countOpenMovesVer(v, self.children[i].i, -self.children[i].mark) + self.countOpenMovesHorDia(h, self.children[i].j, self.children[i].mark*-1) + self.countOpenMovesHorDia(d1, posD1, self.children[i].mark*-1) + self.countOpenMovesHorDia(d2, posD2, self.children[i].mark*-1))
    (iMax, cont, maxHeuristic) = self.findMax(heuristicValues)
    if cont < 2:
      return heuristicValues
    # If there a heuristic draw
    # Step 4: Return the first move that not block a win move
    for i in range(iMax, len(heuristicValues)):
      if heuristicValues[i] == maxHeuristic: 
        if(self.children[i].i == 0):
          return heuristicValues
        h = self.children[i].getHorizontalState(self.children[i].i-1)
        v = self.children[i].getVerticalState(self.children[i].j)
        (d1, d2, posD1, posD2) = self.children[i].getDiagonalState(self.children[i].i-1, self.children[i].j)
        m = self.children[i].mark
        if not (self.checkNotAllowMoves(h,self.children[i].j, m) or self.checkNotAllowMoves(v,self.children[i].i-1, m) or self.checkNotAllowMoves(d1,posD1, m) or self.checkNotAllowMoves(d2,posD2, m)):
          return heuristicValues
    # If all the best moves block a win move we need to analyse if is there a better move to make in that case
    max2 = -1 # The second max value of heuristicValues
    iMax2 = -1 # The first move whit h != maxHeuristic
    for i in range(0, len(heuristicValues)):
      if heuristicValues[i]>max2 and heuristicValues[i]<maxHeuristic:
        max2 = heuristicValues[i]
        iMax2 = i
    if max2 != -1:
      heuristicValues[iMax2] = maxHeuristic + 5
      return heuristicValues
    # Operator order
    return heuristicValues

  # Return a value for the first steps of the heuristic process
  def heuristic(self):  
    if self.isWinner():
      return 50
    if self.block():
      return 40
    if(self.i >0): # Mark the not allowed moves
      h = self.getHorizontalState(self.i-1)
      v = self.getVerticalState(self.j)
      (d1, d2, posD1, posD2) = self.getDiagonalState(self.i-1, self.j)
      m = -self.mark
      if self.checkNotAllowMoves(h,self.j, m) or self.checkNotAllowMoves(v,self.i-1, m) or self.checkNotAllowMoves(d1,posD1, m) or self.checkNotAllowMoves(d2,posD2, m):
        return -1
    # How many moves we block to the enemy
    h = self.getHorizontalState(self.i)
    v = self.getVerticalState(self.j)
    (d1, d2, posD1, posD2) = self.getDiagonalState(self.i, self.j)
    return self.countBlockEnemyMovesHorDia(h, self.j) + self.countBlockEnemyMovesHorDia(d1, posD1) +  self.countBlockEnemyMovesHorDia(d2, posD2) + self.countBlockEnemyMovesVer(v, self.i)

  def isWinner(self):
    h = self.getHorizontalState(self.i)
    v = self.getVerticalState(self.j)
    d1 = self.getDiagonalState(self.i, self.j)[0]
    d2 = self.getDiagonalState(self.i, self.j)[1]
    if self.checkWin(h, self.mark) or self.checkWin(v, self.mark) or self.checkWin(d1, self.mark) or self.checkWin(d2, self.mark):
      return True
    return False

  # Do we block a move?
  def block(self):
    h = self.getHorizontalState(self.i)
    v = self.getVerticalState(self.j)
    (d1, d2, posD1, posD2) = self.getDiagonalState(self.i, self.j)
    if self.checkBlock(h, self.j) or self.checkBlock(v, self.i) or self.checkBlock(d1, posD1) or self.checkBlock(d2, posD2):
      return True
    return False

  # ----------------------------------

  # Return the max value in a vector, the number of items that hold the max value and the first item that hold the value
  def findMax(self, vec):
    cont = 0
    iMax = -1
    maxV = max(vec)
    for i in range(0, len(vec)):
      if vec[i] == maxV:
        cont += 1
        if iMax == -1:
          iMax = i
    return (iMax, cont, maxV)
  
  def getHorizontalState(self, i):
    horizontal = []
    for j in range(0,len(self.state[0])):
      horizontal.append(self.state[i][j])
    return horizontal

  def getVerticalState(self, j):
    vertical = []
    for i in range(0,len(self.state)):
      vertical.append(self.state[i][j])
    return vertical

  # Return the 2 diagonals that contains the (i,j) move 
  def getDiagonalState(self, i, j):
    i2 = i
    j2 = j
    diagonal1 = []
    diagonal2 = []
    # The diagonal 1
    while i2<len(self.state)-1 and j2>0:
      i2+=1
      j2-=1
    posD1 = i2-i # This number is tell us the new position of the move in the new array
    while i2>=0 and j2<len(self.state[0]):
      diagonal1.append(self.state[i2][j2])
      i2-=1
      j2+=1
    i2 = i
    j2 = j
    # The diagonal 2
    while i2>0 and j2>0:
      i2-=1
      j2-=1
    posD2 = j-j2 # This number is tell us the new position of the move in the new array
    while i2<len(self.state) and j2<len(self.state[0]):
      diagonal2.append(self.state[i2][j2])
      i2+=1
      j2+=1
    return (diagonal1, diagonal2, posD1, posD2)
  .
  def checkWin(self, vec, mark):
    if len(vec) < 4:
      return False
    else:
      val = 0
      for i in range(0, len(vec)):
        if vec[i]==mark:
          val+=1
        else:
          val = 0
        if val==4:
          return True
      return False
  
  def checkBlock(self, vec, pos):
    initPos = max(0,pos-3)
    finalPos = initPos+3
    while (initPos<=pos and finalPos<len(vec)):
      val = 0
      for i in range(initPos, finalPos+1):
        if i is not pos:
          if vec[i]==-self.mark:
            val+=1
      if val==3:
        return True
      initPos+=1
      finalPos+=1
    return False

  # In a horizontal or diagonal array, count how many moves we block to the enemy
  def countBlockEnemyMovesHorDia(self, vec, pos):
    initPos = max(0,pos-3)
    finalPos = initPos+3
    moves=0
    while (initPos<=pos and finalPos<len(vec)):
      flag=False
      val = 0
      for i in range(initPos, finalPos+1):
        if i is not pos:
          if vec[i]==-self.mark:
            val+=1
          if vec[i]==self.mark:
            flag=True
      if flag is not True and val>0:
        moves+=1
      initPos+=1
      finalPos+=1
    return moves

  # In a vertical array, count how many moves we block to the enemy
  def countBlockEnemyMovesVer(self, vec, pos):
    if(pos == len(vec)-1):
      return 0
    if(vec[pos+1] == -self.mark):
      if(pos >=2):
        return 1
      if pos == 1 and vec[pos+1] == -self.mark and vec[pos+2] == -self.mark:
        return 1
      if pos == 0 and vec[pos+1] == -self.mark and vec[pos+2] == -self.mark and vec[pos+3] == -self.mark:
        return 1  
    return 0

  # Count if is possibly win with a vertical line
  def countOpenMovesVer(self, vec, pos, mark):
    i = 0
    cont = 0
    while i<len(vec) and vec[i] != -mark:
      cont+=1
      if cont>3:
        return 1
      i+=1
    return 0

  # Count how many possible lines we have in a horizontal or diagonal vector
  def countOpenMovesHorDia(self, vec, pos, mark):
    initPos = max(0,pos-3)
    finalPos = initPos+3
    moves = 0
    while (initPos<=pos and finalPos<len(vec)):
      val = 0
      for i in range(initPos, finalPos+1):
        if i is not pos:
          if vec[i]==0 or vec[i]==mark:
            val+=1
      if val == 3:
        moves+=1
      initPos+=1
      finalPos+=1
    return moves

  # Check if one move blocks a win move
  def checkNotAllowMoves(self, vec, pos, mark):
    vecCopy = copy.deepcopy(vec)    
    vecCopy[pos] = mark
    if self.checkWin(vecCopy, mark):
      return True
    return False

# Alpha beta pruning to get the best move
# Return the heuristic value and the best move
def alpha_beta(node, depth, a, b, turn):
  # turn: true - MAX
  # turn: false - MIN
  if (depth == 0):
    return (node.h, node.operator)
  # Add childs
  children=node.getchildrens()
  for k in range(0, len(children)):
    if children[k] is not None:
      (child, i, j) = children[k]
      newChild = node.add_child(-node.mark, i=i, j=j, value=node.value+'-'+str(k), state=child, operator=k)
  # Put the respective heuristic values
  heuristicValues = node.chooseBestMove()
  for i in range(0, len(heuristicValues)):
    aux = heuristicValues[i]
    node.children[i].h = aux
  if turn: # Max level
    value = float('-inf')
    operator = None
    for i, n in enumerate(node.children):
      (val, op) = alpha_beta(n, depth-1, a, b, not turn)
      if (val > value):
        value = val
        operator = n.operator
      a = max(a, value)
      if (a>=b):
        break
    return (value, operator)
  else: # Min level
    value = float('inf')
    operator = None
    for i, n in enumerate(node.children):
      (val, op) = alpha_beta(n, depth-1, a, b, not turn)
      if (val < value):
        operator = n.operator
        value = val
      b = min(b, value)
      if (a>=b):
        break 
    return (value, operator)

# Nao will call this method
def play(initState):
  n = -1 # Enemy mark
  b = 1 # AI mark
  operators = [0,1,2,3,4,5,6]
  m = n
  br = Board(mark=m, i=0, j=0, state=initState,value="1",operators=operators, operator=None, parent=None,objective=None)
  return alpha_beta(br, 1, float('-inf'), float('inf'), True)