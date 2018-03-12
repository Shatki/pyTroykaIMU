# -*- coding: utf-8 -*-
import pygame, sys, os, time
from lis3mdl import LIS3MDL
from pygame.locals import *

rotation = 0

def lis3_read():
    global rotation

    # calibration data
    compass.calibration_matrix = [
        [1.259098, 0.013830, 0.039295],
        [0.01380, 1.245928, -0.018922],
        [0.039295, -0.018922, 1.360489],
    ]
    compass.bias = [11.16, -43.55, -52.62]

    # while True:
    #    rotation = 360 - compass.heading()
    #    time.sleep(0.1)

compass = LIS3MDL()

FPS = 25
WINDOWWIDTH = 1024
WINDOWHEIGHT = 768
CELLSIZE = 32
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('LIS3MDL')

    # thread.start_new_thread(hmc5883l_read,())
    while True:
        runGame()

def read_compass():
    compass

    return


def runGame():
    global rotation

    titleFont = pygame.font.Font('freesansbold.ttf', 50)
    titleSurf1 = titleFont.render('LIS3MDL', True, WHITE)
    img = pygame.image.load(os.path.join('images','compas.png'))
    imgx = 10
    imgy = 10

    while True: # main game loop
        for event in pygame.event.get():        # event handling loop
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if event.key == pygame.K_LEFT:
                    rotation -= 10 # degrees
                if event.key == pygame.K_RIGHT:
                    rotation += 10 # degrees

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()

        rotatedSurf1 = pygame.transform.rotate(img, rotation)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()