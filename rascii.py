import math
import os


###########
# GLOBALS #
###########
color = '█'
border_color = '#'
fill = False
fill_color = 'f'
translateVector = [0, 0]  # x, y translation


#######################
# Important Functions #
#######################
def clear_console():
	"""
	Clears the console with checks for operating system
	"""
	os.system('cls' if os.name in ('nt', 'dos') else 'clear')


def cartesian_to_idx(width, x, y):
	"""
	Finds the index of an (x, y) in the screen_data array
	"""
	return x + ((width+1)*y)


def idx_to_cartesian(width, idx):
	"""
	Finds the (x, y) on the screen from a given index
	"""
	x = (idx % (width+1)) if idx > 1 else 0
	y = (idx - x)/(width+1) if idx > 1 else 0
	return x, int(y)


def color_value(value: int):
	"""
	Maps the 255 rgb values to 70 alpha pre-specified characters to give illusion of light-level.
	"""
	global color
	if value < 0 or value > 255: error("Color Value must be between 0 and 255")
	color_range = ' .`^",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8@$█'
	color = color_range[math.floor(((len(color_range)-1)/255) * value)]

##################
# Error Function #
##################
def error(Message: str):
	# used function to easily keep track of error handling
	print(f'<!-- Error: {Message} --!>')
	exit(1)


################
# Window Class #
################
class new_window:
	"""
	Class to create and handle the window
	"""
	def __init__(self, width, height) -> None:
		self.screen_data = []
		self.bg_color = '_'
		self.width  = width
		self.height = height
		self.border = False

	def __repr__(self):
		"""
		Just for testing purposes
		"""
		return f'bg_color:({self.bg_color}), width:{self.width}, height:{self.height}'

	def setup(self):
		"""
		Will create the screen_data array based on a given width and height
		"""
		if not self.border:  # if not drawing the border
			self.screen_data = ['~/' if i % (self.width+1) == 0 else self.bg_color for i in range((self.width*self.height)+self.height)]

		elif self.border:  # if drawing a border
			for row in range(self.height):
				for col in range(self.width):

					if row == 0 or row == self.height-1 or col == 0 or col == self.width-1:
						self.screen_data.append(border_color)
					else:
						self.screen_data.append(self.bg_color)

				self.screen_data.append('~/')

	def draw(self):
		"""
		Iterates over every char in the window and appends to a "screen buffer"
		which is then printed all at once for efficiency

		special line break character = '~/'
		"""
		screen_buffer = ''
		for idx, i in enumerate(self.screen_data):
			if i != '~/':
				screen_buffer += f'{i} '  # char + 'space'
			elif i == '~/':
				screen_buffer += '\n'
		clear_console()
		print(screen_buffer)

	def clear(self):
		"""
		same as setup method, however this resets screen_data's state
		"""
		self.screen_data.clear()

		if not self.border:
			self.screen_data = ['~/' if i % (self.width+1) == 0 else self.bg_color for i in range((self.width*self.height)+self.height)]

		if self.border:
			for row in range(self.height):
				for col in range(self.width):

					if row == 0 or row == self.height-1 or col == 0 or col == self.width-1:
						self.screen_data.append(border_color)
					else:
						self.screen_data.append(self.bg_color)

				self.screen_data.append('~/')


#####################
# Drawing Functions #
#####################
def point(screen, x, y):
	"""
	Edits screen_data array to put char at given (x, y) 
	"""
	index = cartesian_to_idx(screen.width, x, y)
	screen.screen_data[int(index)] = color


