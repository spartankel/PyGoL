from copy import deepcopy
import colorama
import argparse
import random
import time
import sys

# Global Probability Table
# [-1.0, 1.0] --> from [-1.0, 0.0) is the birth probability "Reproducing"
#             --> 0.0 nothing changes "Stable"
#             --> from (0.0, 1.0] is the death probability "Starving" or "Crowded"

mc_life2death_probs = {
	0 : 1.00,
	1 : 1.00,
	2 : 0.00,
	3 : -1.00,
	4 : 1.00,
	5 : 1.00,
	6 : 1.00,
	7 : 1.00,
	8 : 1.00
}

class Cell:
	STATE = {
		"Starving" : (0, 1),
		"Stable" : (2,),
		"Reproducing" : (3,),
		"Crowded" : (4, 5, 6, 7, 8)
	}

	def __init__(self, x, y):
		self._alive = False
		self._x = x
		self._y = y

	def getCoords(self):
		return (self._x, self._y)

	def birth(self):
		self._alive = True

	def death(self):
		self._alive = False

	def isAlive(self):
		return self._alive

	def isDead(self):
		return not self._alive

	def cloneState(self, other):
		if not isinstance(other, Cell):
			raise ValueError("Only objects of class 'Cell' can be cloned")
		self._alive = other._alive

	def clone(self, other):
		if not isinstance(other, Cell):
			raise ValueError("Only objects of class 'Cell' can be cloned")
		self._alive = other._alive
		self._x = other._x
		self._y = other._y

	def __str__(self):
		state = "Alive" if self._alive else "Dead"
		return "{} at {}, {}".format(state, self._x, self._y)

class Grid:
	def __init__(self, x_size, y_size, prob_dict = None):
		self._rows = x_size
		self._columns = y_size
		self._grid = []
		self._mc = True if prob_dict else False
		self._probs = prob_dict
		for i in range(x_size):
			row = []
			for j in range(y_size):
				row.append(Cell(i, j))
			self._grid.append(tuple(row))
		self._grid = tuple(self._grid)

	def __iter__(self):
		return [cell for row in self._grid for cell in row].__iter__()

	def __len__(self):
		return self._rows * self._columns

	def __str__(self):
		s_print = ""
		for i in range(self._rows):
			for j in range(self._columns):
				plt_tkn = '*' if self[i, j].isAlive() else ' '
				s_print += plt_tkn + " "
			s_print += "\n"
		return s_print

	def __getitem__(self, key):
		if len(key) != 2:
			raise KeyError("Grid access needs two keys for the cell coordinates in the grid")
		return self.__getCell(key[0], key[1])

	def generateInitialState(self, seed=6666):
		random.seed = seed
		for cell in self:
			cell._alive = random.choice([True, False])

	def killAll(self):
		for cell in self:
			cell.death()

	def bornAll(self):
		for cell in self:
			cell.birth()

	def getDimension(self):
		return (self._rows, self._columns)

	def getNeighbours(self, cell):
		neig_l = []
		for i in range(-1, 2):
			for j in range(-1, 2):
				if i == 0 and j == 0:
					continue
				neig_l.append(self[cell._x + i, cell._y + j])
		return tuple(neig_l)

	def getAliveNeighbours(self, arg):
		if isinstance(arg, Cell):
			n_list = self.getNeighbours(arg)
		elif isinstance(arg, list) or isinstance(arg, tuple):
			n_list = arg
		else:
			raise ValueError("{} expects a Cell type or a neighbour list as argument.".format(self.getCellNeighbours.__name__))

		how_many_alive_neigh = 0
		for cell_neigh in n_list:
			if cell_neigh.isAlive():
				how_many_alive_neigh += 1

		return how_many_alive_neigh

	def updateCell(self, cell):
		updated_cell_state = cell._alive

		if cell.isAlive():
			if self.getCellState(cell) is "Starving" or self.getCellState(cell) is "Crowded":
				updated_cell_state = False
		else:
			if self.getCellState(cell) is "Reproducing":
				updated_cell_state = True

		return updated_cell_state

	def update(self):
		future_grid = deepcopy(self._grid)
		for i in range(self._rows):
			for j in range(self._columns):
				if self.updateCell(self[i, j]):
					future_grid[i][j].birth()
				else:
					future_grid[i][j].death()
		self.cloneState(future_grid)

	def __getCell(self, x, y):
		''' Aplying Periodic Boundary Conditions '''
		while x < 0:
			x += self._rows
		while x >= self._rows:
			x -= self._rows
		while y < 0:
			y += self._columns
		while y >= self._columns:
			y -= self._columns
		return self._grid[x][y]

	def getCellState(self, arg):
		if isinstance(arg, Cell):
			how_many_alive_neigh = self.getAliveNeighbours(arg)
		elif isinstance(arg, int):
			how_many_alive_neigh = arg
		else:
			raise ValueError("{} expects a Cell type or the number of alive neighbours as argument.".format(self.getCellState.__name__))

		cell_state = "Stable"
		# Monte Carlo Stuff
		if self._mc:
			barrier = self._probs[how_many_alive_neigh]
			if barrier < 0.0:
				barrier = abs(barrier)
				if self.__roll(barrier):
					cell_state = "Reproducing"
			else:
				if self.__roll(barrier):
					cell_state = "Starving"
		# Deterministic GoL
		else:
			for state in Cell.STATE:
				if how_many_alive_neigh in Cell.STATE[state]:
					cell_state = state
		return cell_state

	@staticmethod
	def __roll(prob):
		dice = random.uniform(0, 1)
		if dice > prob:
			return False
		else:
			return True

	def cloneState(self, otherGrid):
		for i in range(self._rows):
			for j in range(self._columns):
				other_cell = otherGrid[i][j]
				coords = other_cell.getCoords()
				cell = self[coords[0], coords[1]]
				cell.cloneState(other_cell)

# Only for plotting purposes
def put_cursor(x,y):
	print("\x1b[{};{}H".format(y+1,x+1))

def clear():
	print("\x1b[2J")

# Argument parser
def read_cmd(args):
	parser = argparse.ArgumentParser(description="Game of Life")
	parser.add_argument('--dim', help="Simulation grid dimension (Default = 50)", type=int, default=50)
	parser.add_argument('--steps', '-s', help="Number of simulation steps (Default = 100)", type=int, default=100)
	parser.add_argument('--wait', help="Seconds between plots. Not considering simulation time (Default = 0.1)", type=float, default=0.1)
	parser.add_argument('--monte-carlo', '-mc', help="Uses the non-deterministic event model", action="store_true")

	return parser.parse_args()

def check_params(args):
	if args.dim < 3:
		raise ValueError("Minimum grid dimension cannot be smaller than 3x3")
	if args.steps < 0:
		raise ValueError("Number of simulation steps must be non-negative! Cannot go back in time...")
	if args.wait < 0:
		raise ValueError("Seriously? Negative time?")

	return args

if __name__ == '__main__':

	try:
		args = check_params(read_cmd(sys.argv))
	except ValueError as e:
		sys.exit("Watchout your params: {}".format(e.message))

	print("Creating the grid ...")
	prob_dict = mc_life2death_probs if args.monte_carlo else {}
	grid = Grid(args.dim, args.dim, prob_dict)
	grid.generateInitialState()

	colorama.init()
	clear()
	for step in range(args.steps):
		put_cursor(0,0)
		print(grid)
		print("Step: {}".format(step))
		time.sleep(args.wait)
		grid.update()
