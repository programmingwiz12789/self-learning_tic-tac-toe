import pygame
import random
from tkinter import messagebox

def Win(board, player):
    d1Cnt = 0
    d2Cnt = 0
    for i in range(BOARD_SIZE):
        rowCnt = 0
        colCnt = 0
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                rowCnt += 1
            if board[j][i] == player:
                colCnt += 1
        if rowCnt == BOARD_SIZE or colCnt == BOARD_SIZE:
            return True
    for i in range(BOARD_SIZE):
        if board[i][i] == player:
            d1Cnt += 1
        if board[i][BOARD_SIZE - 1 - i] == player:
            d2Cnt += 1
    if d1Cnt == 3 or d2Cnt == 3:
        return True
    return False

def Draw(board):
    if not Win(board, 'X') and not Win(board, 'O'):
        empties = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == '':
                    empties += 1
        return empties == 0
    return False

def GameOver(board):
    return Win(board, 'O') or Win(board, 'X') or Draw(board)

def Reset():
    global board, epsilon, stateSpace
    board = []
    for i in range(BOARD_SIZE):
        temp = []
        for j in range(BOARD_SIZE):
            temp.append('')
        board.append(temp)
    if mode == 1:
        epsilon -= 1 / stateSpace

def ResetAll():
    global board, epsilon, Q, iterations, wins, losses, draws
    board = []
    for i in range(BOARD_SIZE):
        temp = []
        for j in range(BOARD_SIZE):
            temp.append('')
        board.append(temp)
    epsilon = 0.9
    Q = []
    for s in range(stateSpace):
        temp = []
        for a in range(actionSpace):
            temp.append(0)
        Q.append(temp)
    iterations = 0
    wins = 0
    losses = 0
    draws = 0

def Reward(board):
    if Win(board, 'O'):
        return WIN_SCORE
    elif Win(board, 'X'):
        return LOSS_SCORE
    elif Draw(board):
        return DRAW_SCORE
    else:
        OWins = 0
        OD1Bool = True
        OD2Bool = True
        XWins = 0
        XD1Bool = True
        XD2Bool = True
        for i in range(BOARD_SIZE):
            ORowBool = True
            OColBool = True
            XRowBool = True
            XColBool = True
            for j in range(BOARD_SIZE):
                if board[i][j] == 'X':
                    ORowBool = False
                elif board[i][j] == 'O':
                    XRowBool = False
                if board[j][i] == 'X':
                    OColBool = False
                elif board[j][i] == 'O':
                    XColBool = False
            if ORowBool:
                OWins += 1
            if OColBool:
                OWins += 1
            if XRowBool:
                XWins += 1
            if XColBool:
                XWins += 1
        for i in range(BOARD_SIZE):
            if board[i][i] == 'X':
                OD1Bool = False
            elif board[i][i] == 'O':
                XD1Bool = False
            if board[i][BOARD_SIZE - 1 - i] == 'X':
                OD2Bool = False
            elif board[i][BOARD_SIZE - 1 - i] == 'O':
                XD2Bool = False
        if OD1Bool:
            OWins += 1
        if OD2Bool:
            OWins += 1
        if XD1Bool:
            XWins += 1
        if XD2Bool:
            XWins += 1
        return OWins - XWins

def GetState(board):
    value = 0
    base = 1
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            val = 0
            if board[i][j] == 'X':
                val = 1
            elif board[i][j] == 'O':
                val = 2
            value += base * val
            base *= 3
    return value

def Action(mode, Q, state, actions):
    action = -1
    max_q = -INF
    for a in range(len(Q[state])):
        if board[actions[a][0]][actions[a][1]] == '':
            if Q[state][a] > max_q:
                max_q = Q[state][a]
                action = a
    if mode == 1 and random.uniform(0, 1) < epsilon:
        action = actions.index(RandomMove(board, actions))
    return action

def RandomMove(board, actions):
    legalActions = []
    for action in actions:
        if board[action[0]][action[1]] == '':
            legalActions.append(action)
    index = random.randint(0, len(legalActions) - 1)
    move = legalActions[index]
    return move

