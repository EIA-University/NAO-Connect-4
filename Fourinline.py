# Importar librerias neecesarias
import pydot
try: 
    import queue
except ImportError:
    import Queue as queue
import numpy as np
import copy

import convertirImgToMatrix as conv

# Clase basica para el tablero
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
  
  def add_node_child(self, node):
    node.level=node.parent.level+1
    self.children.append(node)    
    return node

  def getchildrens(self):
    listChildren = []
    for k, op in enumerate(self.operators):
      state = self.getState(k) # State, Pos i, Pos j
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
  
  def __eq__(self, other):
    return self.state == other.state
 
  def __lt__(self, other):
    return self.f() < other.f()
  
  def repeatStatePath(self, state):
      n = self
      while n is not None and n.state is not state:
          n = n.parent
      return n is not None
    
  def pathObjective(self):
      n=self
      result=[]
      while n is not None:
          result.append(n)
          n=n.parent
      return result
    
  def printPath(self):
      stack=self.pathObjective()
      while len(stack)!=0:
          node=stack.pop()
          if node.operator is not None:
              print "f'operador:  {node.operators[node.operator]} \t estado: {node.state}'"
          else:
              print "f' {node.state}'"
  
  def heuristic(self):
    return 0
  
  def cost(self):
    return 1
  
  def f(self): 
    return self.cost()+self.heuristic()

