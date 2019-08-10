import win32api, win32gui, win32con
import MSFinder
from random import randint
from time import sleep
from PIL import ImageGrab
from sys import argv

TRIES = 1
if len(argv) > 4:
	TRIES = int(argv[4])

DELTA = 0
if len(argv) > 3:
	DELTA = float(argv[3])

CELL_PIXEL_SIZE = 16

CELL_NOT_FOUND = 256 * 256 * 256 - 1

CELL_FOUND = 128 * 256 * 256 + 128 * 256 + 128

CELL_NUMBER = [
	192 * 256 * 256 + 192 * 256 + 192,	# Empty
	255 * 256 * 256,					# 1
	128 * 256,							# 2
	255,								# 3 or bomb
	128 * 256 * 256,					# 4
	128,								# 5
	128 * 256 * 256 + 128 * 256,		# 6
	0,									# 7
	128 * 256 * 256 + 128 * 256 + 128,	# 8
	15790320							# Victory page
]

CELL_COLOR_OFFSET = (9, 3)

CELL_GLOBAL_OFFSET = (0, 0)

WINDOW = win32gui.GetDC(win32gui.GetDesktopWindow())

BBOX = None
SCREENSNAP = None

#while True:
#	pos = win32api.GetCursorPos()
#	print(win32gui.GetPixel(WINDOW, pos[0], pos[1]))

# ---- FUNCTIONS ----
def save_view (filename):
	sleep(DELTA)
	global SCREENSNAP
	tmp = (BBOX[0], BBOX[1] - 50, BBOX[2], BBOX[3])
	SCREENSNAP = ImageGrab.grab(tmp)
	SCREENSNAP.save(filename)

def get_pixel_color_slow (pos):
	return win32gui.GetPixel(WINDOW, pos[0], pos[1])

def get_pixel_color_fast (pos):
	a = SCREENSNAP.getpixel(pos)
	return a[0] + 256 * a[1] + 256 * 256 * a[2]

def get_pixel_type (cell):
	x = cell[0]
	y = cell[1]
	x_global = CELL_PIXEL_SIZE * x
	y_global = CELL_PIXEL_SIZE * y
	
	color = get_pixel_color_fast((x_global, y_global))

	if color == CELL_NOT_FOUND: return None
	elif color == CELL_FOUND:
		cell_color = get_pixel_color_fast((x_global + CELL_COLOR_OFFSET[0], y_global + CELL_COLOR_OFFSET[1]))
		num = CELL_NUMBER.index(cell_color)
		if num == 3 and get_pixel_color_fast((x_global + CELL_COLOR_OFFSET[0], y_global + CELL_COLOR_OFFSET[1] + 1)) == 0:
			print("DEAD :(")
			return -1
		if num == 9:
			print("Done!")
			return -1
		return num

def set_cell (cell):
	ctype = get_pixel_type(cell)
	if ctype == -1:
		return True
	MSFinder.set_cell_type(cell, ctype)

def update_grid ():
	sleep(DELTA)		# Latency needed to let the game update the tiles
	global SCREENSNAP
	SCREENSNAP = ImageGrab.grab(BBOX)
	for i in range(MSFinder.WIDTH):
		for j in range(MSFinder.HEIGHT):
			if MSFinder.GRIDNUMBERS[i][j] == None:
				if set_cell((i, j)) == True:
					return True

def left_click (pos):
	x = pos[0]
	y = pos[1]
	win32api.SetCursorPos(pos)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def right_click (pos):
	x = pos[0]
	y = pos[1]
	win32api.SetCursorPos(pos)
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

def left_click_cell (cell):
	x = cell[0]
	y = cell[1]
	x_global = CELL_GLOBAL_OFFSET[0] + CELL_PIXEL_SIZE * x + (CELL_PIXEL_SIZE // 2)
	y_global = CELL_GLOBAL_OFFSET[1] + CELL_PIXEL_SIZE * y + (CELL_PIXEL_SIZE // 2)
	left_click((x_global, y_global))

def right_click_cell (cell):
	x = cell[0]
	y = cell[1]
	x_global = CELL_GLOBAL_OFFSET[0] + CELL_PIXEL_SIZE * x + (CELL_PIXEL_SIZE // 2)
	y_global = CELL_GLOBAL_OFFSET[1] + CELL_PIXEL_SIZE * y + (CELL_PIXEL_SIZE // 2)
	right_click((x_global, y_global))

def restart ():
	x = CELL_GLOBAL_OFFSET[0] + MSFinder.WIDTH * (CELL_PIXEL_SIZE // 2)
	y = CELL_GLOBAL_OFFSET[1] - 30
	left_click((x, y))

# Waiting start from user
print("Press a when you are ready.")
while win32api.GetKeyState(65) >= 0: ()

print("Waiting for click!")
while win32api.GetKeyState(1) >= 0: ()
cursor_pos = win32api.GetCursorPos()

print("Launching!")
sleep(0.05)

# Setting global offset
y_offset = 0
while get_pixel_color_slow((cursor_pos[0], cursor_pos[1] + y_offset)) != CELL_FOUND:
	y_offset -= 1
x_offset = 0
while get_pixel_color_slow((cursor_pos[0] + x_offset, cursor_pos[1])) != CELL_FOUND:
	x_offset -= 1
CELL_GLOBAL_OFFSET = (cursor_pos[0] + x_offset, cursor_pos[1] + y_offset)

BBOX = (CELL_GLOBAL_OFFSET[0], CELL_GLOBAL_OFFSET[1], CELL_GLOBAL_OFFSET[0] + MSFinder.WIDTH * CELL_PIXEL_SIZE - 1, CELL_GLOBAL_OFFSET[1] + MSFinder.HEIGHT * CELL_PIXEL_SIZE - 1)

for u in range(TRIES):
	MSFinder.reset()
	restart()

	left_click_cell((randint(0, MSFinder.WIDTH), randint(0, MSFinder.HEIGHT)))
	sleep(0.5)

	update_grid()

	while not MSFinder.is_finished():
		q = MSFinder.execute_turn()

		if q == {}:
			bg = None
			if len(MSFinder.SOLUTIONS) > 0:
				tmp0 = {e: 0 for e in MSFinder.SOLUTIONS[0]}
				for s in MSFinder.SOLUTIONS:
					for e in s:
						if s[e] == False:
							tmp0[e] += 1
				tmp1 = list(tmp0.values())
				bg = list(tmp0.keys())[tmp1.index(max(tmp1))]
				print("Prepared blind guess on", bg)
			else:
				i = 0
				while None not in MSFinder.GRIDBOMB[i]: i += 1
				j = MSFinder.GRIDBOMB[i].index(None)
				bg = (i, j)
				print("Unprepared blind guess on", bg)
			
			left_click_cell(bg)
			if update_grid(): break
			continue

		for e in q:
			if q[e] == True:
				right_click_cell(e)
			else:
				left_click_cell(e)
		if update_grid(): break
	
	save_view("VIEW-" + str(u) + ".png")
	print("Test " + str(u) + " done")