import time
import random
from sshkeyboard import listen_keyboard, stop_listening

score = 0

isRunning = True
isDown = False

map = [[0 for _ in range(8)] for _ in range(16)]
blocks = {
    1 : [[1,1,1,1]], # I
    2 : [[1,1],      # O
         [1,1]],
    3 : [[1,1,1],    # T
         [0,1,0]],
    4 : [[0,0,1],    # L
         [1,1,1]],
    5 : [[1,0,0],    # J
         [1,1,1]],
    6 : [[1,1,0],    # Z
         [0,1,1]],
    7 : [[0,1,1],    # S
         [1,1,0]]
}

Type = random.randint(1, 7)
curr = {'block' : blocks[Type], 'pos' : [3, 0], 'rotate' : 0}

def mapPrint():
    print()
    print(f"점수 : {score}")
    print()
    for p in map:
        print(p)
    for _ in range(2):
        print()

def drawBlock(block, pos):
    for i in range(len(block)):
        for j in range(len(block[0])):
            if block[i][j] == 1:
                map[pos[1] + i][pos[0] + j] = block[i][j]

def eraseBlock(block, pos):
    for i in range(len(block)):
        for j in range(len(block[0])):
            map[pos[1] + i][pos[0] + j] = 0

def rotateBlock(Type, pos, rotate):
    if rotate == 0:
        b = [[0 for _ in range(len(blocks[Type][0]))] for _ in range(len(blocks[Type]))]
        for i in range(len(blocks[Type])):
            for j in range(len(blocks[Type][0])):
                if blocks[Type][i][j] == 1:
                    b[i][j] = 1
                
    if rotate == 1:
        b = [[0 for _ in range(len(blocks[Type]))] for _ in range(len(blocks[Type][0]))]
        for i in range(len(blocks[Type][0])):
            for j in range(len(blocks[Type]) - 1, -1, -1):
                if blocks[Type][j][i] == 1:
                    b[i][len(blocks[Type]) - 1 - j] = 1

    if rotate == 2:
        b = [[0 for _ in range(len(blocks[Type][0]))] for _ in range(len(blocks[Type]))]
        for i in range(len(blocks[Type]) - 1, -1, -1):
            for j in range(len(blocks[Type][0]) - 1, -1, -1):
                if blocks[Type][i][j] == 1:
                    b[len(blocks[Type]) - 1 - i][len(blocks[Type][0]) - 1 - j] = 1

    if rotate == 3:
        b = [[0 for _ in range(len(blocks[Type]))] for _ in range(len(blocks[Type][0]))]
        for i in range(len(blocks[Type][0]) - 1, -1, -1):
            for j in range(len(blocks[Type])):
                if blocks[Type][j][i] == 1:
                    b[len(blocks[Type][0]) - 1 - i][j] = 1
    if pos[0] + len(b[0]) > 8:
        pos[0] = 8 - len(b[0])
    return b

def eraseLine(c, s):
    for i in range(s, c - 1, -1):
        for j in range(len(map[0])):
            map[i][j] = map[i - c][j]

    for i in range(c):
        for j in range(len(map[0])):
            map[i][j] = 0

def complete():
    global score
    rowCount = 0
    startIdx = 0
    for y in range(len(map)-1, -1, -1):
        if isLine(y):
            rowCount += 1
            if startIdx < y:
                startIdx = y
    if rowCount != 0:
        eraseLine(rowCount, startIdx)
        score += 100 * rowCount

def downBlock(block, pos):
    while not isCollision(block, pos):
        pos[1] += 1

def isCollision(block, pos):
    if pos[1] >= 16 - len(block):
        return True
    hit = []
    for i in range(len(block[0])):
        Max = 0
        for j in range(len(block)):
            if block[j][i] == 1:
                Max = j
        hit.append(Max)
    
    for i in range(len(hit)):
        if map[pos[1] + hit[i] + 1][pos[0] + i]:
            return True
    return False

def isRightWall(block, pos):
    if pos[0] + len(block[0]) + 1 > 8:
        return False
    return True

def isLeftWall(block, pos):
    if pos[0] - 1 < 0:
        return False
    return True

def isLine(y):
    for i in range(len(map[0])):
        if map[y][i] == 0:
            return False
    return True

def isOver(block, pos):
    for i in range(len(block)):
        for j in range(len(block[0])):
            if map[pos[1] + i][pos[0] + j] == 1:
                return True
    return False

def on_press(key):
    global isRunning, curr, Type, isDown
    if not isRunning:
        return

    eraseBlock(curr['block'], curr['pos'])

    if key == "q":
        print('게임을 종료합니다.')
        isRunning = False
        stop_listening()
    elif key == "right" and isRightWall(curr['block'], curr['pos']):
        curr['pos'][0] += 1
    elif key == "left" and isLeftWall(curr['block'], curr['pos']):
        curr['pos'][0] -= 1 
    elif key == "up":
        curr['rotate'] += 1
        if curr['rotate'] > 3:
            curr['rotate'] = 0
        curr['block'] = rotateBlock(Type, curr['pos'], curr['rotate'])
    elif key == "down":
        downBlock(curr['block'], curr['pos'])
        isDown = True

    drawBlock(curr['block'], curr['pos'])
    mapPrint()

import threading

# 백그라운드에서 키 입력을 감지하도록 스레드 분기
def start_listener():
    listen_keyboard(on_press=on_press)

listener_thread = threading.Thread(target=start_listener, daemon=True)
listener_thread.start()

# 메인 게임 루프
try:
    while isRunning:
        isDown = False
        if curr['pos'][1] + len(curr['block']) == 16 or isCollision(curr['block'], curr['pos']):
            drawBlock(curr['block'], curr['pos'])
            complete()

            Type = random.randint(1, 7)
            curr = {'block' : blocks[Type], 'pos' : [3, 0], 'rotate' : 0}
            if isOver(curr['block'], curr['pos']):
                print("게임 오버")
                isRunning = False
                break

        drawBlock(curr['block'], curr['pos'])
        mapPrint()

        time.sleep(1)

        # 아래로 한 칸 떨어뜨리기
        if not isDown:
            eraseBlock(curr['block'], curr['pos'])
            curr['pos'][1] += 1
finally:
    stop_listening()