# def Minimax(depth, board, isMax):
#     if depth == DEPTH or Win(board, 'O') or Win(board, 'X') or Draw(board):
#         score = -Reward(board) - depth
#         return score
#     else:
#         if isMax:
#             bestScore = -INF
#             for i in range(BOARD_SIZE):
#                 for j in range(BOARD_SIZE):
#                     if board[i][j] == '':
#                         board[i][j] = 'X'
#                         bestScore = max(bestScore, Minimax(depth + 1, board, not isMax))
#                         board[i][j] = ''
#             return bestScore
#         else:
#             bestScore = INF
#             for i in range(BOARD_SIZE):
#                 for j in range(BOARD_SIZE):
#                     if board[i][j] == '':
#                         board[i][j] = 'O'
#                         bestScore = min(bestScore, Minimax(depth + 1, board, not isMax))
#                         board[i][j] = ''
#             return bestScore

# def BestMove(board):
#     bestScore = -INF
#     bestRow = -1
#     bestCol = -1
#     for i in range(BOARD_SIZE):
#         for j in range(BOARD_SIZE):
#             if board[i][j] == '':
#                 board[i][j] = 'X'
#                 score = Minimax(0, board, False)
#                 board[i][j] = ''
#                 if score > bestScore:
#                     bestScore = score
#                     bestRow = i
#                     bestCol = j
#     return bestRow, bestCol

def AIMove(mode, actions):
    global state, nextState, action
    state = GetState(board)
    action = Action(mode, Q, state, actions)
    row = actions[action][0]
    col = actions[action][1]
    board[row][col] = 'O'
    reward = Reward(board)
    nextState = GetState(board)
    Q[state][action] = Q[state][action] + alpha * (reward + gamma * max(Q[nextState]) - Q[state][action])

def UpdateQTable(state, nextState, action, reward):
    Q[state][action] = Q[state][action] + alpha * (reward + gamma * max(Q[nextState]) - Q[state][action])

pygame.init()
pygame.display.set_caption('Self-Learning Tic-Tac-Toe')
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
BUTTON_WIDTH = 51
BUTTON_HEIGHT = 51
BUTTON_BORDER_WIDTH = 1
BUTTON_BCOLOR = (255, 255, 0)
FCOLOR = (0, 0, 0)
BUTTON_FONT = pygame.font.SysFont('Sans Serif', 50)
BUTTON_TEXT_OFFSET = 11
BLANK = BUTTON_FONT.render('', True, FCOLOR)
X = BUTTON_FONT.render('X', True, FCOLOR)
O = BUTTON_FONT.render('O', True, FCOLOR)
BOARD_SIZE = 3
# DEPTH = BOARD_SIZE ** 2
# DEPTH = 2
WIN_SCORE = 1000
LOSS_SCORE = -1000
DRAW_SCORE = 0
INF = 1e9
INFO_FONT_SIZE = 23
INFO_FONT = pygame.font.SysFont('Sans Serif', INFO_FONT_SIZE)
INFO_TEXT_OFFSET = 5
INSTRUCTION_FONT_SIZE = 20
INSTRUCTION_FONT = pygame.font.SysFont('Sans Serif', INSTRUCTION_FONT_SIZE)
INSTRUCTION_TEXT_OFFSET = 5
CHANGE_MODE_TEXT = INSTRUCTION_FONT.render('Right Mouse Click to switch between playing mode and training mode', True, FCOLOR)
RESET_ALL_TEXT = INSTRUCTION_FONT.render('Press R to reset the training process (only available in playing mode)', True, FCOLOR)

board = []
for i in range(BOARD_SIZE):
    temp = []
    for j in range(BOARD_SIZE):
        temp.append('')
    board.append(temp)
buttons = []
for i in range(BOARD_SIZE):
    temp = []
    for j in range(BOARD_SIZE):
        temp.append(None)
    buttons.append(temp)

epsilon = 0.9
alpha = 0.01
gamma = 0.6
state = -1
nextState = -1
action = -1
actions = []
for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
        actions.append((i, j))
