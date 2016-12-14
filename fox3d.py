#!/usr/bin/env python3
#-*- coding:utf-8 -*-

######################
# Foxenstein Raycaster
# Spiralwise - 2016
#
# This raycaster is inspired by http://lodev.org/cgtutor/raycasting.html
######################

import pygame
from pygame.locals import *
from math import inf, sqrt

DUMMY_MAP = [
	[1, 1, 1, 1, 1, 1],
	[1, 1, 0, 0, 1, 1],
	[1, 1, 0, 0, 1, 1],
	[1, 0, 0, 0, 0, 1],
	[1, 0, 1, 0, 1, 1],
	[1, 1, 1, 1, 1, 1]
]
BLOCK_SIZE = 64
SCREEN_DISTANCE = 10
SCREEN_SIZE = (640, 480)
RESOLUTION = 480
FOCAL_LENGTH = 0.3

COLOR = {
	'BLACK': (0, 0, 0),
	'WHITE': (255, 255, 255),
	'WALL': (196, 196, 0),
	'CEIL': (0, 127, 127),
	'FLOOR': (96, 96, 127)
}
WALL_HEIGHT = SCREEN_SIZE[1]/3
WALL_HEIGHT_DEMI = WALL_HEIGHT/2
HORIZONT_LINE = SCREEN_SIZE[1]/2

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Foxenstein 3D")

Player = {
	'pos': [BLOCK_SIZE*2, BLOCK_SIZE*2],
	'dir': [0.0, -1.0]
}

Camera = {
	'dir': [0.66, 0]
}


# Cast a ray to the nearest wall and returns the length
# input x: x-screen pixel
def hit_wall(x):

	hit = False

	blockHit = [int(Player['pos'][0]/BLOCK_SIZE),
		int(Player['pos'][1]/BLOCK_SIZE)]

	rayDir = [0.0, 0.0]
	cameraX = 2 * x / SCREEN_SIZE[0] -1
	rayDir[0] = Player['dir'][0] + Camera['dir'][0] * cameraX
	rayDir[1] = Player['dir'][1] + Camera['dir'][1] * cameraX

	delta = [0.0, 0.0]
	if rayDir[0] == 0.0:
		delta[0] = inf
	else:
		rayRatio = (rayDir[1] * rayDir[1]) / (rayDir[0] * rayDir[0])
		delta[0] = sqrt(1 + rayRatio)
	if rayDir[1] == 0.0:
		delta[1] = inf
	else:
		rayRatio = (rayDir[0] * rayDir[0]) / (rayDir[1] * rayDir[1])
		delta[1] = sqrt(1 + rayRatio)

	step = [0, 0]
	sideHitDist = [0.0, 0.0]
	if Player['dir'][0] > 0:
		sideHitDist[0] = (blockHit[0]+1)*BLOCK_SIZE - Player['pos'][0]
		sideHitDist[0] *= delta[0]
		step[0] = 1
	else:
		sideHitDist[0] = Player['pos'][0] - blockHit[0]*BLOCK_SIZE
		sideHitDist[0] *= delta[0]
		step[0] = -1
	if Player['dir'][1] > 0:
		sideHitDist[1] = (blockHit[1]+1)*BLOCK_SIZE - Player['pos'][1]
		sideHitDist[1] *= delta[1]
		step[1] = 1
	else:
		sideHitDist[1] = Player['pos'][1] - blockHit[1]*BLOCK_SIZE
		sideHitDist[1] *= delta[1]
		step[1] = -1

	while not hit:
		if sideHitDist[0] < sideHitDist[1]:
			sideHitDist[0] += delta[0]
			blockHit[0] += step[0]
			side = 0
		else:
			sideHitDist[1] += delta[1]
			blockHit[1] += step[1]
			side = 1
		if (DUMMY_MAP[blockHit[0]][blockHit[1]] > 0):
			hit = True

	if side:
		distance = sideHitDist[1]
	else:
		distance = sideHitDist[0]

	return distance


def draw_wall(x, distance):
	perceivedHeight = int(WALL_HEIGHT/distance)
	pygame.draw.line(screen,
		COLOR['WALL'],
		(x, (perceivedHeight + SCREEN_SIZE[1]/2)),
		(x, (-perceivedHeight + SCREEN_SIZE[1]/2)))


running = True
while running:
	screen.fill(COLOR['BLACK'])
	pygame.draw.rect(screen, COLOR['CEIL'], (1, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]/2))
	pygame.draw.rect(screen, COLOR['FLOOR'], (0, SCREEN_SIZE[1]/2, SCREEN_SIZE[0], SCREEN_SIZE[1]/2))
	for col in range(SCREEN_SIZE[0]):
		draw_wall(col, hit_wall(col))

	pygame.display.flip()

	for event in pygame.event.get():
		if event.type == QUIT:
			break
		elif event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
