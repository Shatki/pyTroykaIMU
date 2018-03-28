# -*- coding: utf-8 -*-
import os
import sys
import pygame
from socket import *

# Setup your Raspberry Pi host first!
HOST = '192.168.0.76'
PORT = 21567
BUFSIZ = 128
ADDR = (HOST, PORT)

rotation = 0

FPS = 25
WINDOWWIDTH = 1024
WINDOWHEIGHT = 768
CELLSIZE = 32
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
BGCOLOR = BLACK


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('TroykaIMU magnetometer test')

    while True:
        runGame()


def read_compass():
    try:
        # читаем данные из сети
        data = tcpCliSock.recv(BUFSIZ)
        if data:
            # print(data)
            data = data.decode().split(';')
            return float(data[9])
    except:
        print("Server wasstoped. Demo finished")
        tcpCliSock.close()
        exit()
    return


def runGame():
    global rotation


    titleFont = pygame.font.Font('freesansbold.ttf', 50)
    titleSurf1 = titleFont.render('LIS3MDL', True, WHITE)
    img = pygame.image.load(os.path.join('images', 'compas.png'))
    imgx = 10
    imgy = 10

    while True:  # main game loop
        # читаем данные из сети
        rotation = read_compass()

        for event in pygame.event.get():  # event handling loop
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if event.key == pygame.K_LEFT:
                    rotation -= 10  # degrees
                if event.key == pygame.K_RIGHT:
                    rotation += 10  # degrees

        DISPLAYSURF.fill(BGCOLOR)

        drawGrid()

        rotatedSurf1 = pygame.transform.rotate(img, rotation)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


# Socket
try:
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)

except:
    print('Cannot set connection with Raspberry Pi dataServer')
finally:
    main()