stateSpace = 3 ** (BOARD_SIZE ** 2)
actionSpace = len(actions)
Q = []
for s in range(stateSpace):
    temp = []
    for a in range(actionSpace):
        temp.append(0)
    Q.append(temp)

running = True
mode = 0
iterations = 0
wins = 0
losses = 0
draws = 0
while running:
    if mode == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    b = False
                    for i in range(BOARD_SIZE):
                        for j in range(BOARD_SIZE):
                            if board[i][j] == '':
                                if buttons[i][j].collidepoint(event.pos):
                                    if not GameOver(board):
                                        board[i][j] = 'X'
                                    if not GameOver(board):
                                        AIMove(mode, actions)
                                    b = True
                                    break
                        if b:
                            break
                elif event.button == 3:
                    mode = 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                ResetAll()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mode = 0
        move = RandomMove(board, actions)
        if not GameOver(board):
            board[move[0]][move[1]] = 'X'
        # bestRow, bestCol = BestMove(board)
        # if not GameOver(board):
        #     board[bestRow][bestCol] = 'X'
        if not GameOver(board):
            AIMove(mode, actions)
    screen.fill((255, 0, 0))
    textOffset = INSTRUCTION_TEXT_OFFSET
    screen.blit(CHANGE_MODE_TEXT, (INSTRUCTION_TEXT_OFFSET, textOffset))
    textOffset += INSTRUCTION_FONT_SIZE + INSTRUCTION_TEXT_OFFSET
    screen.blit(RESET_ALL_TEXT, (INSTRUCTION_TEXT_OFFSET, textOffset))
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            topLeftX = (SCREEN_WIDTH // 2) + BUTTON_WIDTH * (-1.5 + j)
            topLeftY = (SCREEN_HEIGHT // 2) + BUTTON_HEIGHT * (-1.5 + i)
            rect = pygame.Rect(topLeftX, topLeftY, BUTTON_WIDTH - BUTTON_BORDER_WIDTH, BUTTON_HEIGHT - BUTTON_BORDER_WIDTH)
            buttons[i][j] = rect
            pygame.draw.rect(screen, BUTTON_BCOLOR, rect)
            text = None
            if board[i][j] == 'X':
                text = X
            elif board[i][j] == 'O':
                text = O
            else:
                text = BLANK
            screen.blit(text, (topLeftX + BUTTON_TEXT_OFFSET, topLeftY + BUTTON_TEXT_OFFSET))
    iterationsText = INFO_FONT.render("Iterations: " + str(iterations), True, FCOLOR)
    winsText = INFO_FONT.render("Wins: " + str(wins), True, FCOLOR)
    lossesText = INFO_FONT.render("Losses: " + str(losses), True, FCOLOR)
    drawsText = INFO_FONT.render("Draws: " + str(draws), True, FCOLOR)
    textOffset = INFO_TEXT_OFFSET
    btn = buttons[BOARD_SIZE - 1][0]
    screen.blit(iterationsText, (btn.left, btn.top + btn.height + textOffset))
    textOffset += INFO_FONT_SIZE + INFO_TEXT_OFFSET
    screen.blit(winsText, (btn.left, btn.top + btn.height + textOffset))
    textOffset += INFO_FONT_SIZE + INFO_TEXT_OFFSET
    screen.blit(lossesText, (btn.left, btn.top + btn.height + textOffset))
    textOffset += INFO_FONT_SIZE + INFO_TEXT_OFFSET
    screen.blit(drawsText, (btn.left, btn.top + btn.height + textOffset))
    pygame.display.update()
    if Win(board, 'O'):
        if mode == 0:
            messagebox.showinfo('Game Over', 'O wins !')
        wins += 1
        iterations += 1
        Reset()
    elif Win(board, 'X'):
        if mode == 0:
            messagebox.showinfo('Game Over', 'X wins !')
        losses += 1
        iterations += 1
        UpdateQTable(state, nextState, action, LOSS_SCORE)
        Reset()
    elif Draw(board):
        if mode == 0:
            messagebox.showinfo('Game Over', 'Draw !')
        draws += 1
        iterations += 1
        UpdateQTable(state, nextState, action, DRAW_SCORE)
        Reset()
    
pygame.quit()