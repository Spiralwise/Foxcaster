#!/usr/bin/env python3
#-*- coding:utf-8 -*-

######################
# Foxenstein Raycaster
# Spiralwise - 2016
#
# This raycaster is inspired by http://lodev.org/cgtutor/raycasting.html
#
# TODO : Find a vector library for a more efficient vector manipulation
######################

import pygame
from pygame.locals import *
from math import *
from time import perf_counter

DUMMY_MAP = [
	[1, 1, 1, 1, 1, 1],
	[1, 3, 0, 0, 1, 1],
	[1, 3, 0, 0, 1, 1],
	[1, 0, 0, 0, 0, 1],
	[1, 0, 2, 0, 2, 1],
	[1, 1, 1, 1, 1, 1]
]
BLOCK_SIZE = 2
SCREEN_DISTANCE = 10
SCREEN_SIZE = (640, 480)
RESOLUTION = 480
FOCAL_LENGTH = 0.3
MAP_POS = [5, 5]
MAP_SIZE = 10

COLOR = {
	'BLACK': (0, 0, 0),
	'WHITE': (255, 255, 255),
	'WALL': [
		(196, 196, 0),
		(196, 32, 32),
		(32, 32, 196)
	],
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
	'pos': [BLOCK_SIZE*3, BLOCK_SIZE*3],
	'dir': [0.0, -1.0],
	'speed': 1.0,
	'rot_speed': 0.01,
	'move_state': 0,
	'turn_state': 0
}

Camera = {
	'dir': [1.0, 0.0]
}

Font = pygame.font.SysFont("monospace", 10)

#Texture = pygame.PixelArray(pygame.image.load("texture_test.png"))
Texture = pygame.image.load("texture_test.png")

def draw_minimap(distance):
	for y, row in enumerate(DUMMY_MAP):
		for x, square in enumerate(row):
			if square:
				pygame.draw.rect(screen
				, (200, 0, 0)
				, (MAP_POS[0]+MAP_SIZE*x
					, MAP_POS[1]+MAP_SIZE*y
					, MAP_SIZE, MAP_SIZE))
	pos_on_map_x = int(MAP_POS[0]+MAP_SIZE*(Player['pos'][0]/BLOCK_SIZE))
	pos_on_map_y = int(MAP_POS[1]+MAP_SIZE*(Player['pos'][1]/BLOCK_SIZE))
	pygame.draw.circle(screen
		, (0, 0, 200)
		, (pos_on_map_x, pos_on_map_y)
		, 3)
	pygame.draw.line(screen
		, (0, 0, 200)
		, (pos_on_map_x, pos_on_map_y)
		, (pos_on_map_x+Player['dir'][0]*6, pos_on_map_y+Player['dir'][1]*6))
	text = Font.render(str(Player["pos"])
	                   + ", "
	                   + str(Player["dir"])
					   + ", "
					   + str(distance), 1, (25, 25, 50))
	screen.blit(text, (10, SCREEN_SIZE[0]-200))

def display_framerate(framerate):
	text = Font.render(str(framerate), 1, (28, 28, 50))
	screen.blit(text, (10, 10))


def rotate_vector(vec, angle):
	rot_mtx = [
		[cos(angle), -sin(angle)],
		[sin(angle), cos(angle)]
	]
	vx = rot_mtx[0][0] * vec[0] + rot_mtx[0][1] * vec[1]
	vy = rot_mtx[1][0] * vec[0] + rot_mtx[1][1] * vec[1]
	return [vx, vy]


def hit_wall(x):
	'''Cast a ray to the nearest wall and returns the length

	   input x: x-screen pixel
	   output:
	   - length of the ray in units
	   - which side has been hit
	   - wall index
	   - wall impact position in ratio
	'''

	hit = False

	blockHit = [int(Player['pos'][0]/BLOCK_SIZE),
	            int(Player['pos'][1]/BLOCK_SIZE)]

	rayDir = [0.0, 0.0]
	cameraX = 2 * x / (SCREEN_SIZE[0]-1) -1
	rayDir[0] = Player['dir'][0] + Camera['dir'][0] * cameraX
	rayDir[1] = Player['dir'][1] + Camera['dir'][1] * cameraX

	delta = [0.0, 0.0]
	if rayDir[0] == 0.0:
		delta[0] = inf
	else:
		rayRatio = (rayDir[1] * rayDir[1]) / (rayDir[0] * rayDir[0])
		delta[0] = sqrt(1 + rayRatio) * BLOCK_SIZE
	if rayDir[1] == 0.0:
		delta[1] = inf
	else:
		rayRatio = (rayDir[0] * rayDir[0]) / (rayDir[1] * rayDir[1])
		delta[1] = sqrt(1 + rayRatio) * BLOCK_SIZE

	step = [0, 0]
	sideHitDist = [0.0, 0.0]
	if rayDir[0] > 0:
		sideHitDist[0] = blockHit[0]+1 - Player['pos'][0]/BLOCK_SIZE
		sideHitDist[0] *= delta[0]
		step[0] = 1
	else:
		sideHitDist[0] = Player['pos'][0]/BLOCK_SIZE - blockHit[0]
		sideHitDist[0] *= delta[0]
		step[0] = -1
	if rayDir[1] > 0:
		sideHitDist[1] = blockHit[1]+1 - Player['pos'][1]/BLOCK_SIZE
		sideHitDist[1] *= delta[1]
		step[1] = 1
	else:
		sideHitDist[1] = Player['pos'][1]/BLOCK_SIZE - blockHit[1]
		sideHitDist[1] *= delta[1]
		step[1] = -1

	while not hit:
		if sideHitDist[0] < sideHitDist[1]:
			distance = sideHitDist[0]
			sideHitDist[0] += delta[0]
			blockHit[0] += step[0]
			side = 0
		else:
			distance = sideHitDist[1]
			sideHitDist[1] += delta[1]
			blockHit[1] += step[1]
			side = 1
		if (DUMMY_MAP[blockHit[1]][blockHit[0]] > 0):
			hit = True

	distanceXY = (blockHit[side]-((step[side]-1)/2))*BLOCK_SIZE - Player['pos'][side]
	otherSide = 0 if side else 1
	wallHit = sqrt(distance*distance - distanceXY*distanceXY) * step[otherSide]
	wallHit += Player['pos'][otherSide] - blockHit[otherSide]*BLOCK_SIZE
	wallHit /= BLOCK_SIZE

	return distance, side, DUMMY_MAP[blockHit[1]][blockHit[0]], wallHit
	#FIXME Make it RayHit object

