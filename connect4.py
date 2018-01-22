import sys
import math
import numpy as np
import pygame

COLUMN_COUNT = 7
ROW_COUNT = 6
DIFFICULTY_LVL = 8

SQUARESIZE = 100
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT+1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
RADIUS = int(SQUARESIZE/2 - 5)
BG_COLOR = (0,102,204)
EMPTY_CASE = (32, 32, 32)
P1_PIECE = (240, 40, 40)
P2_PIECE = (220, 200, 30)
HUMAN_PLAYER = 1
AI_PLAYER = 2

def score_pawns(pawns, player):
    return (pawns * 2 * player) + (pawns / 2)

def is_full(board):
    for col in range(COLUMN_COUNT):
        if is_valid(board, col):
            return False
    return True

def count_pawns(board):
    return np.count_nonzero(board)

def evaluation(board):
    if check_win(board, AI_PLAYER):
        return 999999 + count_pawns(board)
    elif is_full(board):
        return 0
    elif check_win(board, HUMAN_PLAYER):
        return -999999 - count_pawns(board)
    else:
        score = 0

        for col in range(COLUMN_COUNT-3):
            for row in range(ROW_COUNT):
                pawns = 0
                player = 0
                for i in range(3):
                    if board[row][col+i] != 0:
                        pawns += 1
                        player = board[row][col+i] == AI_PLAYER and player + 1 or player - 1
                score += score_pawns(pawns, player)

        for col in range(COLUMN_COUNT):
            for row in range(ROW_COUNT-3):
                pawns = 0
                player = 0
                for i in range(3):
                    if board[row+i][col] != 0:
                        pawns += 1
                        player = board[row+i][col] == AI_PLAYER and player + 1 or player - 1
                score += score_pawns(pawns, player)

        for col in range(COLUMN_COUNT-3):
            for row in range(ROW_COUNT-3):
                pawns = 0
                player = 0
                for i in range(3):
                    if board[row+i][col+i] != 0:
                        pawns += 1
                        player = board[row+i][col+i] == AI_PLAYER and player + 1 or player - 1
                score += score_pawns(pawns, player)

        for col in range(COLUMN_COUNT-3):
            for row in range(3, ROW_COUNT):
                pawns = 0
                player = 0
                for i in range(3):
                    if board[row-i][col+i] != 0:
                        pawns += 1
                        player = board[row-i][col+i] == AI_PLAYER and player + 1 or player - 1
                score += score_pawns(pawns, player)

        return score

def calc_max(board, depth, alpha, beta):
    if depth == 0 or check_win(board, HUMAN_PLAYER) or check_win(board, AI_PLAYER):
        return evaluation(board)
    for col in range(COLUMN_COUNT):
        if is_valid(board, col):
            board = drop_piece(board, get_row(board, col), col, actualPlayer)
            tmp = calc_min(board, depth -1, alpha, beta)
            board = cancel(board, col)
            if alpha < tmp:
                alpha = tmp
            if beta <= alpha:
                return alpha
    return alpha

def calc_min(board, depth, alpha, beta):
    if depth == 0 or check_win(board, HUMAN_PLAYER) or check_win(board, AI_PLAYER):
        return evaluation(board)
    for col in range(COLUMN_COUNT):
        if is_valid(board, col):
            board = drop_piece(board, get_row(board, col), col, actualPlayer)
            tmp = calc_max(board, depth -1, alpha, beta)
            board = cancel(board, col)
            if beta > tmp:
                beta = tmp
            if beta <= alpha:
                return beta
    return beta

def block(board):
    for col in range(COLUMN_COUNT):
        if is_valid(board, col):
            board = drop_piece(board, get_row(board, col), col, HUMAN_PLAYER)
            if check_win(board, HUMAN_PLAYER):
                board = cancel(board, col)
                return col
            board = cancel(board, col)
    return None

def play(board, depth):
    bestCol = -1
    alpha = -1000000
    beta = 1000000
    if depth == 0 or check_win(board, HUMAN_PLAYER) or check_win(board, AI_PLAYER):
        return board
    for col in range(COLUMN_COUNT):
        if is_valid(board, col):
            board = drop_piece(board, get_row(board, col), col, actualPlayer)
            tmp = calc_min(board, depth -1, alpha, beta)
            if alpha < tmp:
                alpha = tmp
                bestCol = col
            board = cancel(board, col)
        print("Col " + str(col) + " = " + str(tmp))
    tmpBoard = board
    tmpBoard = drop_piece(tmpBoard, get_row(tmpBoard, bestCol), bestCol, AI_PLAYER)
    if check_win(tmpBoard, AI_PLAYER) == False and DIFFICULTY_LVL >= 5:
        tmpBoard = cancel(tmpBoard, bestCol)
        blockCol = block(board)
        if blockCol is not None:
            bestCol = int(blockCol)
    else:
        tmpBoard = cancel(tmpBoard, bestCol)
    board = drop_piece(board, get_row(board, bestCol), bestCol, AI_PLAYER)
    return board

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

