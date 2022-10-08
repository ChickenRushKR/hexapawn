import cv2
import numpy as np
from queue import PriorityQueue

bg = np.full((700, 600, 3), 255, dtype=np.uint8)
board = [[0,0,0],[0,0,0],[0,0,0]]
select = [-1,-1]
turn = 1
# movrange = [[-1,0],[0,1],[1,0],[0,-1]]
# kilrange = [[-1,-1],[-1,1],[1,1],[1,-1]]

class Tree:
    def __init__(self, head):
        self.head = head

    def expand(self, cur):
        movrange = [[-1,0],[0,1],[1,0],[0,-1]]
        kilrange = [[-1,-1],[-1,1],[1,1],[1,-1]]
        for pawnId in range(len(cur.player.pawnPos)):
            pawnPos = cur.player.pawnPos[pawnId]
            for mov in movrange:
                res = [ai + bi for ai, bi, in zip(pawnPos, mov)]
                if res[0] in range(0, 3) and res[1] in range(0, 3):
                    board = cur.board
                    if board[res[0]][res[1]] == 0:
                        board[pawnPos[0]][pawnPos[1]] = 0
                        board[res[0]][res[1]] = cur.player.color
                        cur.player.mov(pawnPos, res)
                        child = Node(parent=cur, board=board, player=cur.enemy, enemy=cur.player, depth=cur.depth+1)
                        child.score = score(board)
                        child.move = [pawnPos, res]
                        cur.children.put((child.score, child))
            for mov in kilrange:
                res = [ai + bi for ai, bi, in zip(pawnPos, mov)]
                if res[0] in range(0, 3) and res[1] in range(0, 3):
                    board = cur.board
                    if board[res[0]][res[1]] == cur.enemy.color:
                        board[pawnPos[0]][pawnPos[1]] = 0
                        board[res[0]][res[1]] = cur.player.color
                        cur.player.mov(pawnPos, res)
                        cur.enemy.die(res[0], res[1])
                        child = Node(parent=cur, board=board, player=cur.enemy, enemy=cur.player, depth=cur.depth+1)
                        child.score = score(board)
                        child.move = [pawnPos, res]
                        cur.children.put((child.score, child))


class Node:
    def __init__(self, parent, board, player, enemy, depth):
        self.parent = parent
        self.board = board
        self.player = player
        self.enemy = enemy
        self.depth = depth
        self.score = 0
        self.move = []
        self.children = PriorityQueue()
    

class player:
    def __init__(self, id, color):
        if id == 'HUMAN':
            self.id = id
            self.color = color
            self.pawnPos = []
            self.select = -1
            self.remain = 3
        else:
            self.id = id
            self.color = color
            self.pawnPos = []
            self.select = -1
            self.remain = 3

    def load(self):
        pawnPos = []
        for i in range(3):
            for j in range(3):
                if board[j][i] == self.color and self.id == 'HUMAN':
                    pawnPos.append([j, i])
                elif board[j][i] == self.color and self.id == 'COMPUTER':
                    pawnPos.append([j, i])
        self.pawnPos = pawnPos

    def doSelect(self, j, i):
        for pawnID in range(3):
            if self.pawnPos[pawnID] == [j,i]:
                self.select = pawnID
                return self.select

    def unSelect(self):
        self.select = -1

    def die(self, j, i):
        pawnPos = []
        for pawnID in range(3):
            if self.pawnPos[pawnID] != [j,i]:
                pawnPos.append(self.pawnPos[pawnID])
        self.remain = len(pawnPos)
        self.pawnPos = pawnPos

    def mov(self, src, dst):
        pawnPos = []
        for pawnID in range(3):
            if self.pawnPos[pawnID] != src:
                pawnPos.append(self.pawnPos[pawnID])
            else:
                pawnPos.append(dst)
        self.pawnPos = pawnPos

def minimax(human, computer):
    global board
    global turn
    head = Node(parent=None, board=board, player=computer, enemy=human, depth=0)
    tree = Tree(head)
    tree.expand(head)
    print(tree)
    Move = tree.head.children.get()
    print(Move)
    board = Move.board
    turn = human.color
    
        
def score(board):
    whitepos = []
    blackpos = []
    for i in range(3):
        for j in range(3):
            if board[j][i] == 1:
                whitepos.append([j,i])
            if board[j][i] == 2:
                blackpos.append([j,i])
    if len(whitepos) == 0:
        return -100, 100
    if len(blackpos) == 0:
        return 100, -100
    
    whiteScore = 0
    blackScore = 0
    for pawn in range(len(whitepos)):
        whiteScore += (whitepos[pawn][0] ** 2)
        blackScore -= ((4 - 2 + whitepos[pawn][0]) ** 2)
    for pawn in range(len(blackpos)):
        whiteScore -= ((4 - blackpos[pawn][0]) ** 2)
        blackScore += (2 - blackpos[pawn][0]) ** 2
    return whiteScore, blackScore