def draw_wall(x, rayhit):
	'''Draw a wall according to the distance to the player.
	   If the wall has a texture, it will be textured.

	   input x: vertical strip on screen
	   input rayhit
	'''

	perceivedHeight = int(WALL_HEIGHT/rayhit[0])
	if rayhit[2] == 3:
		texX = int(rayhit[3] * Texture.get_width())

		screen.blit(
		    pygame.transform.scale(Texture,
		                           (Texture.get_width(), perceivedHeight*2)),
		    (x, -perceivedHeight+SCREEN_SIZE[1]/2),
			(texX, 0, 1, perceivedHeight*2))
		#screen_array = pygame.PixelArray(screen)
		#for wallY in range(perceivedHeight*2):
		#	texY = int(wallY/(perceivedHeight*2) * (Texture.shape[1]-1))
		#	wallYCentered = int(wallY + SCREEN_SIZE[1]/2 - perceivedHeight)
		#	screen_array[x, wallYCentered] = Texture[texX, texY]
	else:
		color = COLOR['WALL'][rayhit[2]-1]
		if rayhit[1]:
			color = list(map(lambda x: x/2, color)) #NOTE Maybe use bitshifting?
		pygame.draw.line(screen,
			color,
			(x, (perceivedHeight + SCREEN_SIZE[1]/2)),
			(x, (-perceivedHeight + SCREEN_SIZE[1]/2)))


def process_player(delta_time):
	if Player['move_state'] == 1:
		Player['pos'][0] += Player['dir'][0] * Player['speed']*delta_time
		Player['pos'][1] += Player['dir'][1] * Player['speed']*delta_time
	elif Player['move_state'] == -1:
		Player['pos'][0] -= Player['dir'][0] * Player['speed']*delta_time
		Player['pos'][1] -= Player['dir'][1] * Player['speed']*delta_time
	if Player['turn_state'] == 1:
		Player['dir'] = rotate_vector(Player['dir'], -Player['rot_speed'])
		Camera['dir'] = rotate_vector(Camera['dir'], -Player['rot_speed'])
	elif Player['turn_state'] == -1:
		Player['dir'] = rotate_vector(Player['dir'], Player['rot_speed'])
		Camera['dir'] = rotate_vector(Camera['dir'], Player['rot_speed'])

# ---- MAIN
cur_time = perf_counter()
running = True
while running:
	# ---- Draw
	screen.fill(COLOR['BLACK'])
	pygame.draw.rect(screen, COLOR['CEIL'], (1, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]/2))
	pygame.draw.rect(screen, COLOR['FLOOR'], (0, SCREEN_SIZE[1]/2, SCREEN_SIZE[0], SCREEN_SIZE[1]/2))
	for col in range(SCREEN_SIZE[0]):
		draw_wall(col, hit_wall(col))

	last_time = cur_time
	cur_time = perf_counter()
	frame_duration = cur_time - last_time
	framerate = int(1.0/frame_duration)
	display_framerate(framerate)
	#draw_minimap(hit_wall(SCREEN_SIZE[0]/2))
	pygame.display.flip()

	# ---- Input
	for event in pygame.event.get():
		if event.type == QUIT:
			break
		elif event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
			elif event.key == K_w:
				Player['move_state'] = 1
			elif event.key == K_s:
				Player['move_state'] = -1
			elif event.key == K_a:
				Player['turn_state'] = 1
			elif event.key == K_d:
				Player['turn_state'] = -1
		elif event.type == KEYUP:
			if event.key == K_w or event.key == K_s:
				Player['move_state'] = 0
			elif event.key == K_a or event.key == K_d:
				Player['turn_state'] = 0
	process_player(frame_duration)