def drop_piece(board, row, col, player):
    board[row][col] = player
    switch_player()
    return board

def switch_player():
    global actualPlayer
    actualPlayer = actualPlayer == HUMAN_PLAYER and AI_PLAYER or HUMAN_PLAYER

def cancel(board, col):
    row = ROW_COUNT - 1
    while board[row][col] == 0:
        row -= 1
    board[row][col] = 0
    switch_player()
    return board

def is_valid(board, col):
    if col < 0 or col > COLUMN_COUNT:
        return 0
    return board[ROW_COUNT - 1][col] == 0

def get_row(board, col):
    for row in range(ROW_COUNT):
        if board[row][col] == 0:
            return row

def check_win(board, p):
    for col in range(COLUMN_COUNT-3):
        for row in range(ROW_COUNT):
            if board[row][col] == p and board[row][col+1] == p and board[row][col+2] == p and board[row][col+3] == p:
                return True
    for col in range(COLUMN_COUNT):
        for row in range(ROW_COUNT-3):
            if board[row][col] == p and board[row+1][col] == p and board[row+2][col] == p and board[row+3][col] == p:
                return True
    for col in range(COLUMN_COUNT-3):
        for row in range(ROW_COUNT-3):
            if board[row][col] == p and board[row+1][col+1] == p and board[row+2][col+2] == p and board[row+3][col+3] == p:
                return True
    for col in range(COLUMN_COUNT-3):
        for row in range(3, ROW_COUNT):
            if board[row][col] == p and board[row-1][col+1] == p and board[row-2][col+2] == p and board[row-3][col+3] == p:
                return True
    return False

def print_board(board):
    print(np.flip(board, 0))
    print("\n")

def draw_board(board):
    for col in range(COLUMN_COUNT):
        for row in range(ROW_COUNT):
            pygame.draw.rect(screen, BG_COLOR, (col*SQUARESIZE, row*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, EMPTY_CASE, (int(col*SQUARESIZE+SQUARESIZE/2), int(row*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for col in range(COLUMN_COUNT):
        for row in range(ROW_COUNT):
            if board[row][col] == 1:
                pygame.draw.circle(screen, P1_PIECE, (int(col*SQUARESIZE+SQUARESIZE/2), height - int(row*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, P2_PIECE, (int(col*SQUARESIZE+SQUARESIZE/2), height - int(row*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

global actualPlayer
gameOver = False
turn = 0
actualPlayer = HUMAN_PLAYER

board = create_board()
pygame.init()
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)

screen = pygame.display.set_mode(SIZE)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("Monospace", 75)

while not gameOver:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, EMPTY_CASE, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if actualPlayer == 1:
                pygame.draw.circle(screen, P1_PIECE, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, EMPTY_CASE, (0, 0, width, SQUARESIZE))

            if actualPlayer % 2:
                posx = event.pos[0]
                print("Your turn:")
                col = int(math.floor(posx/SQUARESIZE))
                board = drop_piece(board, get_row(board, col), col, actualPlayer)
                print("You played column " + str(col) + ".")
                print_board(board)
                draw_board(board)
                if check_win(board, HUMAN_PLAYER):
                    print("Congrats player " + str(actualPlayer) + " ! You won !")
                    label = myfont.render("You won !", 1, P1_PIECE)
                    screen.blit(label, (40,10))
                    gameOver = True
                elif is_full(board):
                    print("Draw !")
                    label = myfont.render("Draw", 1, BG_COLOR)
                    screen.blit(label, (40,10))
                    gameOver = True

            if gameOver == False:
                print("Ai turn :")
                board = play(board, DIFFICULTY_LVL)
                print_board(board)
                if check_win(board, AI_PLAYER):
                    print("AI won !")
                    label = myfont.render("AI won !", 1, P2_PIECE)
                    screen.blit(label, (40,10))
                    gameOver = True
                elif is_full(board):
                    print("Draw !")
                    label = myfont.render("Draw", 1, BG_COLOR)
                    screen.blit(label, (40,10))
                    gameOver = True
            draw_board(board)
    turn += 1
    if gameOver:
        pygame.time.wait(3000)
