import cv2
import numpy as np
from queue import PriorityQueue
import copy

bg = np.full((700, 600, 3), 255, dtype=np.uint8)
board = [[0,0,0],[0,0,0],[0,0,0]]
select = [-1,-1]
turn = 1
user = 0
com = 0
# movrange = [[-1,0],[0,1],[1,0],[0,-1]]
# kilrange = [[-1,-1],[-1,1],[1,1],[1,-1]]

# class Tree:
#     def __init__(self, head):
#         self.head = head

class Node:
    def __init__(self, parent, board, player, enemy, depth):
        self.parent = parent
        self.board = board
        self.player = player
        self.enemy = enemy
        self.depth = depth
        self.score = -9999
        self.move = []
        self.children = []

    def copy(self):
        newplayer = self.player.copy(self.board)
        newenemy = self.enemy.copy(self.board)
        newNode = Node(self.parent, self.board, newplayer, newenemy, self.depth)
        return newNode
    
    def sort(self, max):
        if max:
            self.children = sorted(self.children, key=lambda x: x.score, reverse=True)
        else:
            self.children = sorted(self.children, key=lambda x: x.score)

    

class player:
    def __init__(self, id, color):
        if id == 'HUMAN':
            self.id = id
            self.color = color
            self.pawnPos = []
            self.select = -1
            self.remain = 0
        else:
            self.id = id
            self.color = color
            self.pawnPos = []
            self.select = -1
            self.remain = 0

    def copy(self, board):
        newplayer = player(self.id, self.color)
        newplayer.load(board)
        return newplayer

    def load(self, board):
        self.remain = 0
        pawnPos = []
        for i in range(3):
            for j in range(3):
                if board[j][i] == self.color:
                    self.remain += 1
                    pawnPos.append([j, i])
                elif board[j][i] == self.color:
                    self.remain += 1
                    pawnPos.append([j, i])
                elif board[j][i] == 3 and self.id == 'HUMAN':
                    self.remain += 1
                    pawnPos.append([j, i])

        self.pawnPos = pawnPos

    def doSelect(self, j, i):
        for pawnID in range(self.remain):
            if self.pawnPos[pawnID] == [j,i]:
                self.select = pawnID
                return self.select

    def unSelect(self):
        self.select = -1

    def die(self, j, i):
        pawnPos = []
        for pawnID in range(self.remain):
            if self.pawnPos[pawnID] != [j,i]:
                pawnPos.append(self.pawnPos[pawnID])
        self.remain = len(pawnPos)
        self.pawnPos = pawnPos

    def mov(self, src, dst):
        pawnPos = []
        for pawnID in range(self.remain):
            if self.pawnPos[pawnID] != src:
                pawnPos.append(self.pawnPos[pawnID])
            else:
                pawnPos.append(dst)
        self.pawnPos = pawnPos



def expand(cur, depth, max):
    if depth == 3:
        _score = score(cur.board)
        return _score[cur.enemy.color - 1]

    movrange = [[-1,0],[0,1],[1,0],[0,-1],[-1,-1],[-1,1],[1,1],[1,-1]]
    idx = 0
    l = 0
    for pawnId in range(len(cur.player.pawnPos)):
        idx = 0
        pawnPos = cur.player.pawnPos[pawnId]
        for mov in movrange:
            res = [pawnPos[0] + mov[0], pawnPos[1] + mov[1]]
            # res = [ai + bi for ai, bi, in zip(pawnPos, mov)]
            if res[0] not in range(0, 3) or res[1] not in range(0, 3):
                idx += 1
                continue
            board = copy_arr(cur.board)
            play = cur.copy()
            if board[res[0]][res[1]] == 0 and idx < 4:
                board[pawnPos[0]][pawnPos[1]] = 0
                board[res[0]][res[1]] = play.player.color
                play.player.mov(pawnPos, res)
                child = Node(parent=cur, board=board, player=play.enemy, enemy=play.player, depth=play.depth+1)
                child.move = [pawnPos, res]
                if score(board)[max] != 100:
                    child.score = expand(child, depth + 1, max = not max)
                else:
                    child.score = score(board)[max]

                if len(cur.children) != 0 and cur.children[0].score <= child.score and max is False:
                    idx += 1
                    continue
                elif len(cur.children) != 0 and cur.children[0].score >= child.score and max is True:
                    idx += 1
                    continue

                cur.children.append(child)
                cur.sort(max)
            if board[res[0]][res[1]] == play.enemy.color and idx >= 4:
                board[pawnPos[0]][pawnPos[1]] = 0
                board[res[0]][res[1]] = play.player.color
                play.player.mov(pawnPos, res)
                play.enemy.die(res[0], res[1])
                child = Node(parent=cur, board=board, player=play.enemy, enemy=play.player, depth=play.depth+1)
                child.move = [pawnPos, res]
                if score(board)[max] != 100:
                    child.score = expand(child, depth + 1, max = not max)
                else:
                    child.score = score(board)[max]
                    
                if len(cur.children) != 0 and cur.children[0].score <= child.score and max is False:
                    idx += 1
                    continue
                elif len(cur.children) != 0 and cur.children[0].score >= child.score and max is True:
                    idx += 1
                    continue

                cur.children.append(child)
                cur.sort(max)
            
            idx += 1
    return cur.children[0].score
            
            
