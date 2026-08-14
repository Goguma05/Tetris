import time, random
import sys, tty, termios, select

# 논블로킹 키 입력을 위한 함수
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    ch = None
    try:
        # 터미널을 raw 모드로 전환 (엔터 없이 즉시 입력 받기 위함)
        tty.setraw(fd)
        
        # select를 이용해 입력이 있는지 0.01초 동안 대기
        rlist, _, _ = select.select([sys.stdin], [], [], 1)
        if rlist:
            ch = sys.stdin.read(1)
            # ESC 문자(\x1b)인 경우 뒤에 오는 방향키 코드 2바이트를 마저 읽음
            if ch == '\x1b':
                ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

isRunning = True
map = [[0 for _ in range(8)] for _ in range(16)]

blocks = {
    1 : [[1,1,1,1]], # I
    2 : [[1,1],      # o
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

def mapPrint():
    for _ in range(3):
        print()
    for p in map:
        print(p)
    for _ in range(2):
        print()

def drawBlock(block, pos, rotate):
    if rotate == 0:
        for i in range(len(block)):
            for j in range(len(block[0])):
                if block[i][j] == 1:
                    map[pos[1] + i][pos[0] + j] = block[i][j]
    if rotate == 1:
        for i in range(len(block[0])):
            for j in range(len(block) - 1, -1, -1):
                if block[j][i] == 1:
                    map[pos[1] + i][pos[0] + j] = block[j][i]
    if rotate == 2:
        for i in range(len(block) - 1, -1, -1):
            for j in range(len(block[0]) - 1, -1, -1):
                if block[i][j] == 1:
                    map[pos[1] + 1 - i][pos[0] + j] = block[i][j]
    if rotate == 3:
        for i in range(len(block[0])):
            for j in range(len(block)):
                if block[j][i] == 1:
                    map[pos[1] + i][pos[0] + j] = block[j][i]

def eraseBlock(block, pos, rotate):
    if rotate == 0:
        for i in range(len(block)):
            for j in range(len(block[0])):
                map[pos[1] + i][pos[0] + j] = 0
    if rotate == 1:
        for i in range(len(block[0])):
            for j in range(len(block) - 1, -1, -1):
                map[pos[1] + i][pos[0] + j] = 0
    if rotate == 2:
        for i in range(len(block) - 1, -1, -1):
            for j in range(len(block[0]) - 1, -1, -1):
                map[pos[1] + 1 - i][pos[0] + j] = 0
    if rotate == 3:
        for i in range(len(block[0])):
            for j in range(len(block)):
                map[pos[1] + i][pos[0] + j] = 0

def isCollision(block, pos):
    hit = []
    for i in range(len(block[0])):
        Max = 0
        for j in range(len(block)):
            if block[j][i] == 1:
                Max = j
        hit.append(Max)
    
    for i in range(len(hit)):
        if map[pos[1] + hit[i] + 1][pos[0] + i] == 1:
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

curr = {'block' : blocks[random.randint(1,7)], 'pos' : [3, 0], 'rotate' : 0}


while isRunning:
    if curr['pos'][1] + len(curr['block']) == 16 or isCollision(curr['block'], curr['pos']):
        drawBlock(curr['block'], curr['pos'], curr['rotate'])
        curr = {'block' : blocks[random.randint(1,7)], 'pos' : [3, 0], 'rotate' : 0}

    # 1. 현재 위치에 블록 그리기 및 출력
    drawBlock(curr['block'], curr['pos'], curr['rotate'])
    mapPrint()

    # 2. 1초 동안 0.05초 간격으로 키 입력을 반복 감지
    start_time = time.time()
    while time.time() - start_time < 0.8:
        key = getch()
        
        if key is not None:
            # ESC 종료
            if key == 27:
                print("게임을 종료합니다.")
                isRunning = False
                break
            
            # 기존 위치 지우기
            eraseBlock(curr['block'], curr['pos'], curr['rotate'])
            
            if key == '\x1b[C': # 오른쪽
                if isRightWall(curr['block'], curr['pos']):
                    curr['pos'][0] += 1
            elif key == '\x1b[D': # 왼쪽
                if isLeftWall(curr['block'], curr['pos']):
                    curr['pos'][0] -= 1
            elif key == '\x1b[A': # 위쪽
                curr['rotate'] += 1
                if curr['rotate'] > 3:
                    curr['rotate'] = 0
            elif key == '\x1b[B': # 아래쪽 빠르게
                pass
            
            # 이동 후 다시 그리고 출력
            drawBlock(curr['block'], curr['pos'], curr['rotate'])
            mapPrint()
            
        time.sleep(0.05)

    # 3. 1초 경과 후 아래로 한 칸 떨어뜨리기
    eraseBlock(curr['block'], curr['pos'], curr['rotate'])
    curr['pos'][1] += 1

# 1. 로테이션 후 바닥과 벽 충돌 계산
# 2. 아래키 완성
# 3. 완성된 줄 감지와 삭제
# 4. 게임 오버
# 5. 점수 출력
# 6. 난이도 조정