def line(screen, x1, y1, x2, y2):
	"""
	* Forms an equation from the two points
	* Then iterates over all probable points and checks with equation
	* Due to low ascii resolution a buffer of +/- (gradient/2) is given for accuracy.
	"""
	x1, x2 = x1 + translateVector[0], x2 + translateVector[0]
	y1, y2 = y1 + translateVector[1], y2 + translateVector[1]

	translate = False
	vertical = False
	
	if (x2-x1) != 0:  # try is used to fix vertical lines having undefined gradients
		m = (y2-y1)/(x2-x1)	
	else:
		m = 0
		vertical = True

	if y2 - y1 == 0:  # fix's horizontal line error
		m = 0
		translate = True

	c = y1 - (m * x1)  # y-intercept calculation
	lor, upr = -(m/2) if m > 0 else m/2, m/2 if m > 0 else -(m/2)  # buffer calculation

	if m < 1 and m >= 0: lor, upr = -(1/2), 1/2  # small gradient buffer

	# these lines are used for calculating where to iterate over the screen, instead of iterating over the whole screen.
	left_point   = x1 if x1 <= x2 else x2
	right_point  = x1 if left_point == x2 else x2
	top_point    = y1 if y1 <= y2 else y2
	bottom_point = y1 if top_point == y2 else y2
	stai = cartesian_to_idx(screen.width, left_point, top_point)
	endi = cartesian_to_idx(screen.width, right_point, bottom_point)

	for i in range(stai, endi):  # iteration over specified screen_data
		if screen.screen_data[i] != '~/':
			x, y = idx_to_cartesian(screen.width, i)

			temp = x  # hold of x while it is temporarily changed
			if vertical: m, x, c = 1, y, 0  # vertical line manipulation to give difference of 0
			difference = y - ((m*(x)) + c) if translate == False else 0 
			if vertical: x = temp

			if difference > lor and difference < upr: # does intercept
				if x >= left_point and x <= right_point:  # x buffer
					if y >= top_point and y <= bottom_point:  # y buffer
						point(screen, x, y)


def horizontal_point(screen, x, y, length):
	"""
	Used for rectangle to draw horizontal lines all at once to be more efficient
	"""
	index = cartesian_to_idx(screen.width, x, y)
	screen.screen_data[index:(index+length)] = color*length

def rect(screen, rx, ry, rw, rh):
	"""
	draws a rectangle at given (x, y) with specified width and height
	"""
	global color, fill, fill_color

	rx += translateVector[0]
	ry += translateVector[1]

	# efficiency calculations
	stax, endx = rx, rx + rw
	stay, endy = ry, ry + rh
	stai, endi = cartesian_to_idx(screen.width, stax, stay), cartesian_to_idx(screen.width, endx, endy)

	# if the rectangle is solid then more efficient function can be used
	# for i in range(rh):
	# 	horizontal_point(screen, rx, (ry+i), rw)
	for i in range(stai, endi):
		if screen.screen_data[i] != '~/':
			x, y = idx_to_cartesian(screen.width, i)
			# checks if point is between boundaries
			if x >= rx and x < rx + rw and y >= ry and y < ry + rh:
				if rw > 2 and rh > 2:
					if x > rx and x < (rx + rw)-1 and y > ry and y < (ry + rh)-1:
						if fill:
							temp = color
							color = fill_color
							point(screen, x, y)
							color = temp
					else:
						point(screen, x, y)
				else:
					point(screen, x, y)


def circle(screen, cx, cy, cr):
	global color, fill, fill_color
	"""
	Draws a circle to the screen at a given x, y with radius

	parameters
	----------
	cx: int
		x position of circle centre
	cy: int
		y position of circle centre
	cr: int
		radius of the circle
	fill: bool
		Whether to only draw the circumference
	"""

	cx += translateVector[0]
	cy += translateVector[1]

	# Calculate optomised points to iterate through 
	stax, endx = cx - cr, cx + cr
	stay, endy = cy - cr, cy + cr
	stai, endi = cartesian_to_idx(screen.width, stax, stay), cartesian_to_idx(screen.width, endx, endy)

	# looping over screen_data array
	for i in range(stai, endi):
		if screen.screen_data[i] != '~/':  # Disregard line break

			x, y = idx_to_cartesian(screen.width, i)
			d = (cr*cr) - ((cx-x)*(cx-x) + (cy-y)*(cy-y))

			if fill:
				if d <= cr*2 and d > 0:  # if point is on circumference using another buffer for accuracy
					point(screen, x, y)

				elif d > cr*2:  # if point is inside circle
					temp = color
					color = fill_color
					point(screen, x, y)
					color = temp

			else:
				if d <= cr*2 and d > 0:  # if point is on circumference using another buffer for accuracy
					point(screen, x, y)