# Clase tablero para el 4 en linea
class Board(Node):
  # mark = 1 -> IA
  # mark = -1 -> Enemigo
  # i : Fila donde se hizo la ultima jugada
  # j : Columna donde se hizo la ultima jugada
  # h : Heuristica del estado actual
  
  def __init__(self, mark, i, j, **kwargs):
    self.mark = mark
    self.i = i
    self.j = j
    self.h = None
    super(Board, self).__init__(**kwargs)

  # Modificacion necesaria al agregar nuevos atributos a la clase
  def add_child(self, mark, i, j, value, state, operator):
    node=type(self)(mark=mark, i=i, j=j, value=value, state=state, operator=operator,parent=self, operators=self.operators)
    node.level=node.parent.level+1
    self.children.append(node)
    return node

  # Aplicar alguno de los 7 operadores
  def getState(self, i):
    state = copy.deepcopy(self.state)
    nextState = copy.deepcopy(state)
    mark = self.mark*-1 # Los hijos de un estado poseen la marca contraria (Cambio de turno)
    if (state[0][i] == 0): # Si la columna no esta llena
      for k in reversed(range(0,6)):
        if (state[k][i] == 0):
          nextState[k][i] = mark
          return (nextState, k, i)
    else:
      return None

  # Define las condiciones para cuando un estado es final
  def isTerminal(self):
    if self.h == 50 or self.h == -50: # Si alguien gana
      return True
    # Si el tablero esta lleno
    for i in range(0, len(self.state)):
      if (self.state[0][i] == 0):
        return False # El tablero no esta lleno
    return True # Si el tablero esta lleno

  # Selecciona la mejor jugada
  def chooseBestMove(self):
    heuristicValues = [] # Valores heuristicos de los hijos
    for i, child in enumerate(self.children):
      h = child.heuristic()
      heuristicValues.append(h)
    if(len(heuristicValues)==0):
      return heuristicValues
    (iMax, cont, maxHeuristic) = self.findMax(heuristicValues)
    if maxHeuristic==50 or maxHeuristic==40 or maxHeuristic==-1:
      return heuristicValues
    # Best Move
    if cont < 2: # Paso 1: Retorna el movimiento que mas jugadas le bloquea al enemigo
      #print("El mov que mas bloquea: ", heuristicValues)
      return heuristicValues
    # Calcula heuristicas del paso 2 si existe mas de un hijo con maxHeuristic
    for i in range(iMax, len(heuristicValues)):
      if heuristicValues[i] == maxHeuristic:
        h = self.children[i].getHorizontalState(self.children[i].i)
        v = self.children[i].getVerticalState(self.children[i].j)
        (d1, d2, posD1, posD2) = self.children[i].getDiagonalState(self.children[i].i, self.children[i].j)
        heuristicValues[i] += self.countOpenMovesVer(v, self.children[i].i, self.children[i].mark) + self.countOpenMovesHorDia(h, self.children[i].j, self.children[i].mark) + self.countOpenMovesHorDia(d1, posD1, self.children[i].mark) + self.countOpenMovesHorDia(d2, posD2, self.children[i].mark)
    (iMax, cont, maxHeuristic) = self.findMax(heuristicValues)
    if cont < 2: # Paso 2: Retorna el movimiento que mas jugadas me genere
      #print("Mov que mas me genera: ", heuristicValues)
      return heuristicValues
    # Calcula heuristicas del paso 3 si existe mas de un hijo con maxHeuristic
    for i in range(iMax, len(heuristicValues)):
      if heuristicValues[i] == maxHeuristic:
        if(self.children[i].i == 0): # Si estamos en i=0 no le generamos jugadas al enemigo
          heuristicValues[i] += 15
        if(self.children[i].i >0): # Analizar los movimientos del enemigo si este pone encima
          h = self.children[i].getHorizontalState(self.children[i].i-1)
          v = self.children[i].getVerticalState(self.children[i].j)
          (d1, d2, posD1, posD2) = self.children[i].getDiagonalState(self.children[i].i-1, self.children[i].j)
          heuristicValues[i] += 15 - (self.countOpenMovesVer(v, self.children[i].i, -self.children[i].mark) + self.countOpenMovesHorDia(h, self.children[i].j, self.children[i].mark*-1) + self.countOpenMovesHorDia(d1, posD1, self.children[i].mark*-1) + self.countOpenMovesHorDia(d2, posD2, self.children[i].mark*-1))
    (iMax, cont, maxHeuristic) = self.findMax(heuristicValues)
    if cont < 2: # Paso 3: Retorna el movimiento que mmenos jugadas le genera al enemigo
      #print("Mov que menos le genera al otro: ", heuristicValues)
      return heuristicValues
    # Calcula el primero movimiento que no me bloquee una jugada ganadora
    for i in range(iMax, len(heuristicValues)):
      if heuristicValues[i] == maxHeuristic: 
        # Analizar los movimientos mios
        if(self.children[i].i == 0): # Paso 4: Si i=0 no me bloquea jugadas ganadoras
          #print("Mov que no me bloquea jugadas ganadoras: ", heuristicValues)
          return heuristicValues
        h = self.children[i].getHorizontalState(self.children[i].i-1)
        v = self.children[i].getVerticalState(self.children[i].j)
        (d1, d2, posD1, posD2) = self.children[i].getDiagonalState(self.children[i].i-1, self.children[i].j)
        m = self.children[i].mark
        # Paso 4: Primer movimiento que no bloquea jugadas ganadoras
        if not (self.checkNotAllowMoves(h,self.children[i].j, m) or self.checkNotAllowMoves(v,self.children[i].i-1, m) or self.checkNotAllowMoves(d1,posD1, m) or self.checkNotAllowMoves(d2,posD2, m)):
          #print("Mov que no me bloquea jugadas ganadoras: ", heuristicValues)
          return heuristicValues
    # Paso 5: El 2do mejor movimiento que no me bloquee jugadas ganadoras (Movimiento mas conveniente)
    max2 = -1 # La segunda mayor heuristica
    iMax2 = -1 # Indice del primer hijo con h != maxHeuristic
    for i in range(0, len(heuristicValues)):
      if heuristicValues[i]>max2 and heuristicValues[i]<maxHeuristic:
        max2 = heuristicValues[i]
        iMax2 = i
    if max2 != -1:
      #print("Cualquiera conveniente: ", heuristicValues)
      heuristicValues[iMax2] = maxHeuristic + 5 # Aumentar la heuristica del movimiento mas conveniente
      return heuristicValues
    # Orden de operadores
    #print("Cualquiera: ", heuristicValues)
    return heuristicValues

  # Retorna el valor heuristico de un estado hasta el 4 paso de la heuristica definida.
  def heuristic(self):  
    if self.isWinner():
      return 50
    if self.block():
      return 40
    # Empieza a anaizar cual es el mejor movimiento
    if(self.i >0): # Descartar los movimientos prohibidos.
      h = self.getHorizontalState(self.i-1)
      v = self.getVerticalState(self.j)
      (d1, d2, posD1, posD2) = self.getDiagonalState(self.i-1, self.j)
      m = -self.mark # Los movimientos prohibidos se analizan con la marca del enemigo
      if self.checkNotAllowMoves(h,self.j, m) or self.checkNotAllowMoves(v,self.i-1, m) or self.checkNotAllowMoves(d1,posD1, m) or self.checkNotAllowMoves(d2,posD2, m):
        return -1
    # Cuantos movimientos se le bloquean al enemigo
    h = self.getHorizontalState(self.i)
    v = self.getVerticalState(self.j)
    (d1, d2, posD1, posD2) = self.getDiagonalState(self.i, self.j)
    return self.countBlockEnemyMovesHorDia(h, self.j) + self.countBlockEnemyMovesHorDia(d1, posD1) +  self.countBlockEnemyMovesHorDia(d2, posD2) + self.countBlockEnemyMovesVer(v, self.i)

  # 1. Saber si gane
  def isWinner(self):
    h = self.getHorizontalState(self.i)
    v = self.getVerticalState(self.j)
    d1 = self.getDiagonalState(self.i, self.j)[0]
    d2 = self.getDiagonalState(self.i, self.j)[1]
    if self.checkWin(h, self.mark) or self.checkWin(v, self.mark) or self.checkWin(d1, self.mark) or self.checkWin(d2, self.mark):
      return True
    return False

  # 2. Saber si bloquee
  def block(self):
    h = self.getHorizontalState(self.i)
    v = self.getVerticalState(self.j)
    (d1, d2, posD1, posD2) = self.getDiagonalState(self.i, self.j)
    if self.checkBlock(h, self.j) or self.checkBlock(v, self.i) or self.checkBlock(d1, posD1) or self.checkBlock(d2, posD2):
      return True
    return False

  # ---Metodos auxiliares para las funciones heuristicas---

  def findMax(self, vec):
    cont = 0 # Cuenta cuantos hijos tienen la maxima heuristica
    iMax = -1 # Indice del primer hijo hijo con maxima heuristica
    maxV = max(vec)
    for i in range(0, len(vec)):
      if vec[i] == maxV:
        cont += 1
        if iMax == -1:
          iMax = i
    return (iMax, cont, maxV) # Primer hijo con maxima heuristica, numero de hijos con maxima heuristica, maxima heuristica
  
  # Retorna la horizontal dada la fila
  def getHorizontalState(self, i):
    horizontal = []
    for j in range(0,len(self.state[0])):
      horizontal.append(self.state[i][j])
    return horizontal

  # Retorna la vertical dada la columna
  def getVerticalState(self, j):
    vertical = []
    for i in range(0,len(self.state)):
      vertical.append(self.state[i][j])
    return vertical

  # Retorna dos vectores que representan las dos diagonales de una posicion dadas las coordenadas de este (i,j)
  def getDiagonalState(self, i, j):
    i2 = i
    j2 = j
    diagonal1 = []
    diagonal2 = []
    # Para sacar la diagonal1
    while i2<len(self.state)-1 and j2>0:
      i2+=1
      j2-=1
    posD1 = i2-i # Indica en cual posicion de la diagonal generada quedo la ficha que se puso
    while i2>=0 and j2<len(self.state[0]):
      diagonal1.append(self.state[i2][j2])
      i2-=1
      j2+=1
    i2 = i
    j2 = j
    # Para sacar la diagonal2
    while i2>0 and j2>0:
      i2-=1
      j2-=1
    posD2 = j-j2 # Indica en cual posicion de la diagonal generada quedo la ficha que se puso
    while i2<len(self.state) and j2<len(self.state[0]):
      diagonal2.append(self.state[i2][j2])
      i2+=1
      j2+=1
    return (diagonal1, diagonal2, posD1, posD2) # Se retornan las diagonales y las posiciones donde quedo la ficha en dicho vector
  
  # Dado un vector, verifica si la marca dd esta en el 4 veces seguidas.
  def checkWin(self, vec, mark):
    if len(vec)<4:
      return False
    else:
      val = 0 # Acumulador temporal
      for i in range(0, len(vec)):
        if vec[i]==mark:
          val+=1
        else:
          val = 0
        if val==4: # Si hay 4 en linea.
          return True
      return False
  
  # Dado un vector, verifica si he bloqueado
  def checkBlock(self, vec, pos):
    posIni = max(0,pos-3)
    posFin = posIni+3
    while (posIni<=pos and posFin<len(vec)):
      val = 0 # Acumulador
      for i in range(posIni, posFin+1):
        if i is not pos: # Sin analizar la posicion donde acabo de poner...
          if vec[i]==-self.mark:
            val+=1
      if val==3: # ... Analiza si existen 3 marcas del enemigo 
        return True
      posIni+=1
      posFin+=1
    return False

  # Dado un vector (Horizontal o Diagonal), cuenta cuantos movimientos le bloqueo al oponente
  def countBlockEnemyMovesHorDia(self, vec, pos):
    posIni = max(0,pos-3)
    posFin = posIni+3
    moves=0
    while (posIni<=pos and posFin<len(vec)):
      flag=False
      val = 0 # Acumulador
      for i in range(posIni, posFin+1):
        if i is not pos:
          if vec[i]==-self.mark:
            val+=1
          if vec[i]==self.mark:
            flag=True
      if flag is not True and val>0:
        moves+=1
      posIni+=1
      posFin+=1
    return moves

  # Dado un vector (Vertical), verifica si bloqueo al oponente
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

  # Dado un vector (Vertical), cuenta cuantas posibilidades de ganar se tienen
  def countOpenMovesVer(self, vec, pos, mark):
    i = 0
    cont = 0
    while i<len(vec) and vec[i] != -mark:
      cont+=1
      if cont>3:
        return 1
      i+=1
    return 0

  # Dado un vector (Horizontal o Diagonal), cuenta cuantas movimientos posibilidades tengo de ganar
  def countOpenMovesHorDia(self, vec, pos, mark):
    posIni = max(0,pos-3)
    posFin = posIni+3
    moves = 0
    while (posIni<=pos and posFin<len(vec)):
      val = 0 # Acumulador
      for i in range(posIni, posFin+1):
        if i is not pos:
          if vec[i]==0 or vec[i]==mark: # Si la posicion esta libre
            val+=1
      if val == 3:
        moves+=1
      posIni+=1
      posFin+=1
    return moves

  # Dado un vector, verifica si es un se trata de un movimiento prohibido o que me bloquea una jugada ganadora
  def checkNotAllowMoves(self, vec, pos, mark):
    vecCopy = copy.deepcopy(vec)    
    vecCopy[pos] = mark
    if self.checkWin(vecCopy, mark):
      return True
    return False

  # Imprime el arbol con sus heuristicas
  def printTree(self,node,nivel,ruta):
    if len(node.children)>0:
      print(ruta,"----------------")
    for i,n in enumerate(node.children):
      print("Nivel: ",nivel, "Hijo: ", i,"Heuristica: ", n.h)
    for i,n in enumerate(node.children):
      node.printTree(n,nivel+1,ruta + "-" + str(i))

  # Cambia el valor de las heuristicas
  def changeHeuristics(self, vec):
    max = float('-inf')
    # Buscar el maximo
    for i in range(0, len(vec)):
      if not (vec[i]==50 or vec[i]==40 or vec[i]==-1):
        if vec[i]>max:
          max = vec[i]
    # Si no hay cambios
    if max == float('-inf'):
      return vec
    # Cambiar heuristica
    for i in range(0, len(vec)):
      if not (vec[i]==50 or vec[i]==40 or vec[i]==-1):
        if vec[i] == max:
          vec[i] = 10
        else:
          vec[i] = 0
    return vec

