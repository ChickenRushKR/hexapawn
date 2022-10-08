import cv2
import numpy as np

bg = np.full((700, 600, 3), 255, dtype=np.uint8)
board = [[0,0,0],[0,0,0],[0,0,0]]
select = [-1,-1]
turn = 1

class player:
    def __init__(self, id):
        if id == 'HUMAN':
            self.id = id
            self.pawnPos = [[0,0], [0,1], [0,2]]
            self.select = -1
            self.remain = 3
        else:
            self.id = id
            self.pawnPos = [[2,0], [2,1], [2,2]]
            self.select = -1
            self.remain = 3

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
        

def win_condition(p1, p2):
    global turn
    p1R = p1.pawnPos[0][0] ** 2 + p1.pawnPos[1][0] ** 2 + p1.pawnPos[2][0] ** 2
    p2R = p2.pawnPos[0][0] ** 2 + p2.pawnPos[1][0] ** 2 + p2.pawnPos[2][0] ** 2
    if p2.remain == 0:
        p1R = 100
        p2R = -100
        turn = -1
    elif p1.remain == 0:
        p1R = -100
        p2R = 100
        turn = -1
    elif p1.pawnPos[0][0] == 2 and p1.pawnPos[1][0] == 2 and p1.pawnPos[2][0] == 2:
        p1R = 100
        p2R = -100
        turn = -1
    elif p2.pawnPos[0][0] == 0 and p2.pawnPos[1][0] == 0 and p2.pawnPos[2][0] == 0:
        p1R = -100
        p2R = 100
        turn = -1
    else:
        p1R
        p2R
    return p1R, p2R




def mouse(event, x, y, flags, param):
    global bg
    global board
    global select
    global turn
    if turn == 1:
        if event == cv2.EVENT_FLAG_LBUTTON:
            i = x // 200
            j = y // 200
            if board[j][i] == 1 and select == [-1,-1]:
                param[0].doSelect(j,i)
                board[j][i] = 3
                select = [j, i]
            if select != [-1, -1] and abs(select[0] - j) <= 1 and abs(select[1] - i) <= 1:
                if board[j][i] == 0 and abs(select[0] - j) != abs(select[1] - i):   # MOVE
                    param[0].pawnPos[param[0].select] = [j,i]
                    param[0].unSelect()
                
                    board[j][i] = 1
                    board[select[0]][select[1]] = 0
                    select = [-1, -1]
                    turn = 2
                elif board[j][i] == 2 and abs(select[0] - j) == 1 and abs(select[1] - i) == 1:  # KILL
                    param[0].pawnPos[param[0].select] = [j,i]
                    param[0].unSelect()
                    param[1].die(j, i)

                    board[j][i] = 1
                    board[select[0]][select[1]] = 0
                    select = [-1, -1]
                    turn = 2
        if event == cv2.EVENT_FLAG_RBUTTON:
            param[0].unSelect()
            board[select[0]][select[1]] = 1
            select = [-1, -1]

    
def load(filename=''):
    global bg
    global board
    if filename == '':
        board = [[1,1,1],[0,0,0],[2,2,2]]
    else:
        with open(filename, 'r') as f:
            for i in range(3):
                line = f.readline()
                pawns = line.split(',')
                for j in range(3):
                    board[j][i] = pawns[j]
    return board

def show(human, computer):
    global turn
    nbg = np.full((700, 600, 3), 255, dtype=np.uint8)
    cv2.line(nbg, (200,0), (200,600), (0,0,0), 6)
    cv2.line(nbg, (400,0), (400,600), (0,0,0), 6)
    cv2.line(nbg, (0,200), (600,200), (0,0,0), 6)
    cv2.line(nbg, (0,400), (600,400), (0,0,0), 6)

    for i in range(3):
        for j in range(3):
            if board[j][i] == 0:
                continue
            elif board[j][i] == 1:
                cv2.circle(nbg, ((i*2+1)*100, (j*2+1)*100), 50, (0,0,255), 30)
            elif board[j][i] == 2:
                cv2.circle(nbg, ((i*2+1)*100, (j*2+1)*100), 50, (255,0,0), 30)
            elif board[j][i] == 3:
                cv2.circle(nbg, ((i*2+1)*100, (j*2+1)*100), 50, (255,255,0), 30)
            else:
                exit()
    if turn == 1:
        cv2.putText(nbg, human.id, (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
    elif turn == 2:
        cv2.putText(nbg, computer.id, (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
    else:
        cv2.putText(nbg, "END", (10, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
    

    bg = nbg
    cv2.imshow('Board', nbg)
    cv2.setMouseCallback('Board', mouse, [human, computer])
    cv2.waitKey(100)
    
    


def main():
    global turn
    human = player('HUMAN')
    computer = player('COMPUTER')
    load('')
    while turn != 0:
        show(human, computer)
        humanR, computerR = win_condition(human, computer)
        if humanR == 100:
            print("HUMAN WIN")
            break
        elif computerR == 100:
            print("COMPUTER WIN")
            break




if __name__ == "__main__":
    main()