# def score(white, black):
#     if white.remain == 0:
#         return -100, 100
#     elif black.remain == 0:
#         return 100, -100
#     whiteScore = 0
#     blackScore = 0
#     for pawn in range(len(white.pawnPos)):
#         whiteScore += (white.pawnPos[pawn][0] ** 2)
#         blackScore -= ((4 - 2 + white.pawnPos[pawn][0]) ** 2)
#     for pawn in range(len(black.pawnPos)):
#         whiteScore -= ((4 - black.pawnPos[pawn][0]) ** 2)
#         blackScore += (2 - black.pawnPos[pawn][0]) ** 2
#     return whiteScore, blackScore


def mouse(event, x, y, flags, param):
    global bg
    global board
    global select
    global turn
    if turn == param[0].color:
        if event == cv2.EVENT_FLAG_LBUTTON:
            i = x // 200
            j = y // 200
            if board[j][i] == param[0].color and select == [-1,-1]:
                param[0].doSelect(j,i)
                board[j][i] = 3
                select = [j, i]
            if select != [-1, -1] and abs(select[0] - j) <= 1 and abs(select[1] - i) <= 1:
                if board[j][i] == 0 and abs(select[0] - j) != abs(select[1] - i):   # MOVE
                    param[0].pawnPos[param[0].select] = [j,i]
                    param[0].unSelect()
                
                    board[j][i] = param[0].color
                    board[select[0]][select[1]] = 0
                    select = [-1, -1]
                    turn = param[1].color
                elif board[j][i] == param[1].color and abs(select[0] - j) == 1 and abs(select[1] - i) == 1:  # KILL
                    param[0].pawnPos[param[0].select] = [j,i]
                    param[0].unSelect()
                    param[1].die(j, i)

                    board[j][i] = param[0].color
                    board[select[0]][select[1]] = 0
                    select = [-1, -1]
                    turn = param[1].color
        if event == cv2.EVENT_FLAG_RBUTTON:
            param[0].unSelect()
            board[select[0]][select[1]] = 1
            select = [-1, -1]

    
def load(filename = ''):
    global bg
    global board
    if filename == '':
        board = [[1,1,1],[0,0,0],[2,2,2]]
    else:
        print('Read FILE:', filename)
        with open(filename, 'r') as f:
            for i in range(3):
                line = f.readline()
                pawns = line.split(',')
                for j in range(3):
                    board[i][j] = int(pawns[j])
            print(board)
    return board

def show(human, computer):
    global turn
    nbg = np.full((700, 600, 3), 146, dtype=np.uint8)
    cv2.line(nbg, (200,0), (200,600), (0,0,0), 6)
    cv2.line(nbg, (400,0), (400,600), (0,0,0), 6)
    cv2.line(nbg, (0,200), (600,200), (0,0,0), 6)
    cv2.line(nbg, (0,400), (600,400), (0,0,0), 6)
    cv2.line(nbg, (0,600), (600,600), (0,0,0), 6)

    for i in range(3):
        for j in range(3):
            if board[j][i] == 0:
                continue
            elif board[j][i] == 1:
                cv2.circle(nbg, ((i*2+1)*100, (j*2+1)*100), 50, (255,255,255), -1)
            elif board[j][i] == 2:
                cv2.circle(nbg, ((i*2+1)*100, (j*2+1)*100), 50, (0,0,0), -1)
            elif board[j][i] == 3:
                cv2.circle(nbg, ((i*2+1)*100, (j*2+1)*100), 50, (255,255,0), -1)
            else:
                exit()
    if turn == human.color:
        cv2.putText(nbg, human.id, (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
    elif turn == computer.color:
        cv2.putText(nbg, computer.id, (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
    else:
        cv2.putText(nbg, "END", (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
        bg = nbg
        cv2.imshow('Board', nbg)
        cv2.waitKey(1000)

    bg = nbg
    cv2.imshow('Board', nbg)
    cv2.setMouseCallback('Board', mouse, [human, computer])
    cv2.waitKey(100)
    
    


def main():
    global turn
    global board
    color = input('Type "WHITE" or "BLACK":')
    if color == 'WHITE':
        human = player('HUMAN', 1)
        computer = player('COMPUTER', 2)
    else:
        human = player('HUMAN', 2)
        computer = player('COMPUTER', 1)
    turn = int(input('WHITE first (1) BLACK first (2) '))
    load('')
    human.load()
    computer.load()
    while turn != 0:
        show(human, computer)
        # if turn == computer.color:
            # minimax(human, computer)
        if human.color == 1:
            humanR, computerR = score(board)
        else:
            computerR, humanR = score(board)
        print("human:", humanR)
        print("computer:", computerR)
        if humanR == 100:
            print("HUMAN WIN")
            break
        elif computerR == 100:
            print("COMPUTER WIN")
            break




if __name__ == "__main__":
    main()