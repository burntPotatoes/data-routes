import time
import sys
import pygame
from pygame import gfxdraw

# display: name of the pygame screen
# st_pos: starting position in the form [x pixel coordinate, y pixel coordinate]
# b_len: pixel length of border, must be at least 1
# num: how many lines to draw in the form [vertical lines, horizontal lines], must be at least 2
# col: colour of the lines
def draw_grid(display, st_pos, b_len, num, col, paths):
    # input check
    if b_len[0] < 1 or b_len[1] < 1 or num[0] < 2 or num[1] < 2:
        raise ValueError('draw_grid() called with invalid arguments for length or number of lines')

    # lock screen, this might make it faster to draw stuff? idk
    display.lock()
    # separation for vertical, horizontal lines
    sep = [b_len[0] / num[0], b_len[1] / num[1]]

    # vertical lines
    for i in range(num[0] + 1):
        pygame.draw.line(display, col, (int(st_pos[0] + sep[0] * i), int(st_pos[1])),
                         (int(st_pos[0] + sep[0] * i), int(st_pos[1] + sep[1] * num[1])))
    # horizontal lines
    for i in range(num[1] + 1):
        pygame.draw.line(display, col, (int(st_pos[0]), int(st_pos[1] + sep[1] * i)),
                         (int(st_pos[0] + sep[0] * num[0]), int(st_pos[1] + sep[1] * i)))
    display.unlock()

    # draw path numbers
    for i in range(len(paths)):  # columns
        cur_pos = [int(st_pos[0] + sep[0] * i + 4), int(st_pos[1] - 8)]
        for j in range(len(paths[i])):  # rows
            cur_pos[1] = int(st_pos[1] + j * sep[1] - 8)
            if paths[i][j] > 0:
                create_text(display, cur_pos, str(paths[i][j]), False, smolFont, (25, 25, 150))

    # starting and ending circles
    pygame.draw.circle(screen, (25, 200, 25), st_pos, 5)
    pygame.draw.circle(screen, (200, 25, 25), (int(st_pos[0] + sep[0] * num[0]),
                                               int(st_pos[1] + sep[1] * num[1])), 5)