# Algoritmo alpha beta para recorrer el arbol
def alpha_beta(node, depth, a, b, turn):
  # turn: true - MAX
  # turn: false - MIN
  if (depth == 0 or node.isTerminal()):
    return (node.h, node.operator)
  # Agregar hijos
  children=node.getchildrens()
  for k in range(0, len(children)):
    if children[k] is not None:
      (child, i, j) = children[k]
      newChild = node.add_child(-node.mark, i=i, j=j, value=node.value+'-'+str(k), state=child, operator=k)
  # Agregar heuristicas a los hijos
  heuristicValues = node.chooseBestMove()
  #heuristicValues = node.changeHeuristics(heuristicValues)
  for i in range(0, len(heuristicValues)):
    aux = heuristicValues[i]
    #if node.children[i].mark ==-1 and aux == 0:
    #  aux = -aux
    node.children[i].h = aux
  if turn: # Si juega MAX
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
  else: # Si juega MIN
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

# Metodo main que va a llamar NAO
def play(initState):
  n = -1 # Marca del enemigo
  b = 1 # Marca de la IA
  operators = [0,1,2,3,4,5,6]
  m = n
  b = Board(mark=m, i=0, j=0, state=initState,value="1",operators=operators, operator=None, parent=None,objective=None)
  return alpha_beta(b, 1, float('-inf'), float('inf'), True)[1] # Columna de la mejor jugada