def tri_area_calc(x1, y1, x2, y2, x3, y3):
	"""
	function to calculate the area of a triangle given 3 points
	"""
	lengths = []

	lengths.append((y2-y1)*(y2-y1) + (x2-x1)*(x2-x1))  # finds length of sides without sqrt by keeping them squared
	lengths.append((y3-y2)*(y3-y2) + (x3-x2)*(x3-x2))
	lengths.append((y3-y1)*(y3-y1) + (x3-x1)*(x3-x1))
	lengths.sort()
	c1, c2, c3 = lengths[2], lengths[1], lengths[0]
	c1sq, c2sq = math.sqrt(c1), math.sqrt(c2)  # two manditory sqrt's
	try:
		angle = math.acos((c1 + c2 - c3)/(2*c2sq*c1sq))  # uses cosine rule
	except:
		angle = 0.001
	area  = 0.5 * c1sq * c2sq * math.sin(angle)  # 1/2absin(c)

	return round(area, 1)


def triangle(screen, x1, y1, x2, y2, x3, y3, transparent=False):
	"""
	draws a triangle to the screen if a point is inside the triangle

	method:
		Get the area of the whole triangle

		using the iterated point, form 3 smaller triangles
		find the area of all 3 smaller triangles
		if the sum of all areas adds up to the sum of the whole triangle
		then that point is inside the triangle
	"""

	x1, x2, x3 = x1 + translateVector[0], x2 + translateVector[0], x3 + translateVector[0]
	y1, y2, y3 = y1 + translateVector[1], y2 + translateVector[1], y3 + translateVector[1]

	if not transparent:
		# calculate the area of the whole triangle
		area = tri_area_calc(x1, y1, x2, y2, x3, y3)

		# points calculated for effiency of iterating
		points_list = []
		points_list.append(cartesian_to_idx(screen.width, x1, y1))
		points_list.append(cartesian_to_idx(screen.width, x2, y2))
		points_list.append(cartesian_to_idx(screen.width, x3, y3))
		points_list.sort()

		for i in range(points_list[0], points_list[2]):
			if screen.screen_data[i] != '~/' or i not in points_list:
				# get coordniates of iterated point
				px, py = idx_to_cartesian(screen.width, i)

				# area of 3 smaller triangles
				a1 = tri_area_calc(x1, y1, px, py, x2, y2)
				a2 = tri_area_calc(x2, y2, px, py, x3, y3)
				a3 = tri_area_calc(x3, y3, px, py, x1, y1)

				# check sum with ascii buffer
				if a1+a2+a3 > round(area)-5 and a1+a2+a3 < round(area)+5:
					point(screen, px, py)

	elif transparent:
		# If only drawing outline then just connect with 3 lines
		# far more efficient as no Square Roots are needed
		line(screen, x1, y1, x2, y2)
		line(screen, x2, y2, x3, y3)
		line(screen, x3, y3, x1, y1)


def shape(screen, point_data: list, connected=True):
	"""
	connects points with lines from a specified array to form a shape.
	"""
	if len(point_data) % 2 == 0:
		for i in range(0, len(point_data) - 1, 2):
			if len(point_data) >= 4:
				if i == len(point_data)-2:
					if connected:
						line(screen, point_data[i], point_data[i+1], point_data[0], point_data[1])
				else:
					line(screen, point_data[i], point_data[i+1], point_data[i+2], point_data[i+3])
			else:
				point(screen, point_data[i]+translateVector[0], point_data[i+1]+translateVector[1])

	else:
		msg = "Point_data array has uneven length"
		error(msg)
