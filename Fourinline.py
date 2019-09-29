import pydot
#from IPython.display import Image, display
try: 
    import queue
except ImportError:
    import Queue as queue
import numpy as np
import copy

import convertirImgToMatrix as conv

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

    #Devuelve todos los estados segun los operadores aplicados
    def getchildrens(self):
        listChildren = []
        for k,op in enumerate(self.operators):
            state = self.getState(k) # State, Pos i, Pos j
        if state == None:
            listChildren.append(None)
        else: 
            if not self.repeatStatePath(state[0]):
                listChildren.append(state)
            else: 
                listChildren.append(None)
        return listChildren
        # return [
        #     self.getState(i)
        #       if not self.repeatStatePath(self.getState(i)[0]) 
        #         else None for i, op in enumerate(self.operators)]
    
    def getState(self, index):
        pass
  
    def __eq__(self, other):
        return self.state == other.state
 
    def __lt__(self, other):
        return self.f() < other.f()
  
    def repeatStatePath(self, state):
        n=self
        while n is not None and n.state!=state:
            n=n.parent
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


class Board(Node):
    # mark = 1 -> MAX (Blanco)
    # mark = -1 -> MIN (Negro)
    # i : Fila donde se hizo la ultima jugada
    # j : Columna donde se hizo la ultima jugada

    def __init__(self, mark, i, j, **kwargs):
        #Node.__init__(self, mark,i,j, **kwargs)
        self.mark = mark
        self.i = i
        self.j = j
        super(Board, self).__init__(**kwargs)

    # Modificacion necesaria al agregar un nuevo atributo a la clase
    def add_child(self, mark, i, j, value, state, operator):
        node=type(self)(mark=mark, i=i, j=j, value=value, state=state, operator=operator,parent=self, operators=self.operators)
        node.level=node.parent.level+1
        self.children.append(node)
        return node

    # Aplicar alguno de los 7 operadores
    def getState(self, i):
        state = copy.deepcopy(self.state)
        nextState = copy.deepcopy(state)
        mark = self.mark*-1
        if (state[0][i] == 0): # Si la columna no esta llena
            for k in reversed(range(0,6)):
                if (state[k][i] == 0):
                    nextState[k][i] = mark
                    return (nextState, k, i)
        else:
            return None
        #return nextState if state!=nextState else None

    # Selecciona la mejor jugada
    def chooseBestMove(self):
        heuristicValues = [] # Valores heuristicos de los hijos
        for i, child in enumerate(self.children):
            h = child.heuristic()
            if h == 50: # Si encuentro un movimiento que me hace ganar
                return child.operator
            heuristicValues.append(h)
        if(len(heuristicValues)==0):
            return "Tablero lleno"
        maxHeuristic = max(heuristicValues) # Valor maximo de la h
        if maxHeuristic == 40: # Si no gano, pero puedo bloquear
            for i in range(0, len(heuristicValues)):
                if heuristicValues[i] == 40: 
                    return self.children[i].operator
        if maxHeuristic == -1: # Si todos los movimientos son prohibidos
            return self.children[0].operator      
        # Saber si el valor se repite
        i = 0
        cont = 0
        positionChild = -1 # Guarda la posicion del mejor hijo en caso de no haber valores de h repetidos
        while(i<len(heuristicValues) and cont<2):
            if (heuristicValues[i] == maxHeuristic):
                cont+=1
                positionChild = i
            i+=1
        if cont < 2: # Retorna el valor que mas movimientos bloquea
            return self.children[positionChild].operator
        # Analiza paso 2 de la heuristica: El que mas movimientos me genere
        for i in range(0, len(heuristicValues)):
            if heuristicValues[i] == maxHeuristic:
                h = self.children[i].getHorizontalState(self.children[i].i)
                v = self.children[i].getVerticalState(self.children[i].j)
                (d1, d2, posD1, posD2) = self.children[i].getDiagonalState(self.children[i].i, self.children[i].j)
                heuristicValues[i] += self.countOpenMovesVer(v, self.children[i].i) + self.countOpenMovesHorDia(h, self.children[i].j, self.children[i].mark) + self.countOpenMovesHorDia(d1, posD1, self.children[i].mark) + self.countOpenMovesHorDia(d2, posD2, self.children[i].mark)
        # Saber si el valor se repite
        maxHeuristic = max(heuristicValues)
        i = 0
        cont = 0
        positionChild = -1 # Guarda la posicion del mejor hijo en caso de no haber valores de h repetidos
        while(i<len(heuristicValues) and cont<2):
            if (heuristicValues[i] == maxHeuristic):
                cont+=1
                positionChild = i
            i+=1
        if cont < 2: # Retorna el valor que mas movimientos me genere
            return self.children[positionChild].operator
        # Analiza paso 3 de la heuristica: El que menos le genere al otro.
        for i in range(0, len(heuristicValues)):
            if heuristicValues[i] == maxHeuristic:
                if(self.children[i].i >0): # Analizar los movimientos del enemigo
                    h = self.getHorizontalState(self.children[i].i-1)
                    v = self.getVerticalState(self.children[i].j)
                    (d1, d2, posD1, posD2) = self.getDiagonalState(self.children[i].i-1, self.children[i].j)
                    heuristicValues[i] += 15 - (self.countOpenMovesVer(v, self.children[i].i) + self.countOpenMovesHorDia(h, self.children[i].j, self.children[i].mark*-1) + self.countOpenMovesHorDia(d1, posD1, self.children[i].mark*-1) + self.countOpenMovesHorDia(d2, posD2, self.children[i].mark*-1))
        # Saber si el valor se repite
        maxHeuristic = max(heuristicValues)
        i = 0
        cont = 0
        positionChild = -1 # Guarda la posicion del mejor hijo en caso de no haber valores de h repetidos
        while(i<len(heuristicValues) and cont<2):
            if (heuristicValues[i] == maxHeuristic):
                cont+=1
                positionChild = i
            i+=1
        if cont < 2: # Retorna el valor que mas movimientos le bloquee al otro
            return self.children[positionChild].operator
        else: # Retorna el movimiento que no me bloquee una jugada ganadora
            for i in range(0, len(heuristicValues)):
                if heuristicValues[i] == maxHeuristic: 
                    # Analizar los movimientos del enemigo
                    h = self.getHorizontalState(self.children[i].i-1)
                    v = self.getVerticalState(self.children[i].j)
                    (d1, d2, posD1, posD2) = self.getDiagonalState(self.children[i].i-1, self.children[i].j)
                    m = self.children[i].mark
                    if not (self.checkNotAllowMoves(h,self.children[i].j, m) or self.checkNotAllowMoves(v,self.children[i].i-1, m) or self.checkNotAllowMoves(d1,posD1, m) or self.checkNotAllowMoves(d2,posD2, m)):
                        return self.children[i].operator
            # Retorna cualquiera     
            return self.children[positionChild].operator

  # Retorna el valor heuristico de un estado (Valor numerico)
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
            m = -self.mark # La marca del enemigo
            if self.checkNotAllowMoves(h,self.j, m) or self.checkNotAllowMoves(v,self.i-1, m) or self.checkNotAllowMoves(d1,posD1, m) or self.checkNotAllowMoves(d2,posD2, m):
                return -1
        # Cuantos movimientos le bloquea al enemigo
        h = self.getHorizontalState(self.i)
        v = self.getVerticalState(self.j)
        (d1, d2, posD1, posD2) = self.getDiagonalState(self.i, self.j)
        return self.countBlockEnemyMovesHorDia(h, self.j) + self.countBlockEnemyMovesHorDia(d1, posD1) +  self.countBlockEnemyMovesHorDia(d2, posD2) + self.countBlockEnemyMovesVer(v, self.i)


    # 1. Saber si gano
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

    # 3. Mejor movimiento
    def bestMove(self, m):
        pass

    # ---Metodos auxiliares para la funcion heuristica---

    # Retorna la horizontal de la ficha puesta
    def getHorizontalState(self, i):
        #i: fila de la ficha a revisar
        horizontal = []
        for j in range(0,len(self.state[0])):
            horizontal.append(self.state[i][j])
        return horizontal

    # Retorna la vertical de la ficha puesta
    def getVerticalState(self, j):
        #j: fila de la ficha a revisar
        vertical = []
        for i in range(0,len(self.state)):
            vertical.append(self.state[i][j])
        return vertical

    def getDiagonalState(self, i, j):
        #i, j: fila y columna de la ultima ficha a revisar
        i2 = i
        j2 = j
        diagonal1 = []
        diagonal2 = []
        # Para sacar la diagonal1
        while i2<len(self.state)-1 and j2>0:
            i2+=1
            j2-=1
        posD1 = i2-i # Valor necesario para el bloquear.
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
        posD2 = j-j2 # Valor necesario para el bloquear.
        while i2<len(self.state) and j2<len(self.state[0]):
            diagonal2.append(self.state[i2][j2])
            i2+=1
            j2+=1
        # Si el numero de elementos es menor de alguna diagonal
        # es menor a 3, no vale la pena analizarla.
        return (diagonal1, diagonal2, posD1, posD2)
  
    # Dado un vector, verifica si la marca esta en el 4 veces seguidas.
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
                if i is not pos:
                    if vec[i]==-self.mark:
                        val+=1
            if val==3:
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
        if(vec[pos+1] == -self.mark and pos >=2):
            return 1
        return 0

    # Dado un vector (Vertical), cuenta cuantas posibilidades de ganar se tienen
    def countOpenMovesVer(self, vec, pos):
        i = 0
        cont = 0
        while i<pos:
            if vec[i] == 0:
                cont+=1
            i+=1
        if cont<3:
            return 0
        else:
            return cont-2

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


b = -1
n = 1
#initState = [[0,0,0,0,0,0,0],
 #            [0,0,0,b,n,0,0],
  #           [0,0,n,n,b,n,0],
   #          [0,0,b,n,n,n,b],
    #         [0,0,b,n,b,b,0],
     #        [0,0,n,b,b,b,n]]
initState = conv.matrix


operators = [0,1,2,3,4,5,6]
#i = 0 # Fila de la ultima jugada (Prueba)
#j = 0 # Columna de la ultima jugada (Prueba)
m = b
b = Board(mark=m, i=0, j=0, state=initState,value="1",operators=operators, operator=None, parent=None,objective=None)

# h = b.getHorizontalState(i)
# v = b.getVerticalState(j)
# (d1, d2, posD1, posD2) = b.getDiagonalState(i, j)
# print(b.heuristic())
children=b.getchildrens()
for k in range(0, len(children)):
    if children[k] is not None:
        (child, i, j) = children[k]
        newChild = b.add_child(b.mark*-1, i=i, j=j, value=b.value+'-'+str(k), state=child, operator=k)

print(b.chooseBestMove())