# creates some text centered on an x y coordinate
def create_text(display, location, text, centered, font, col):
    display_text = font.render(str(text), True, col)
    text_rect = display_text.get_rect()
    if centered:
        display.blit(display_text, (location[0] - text_rect[2] // 2, location[1] - text_rect[3] // 2))
    else:
        display.blit(display_text, (location[0], location[1] - text_rect[3] // 2))


# creates a 2d array based on the lines and obstacles (obstacles WIP)
# lines is [vertical, horizontal liens]
def update_moves(lines, obs):
    # initialize list. -1 means it cannot be travelled to
    final_list = [[0 for j in range(lines[1] + 1)] for i in range(lines[0] + 1)]
    # first value (starting point)
    final_list[0][0] = 1

    # calculations! :D
    for i in range(len(final_list)):
        for j in range(len(final_list[i])):
            # if its on the edge, only add the one before it
            if final_list[i][j] == 0:
                # free node: no blocks
                if [2 * i, j - 1] not in obs and [2 * i - 1, j] not in obs and i > 0 and j > 0:
                    final_list[i][j] = final_list[i - 1][j] + final_list[i][j - 1]
                # left edge or top blocker
                elif (i == 0 or [2 * i - 1, j] in obs) and [2 * i, j - 1] not in obs:
                    final_list[i][j] = final_list[i][j - 1]
                # top edge or left blocker
                elif (j == 0  or [2 * i, j - 1] in obs) and [2 * i - 1, j] not in obs:  # upper edge
                    final_list[i][j] = final_list[i - 1][j]

    return final_list


# creates a list of rect objects for the barriers
# list of 2n + 1 columns [column][row]
# each column has n (even) or n+1 buttons
def update_obs_buttons(pos, length, num):
    # list of buttons [pygame.Rect object]
    but_list = [[] for i in range(num[0] * 2 + 1)]
    # separation distance between buttons
    sep = [length[0] / num[0], length[1] / num[1]]

    # loop :D
    for i in range(num[0] * 2 + 1):
        # vertical barriers
        if i % 2 == 0:
            but_list[i] = [pygame.Rect(int(sep[0] * i // 2 + pos[0]) - 5, int(sep[1] * (j + 0.5) + pos[1]) - 5, 11, 11)
                           for j in range(num[1])]
        # horizontal barriers
        else:
            but_list[i] = [pygame.Rect(int(sep[0] * (i // 2 + 0.5) + pos[0]) - 5, int(sep[1] * j + pos[1]) - 5, 11, 11)
                           for j in range(num[1] + 1)]

    return but_list


# ---- SETUP ----

# setup pygame
pygame.init()
pygame.font.init()
time.sleep(0.5)

# setup display and clock
clock = pygame.time.Clock()
disL = 1000
disH = 700
screen = pygame.display.set_mode((disL, disH))
pygame.display.set_caption("Route-simulation")

# images
imgPlus = pygame.image.load("plus-sign.png").convert_alpha()
imgMinus = pygame.image.load("minus-sign.png").convert_alpha()

# fonts
defFont = pygame.font.SysFont('Trebuchet MS', 24, False)
smolFont = pygame.font.SysFont('Trebuchet MS', 18, False)

# colours
colInc = [220, 220, 220]
colDec = [220, 220, 220]
colGrid = [0, 0, 0]
colBox = [125, 125, 125]

# variables
# i/o variables
mousePos = []

# general map variables
mapPos = [40, 40]
mapLen = [620, 620]  # width, height
numLines = [4, 4]  # vertical, horizontal lines

# obstacles button
butObsList = update_obs_buttons(mapPos, mapLen, numLines)
selObsList = []

# obstacles and path
nPath = update_moves(numLines, selObsList)  # 2d array of the number of moves to every location

# button rect objects
# increase/decrease number of vertical lines (min 2)
butDecVert = pygame.Rect(800, disH // 2 - 125, 50, 50)
butIncVert = pygame.Rect(875, disH // 2 - 125, 50, 50)
# increase/decrease number of horizontal lines (min 2)
butDecHor = pygame.Rect(800, disH // 2 + 100, 50, 50)
butIncHor = pygame.Rect(875, disH // 2 + 100, 50, 50)

listOfBut = [butDecVert, butIncVert, butDecHor, butIncHor]  # list for easier access

# ---- LOOP ----
while True:
    # should make it 60FPS max
    clock.tick(60)

    # get input
    mousePressed = [0, 0, 0]  # reset mouse presses
    mousePos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousePressed = pygame.mouse.get_pressed()

    # background
    screen.fill((250, 250, 250))

    # main grid and path numbers
    draw_grid(screen, mapPos, mapLen, numLines, colGrid, nPath)

    # draw barrier squares
    for i in range(len(butObsList)):
        for j in range(len(butObsList[i])):
            # if it has NOT been selected, don't fill it
            if [i, j] not in selObsList:
                pygame.draw.rect(screen, colBox, butObsList[i][j], 1)
            else:
                pygame.draw.rect(screen, colGrid, butObsList[i][j])
            # if mouse button is pressed and its selected, add it to da list
            if mousePressed[0] == 1 and butObsList[i][j].collidepoint(mousePos[0], mousePos[1]):
                if [i, j] not in selObsList:
                    selObsList.append([i, j])
                else:  # delete if its already there (toggle)
                    del (selObsList[selObsList.index([i, j])])
                # update pathing
                butObsList = update_obs_buttons(mapPos, mapLen, numLines)
                nPath = update_moves(numLines, selObsList)

    # draw buttons
    for i in range(len(listOfBut)):
        if i % 2 == 0:  # red decrease
            pygame.draw.rect(screen, colDec, listOfBut[i])
            screen.blit(imgMinus, (listOfBut[i][0], listOfBut[i][1]))
        else:  # green increase
            pygame.draw.rect(screen, colInc, listOfBut[i])
            screen.blit(imgPlus, (listOfBut[i][0], listOfBut[i][1]))
        pygame.draw.rect(screen, (0, 0, 0), listOfBut[i], 1)

    # display num rows and columns
    create_text(screen, (butIncVert[0] - 15, butIncVert[1] - 25),
                "Length: " + str(numLines[0]), True, defFont, (0, 0, 0))
    create_text(screen, (butIncHor[0] - 15, butIncHor[1] - 25),
                "Height: " + str(numLines[1]), True, defFont, (0, 0, 0))

    # increase and decrease number of rows and columns
    for i in range(len(listOfBut)):
        if listOfBut[i].collidepoint(mousePos[0], mousePos[1]):
            pygame.draw.rect(screen, (0, 0, 0), listOfBut[i], 3)
            if mousePressed[0] == 1:  # USER PRESSED BUTTON AAAH
                # dec ver, inc ver, dec hor, inc hor
                if i == 0 and numLines[0] > 2:
                    numLines[0] -= 1
                elif i == 1:
                    numLines[0] += 1
                elif i == 2 and numLines[1] > 2:
                    numLines[1] -= 1
                elif i == 3:
                    numLines[1] += 1
                # update pathing
                butObsList = update_obs_buttons(mapPos, mapLen, numLines)
                nPath = update_moves(numLines, selObsList)

    # update display!
    pygame.display.update()