def minimax(human, computer):
    global board
    global turn
    head = Node(parent=None, board=board, player=computer, enemy=human, depth=0)
    expand(head, 0, True)
    src = head.children[0].move[0]
    dst = head.children[0].move[1]
    if board[dst[0]][dst[1]] == human.color:
        human.die(dst[0], dst[1])
        computer.mov(src, dst)
    else:
        computer.mov(src, dst)
    board[dst[0]][dst[1]] = computer.color
    board[src[0]][src[1]] = 0
    turn = human.color


def copy_arr(arr):
    newarr = [[0,0,0],[0,0,0],[0,0,0]]
    for i in range(3):
        for j in range(3):
            newarr[j][i] = arr[j][i]
    return newarr



def maxplay(node, depth, max):
    global com
    if depth == 3 or len(node.children) == 0:
        return node
    if max:
        value = -9999
        idx = -1
        for i in range(len(node.children)):
            val = maxplay(node.children[i], depth + 1, False)
            if value <= val.score:
                value = val.score
                idx = i
        node.score = value
        print(value)
    else:
        value = 9999
        idx = -1
        for i in range(len(node.children)):
            val = maxplay(node.children[i], depth + 1, True)
            if value >= val.score:
                value = val.score
                idx = i
        node.score = value
        print(value)
    return node

        
        
def score(board):
    global user
    whitepos = []
    blackpos = []
    for i in range(3):
        for j in range(3):
            if board[j][i] == 1:
                whitepos.append([j,i])
                if j == 2:
                    return 100, -100
            if board[j][i] == 2:
                blackpos.append([j,i])
                if j == 0:
                    return -100, 100
            if board[j][i] == 3:
                if user == 1:
                    whitepos.append([j,i])
                else:
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
                    # param[0].pawnPos[param[0].select] = [j,i]
                    param[0].mov(select, [j,i])
                    param[0].unSelect()
                    board[j][i] = param[0].color
                    board[select[0]][select[1]] = 0
                    select = [-1, -1]
                    turn = param[1].color
                elif board[j][i] == param[1].color and abs(select[0] - j) == 1 and abs(select[1] - i) == 1:  # KILL
                    # param[0].pawnPos[param[0].select] = [j,i]
                    param[0].mov(select, [j,i])
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
                pawns = line.split(' ')
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
    elif turn == 10:
        cv2.putText(nbg, "HUMAN WIN", (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
    elif turn == 20:
        cv2.putText(nbg, "COMPUTER WIN", (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
    else:
        cv2.putText(nbg, "END", (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
        bg = nbg
        cv2.imshow('Board', nbg)
        cv2.waitKey(1000)

    bg = nbg
    cv2.imshow('Board', nbg)
    cv2.setMouseCallback('Board', mouse, [human, computer])
    cv2.waitKey(500)
    
    


def main():
    global turn
    global board
    global user
    global com
    while True:
        color = input('Type "WHITE" or "BLACK": ')
        if color == 'WHITE':
            human = player('HUMAN', 1)
            computer = player('COMPUTER', 2)
            user = 1
            com = 2
        else:
            human = player('HUMAN', 2)
            computer = player('COMPUTER', 1)
            user = 2
            com = 1
        turn = int(input('WHITE first (1) BLACK first (2): '))
        filename = input('Input file name (default board=0): ')
        if filename == '0':
            load('')
        else:
            load(filename)
        # human.load(board)
        # computer.load(board)
        while turn != 0:
            human.load(board)
            computer.load(board)
            show(human, computer)
            if human.color == 1:
                humanR, computerR = score(board)
            else:
                computerR, humanR = score(board)
            print("human:", humanR)
            print("computer:", computerR)
            if humanR == 100:
                turn = 10
                show(human, computer)
                print("HUMAN WIN")
                break
            elif computerR == 100:
                turn = 20
                show(human, computer)
                print("COMPUTER WIN")
                break
            if turn == computer.color:
                show(human, computer)
                minimax(human, computer)
                # exit()
        if input('Play more (1), Exit (2)') == '1':
            continue
        else:
            break




if __name__ == "__main__":
    main()