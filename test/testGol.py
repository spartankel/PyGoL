import unittest
import sys
sys.path.append("..")
import gol

# Probability table for the MC tests
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

class TestGol(unittest.TestCase):
	def test_cell_getCoords(self):
		cell = gol.Cell(1, 1)
		self.assertEqual((1, 1), cell.getCoords())

	def test_cell_birth(self):
		cell = gol.Cell(1, 1)

		cell.birth()
		self.assertTrue(cell.alive())
		self.assertFalse(cell.dead())

	def test_cell_death(self):
		cell = gol.Cell(1, 1)

		cell.death()
		self.assertTrue(cell.dead())
		self.assertFalse(cell.alive())

	def test_grid_init(self):
		grid = gol.Grid(9, 9)

		self.assertEqual((9, 9), grid.getDimension())

		# Check that all objects in grid are type Cell
		for cell in grid:
			self.assertIsInstance(cell, gol.Cell)


	def test_grid_roll(self):
		roll_fun = gol.Grid._Grid__roll

		for i in range(10):
			# Check that 0 prob returns always False
			res = roll_fun(0)
			self.assertEqual(res, False, msg="0 chance not returning False")

			# Check that 1 prob returns always True
			res = roll_fun(1)
			self.assertEqual(res, True, msg="1 chance not returning True")

			# Check that only possible return types are True or False
			res = roll_fun(0.5)
			self.assertIsInstance(res, bool, msg="Return type different from [True, False]")

		# Check the dice
		test_dict = {}
		for i in range(1, 101, 1):
			test_dict[i / 100.] = []

		for i in range(10000):
			for chance in test_dict:
				test_dict[chance].append(roll_fun(chance))

		for chance in test_dict:
			true_chance = test_dict[chance].count(True) / float(len(test_dict[chance]))
			false_chance = test_dict[chance].count(False) / float(len(test_dict[chance]))
			self.assertAlmostEqual(chance, true_chance, 1, msg="{} did not converge to {}".format(true_chance, chance))
			self.assertAlmostEqual(1 - chance, false_chance, 1, msg="{} did not converge to {}".format(false_chance, chance))

	def test_grid_getNeighbours(self):
		grid = gol.Grid(9, 9)
		cell = grid[4, 4]
		neighs = grid.getNeighbours(cell)

		# Check the total number of neighbours
		self.assertEqual(len(neighs), 8, msg="Number of cell neighbours different from 8 (In a 2D grid)")

		# Check its coordinates
		# No boundary
		expected_coords = [(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)]
		for neigh_cell in neighs:
			try:
				expected_coords.remove(neigh_cell.getCoords())
			except ValueError as e:
				print "{} not a valid neighbour coordinate".format(neigh_cell.getCoords())

		self.assertEqual(len(expected_coords), 0, msg="No boundary conditions failed retrieving neighbours")

		# With boundary
		cell = grid[8, 8]
		neighs = grid.getNeighbours(cell)
		expected_coords = [(7, 7), (7, 8), (7, 0), (8, 7), (8, 0), (0, 7), (0, 8), (0, 0)]
		for neigh_cell in neighs:
			try:
				expected_coords.remove(neigh_cell.getCoords())
			except ValueError as e:
				print "{} not a valid neighbour coordinate".format(neigh_cell.getCoords())

		self.assertEqual(len(expected_coords), 0, msg="Periodic boundary conditions failed retrieveing neighbours")

	def test_grid_getCell(self):
		grid = gol.Grid(3, 3)
		cell = grid[1, 1]
		self.assertIsInstance(cell, gol.Cell)
		self.assertEqual((1, 1), cell.getCoords())

	def test_grid_getAliveNeighbours(self):
		grid = gol.Grid(6, 6)
		neighs = (grid[1, 1], grid[2, 3], grid[1, 3])
		map(lambda c : c.birth(), neighs)

		# No boundary conditions
		cell = grid[2, 2]
		self.assertEqual(3, grid.getAliveNeighbours(cell))
		self.assertEqual(3, grid.getAliveNeighbours(neighs))

		# With periodic boundary conditions
		neighs = (grid[4, 5], grid[0, 0])
		map(lambda c : c.birth(), neighs)
		cell = grid[5, 5]
		self.assertEqual(2, grid.getAliveNeighbours(cell))
		self.assertEqual(2, grid.getAliveNeighbours(neighs))

	def test_grid_getCellState(self):
		for n_neigh in range(9):
			grid = gol.Grid(3, 3)
			cell = grid[1, 1]
			neighs = grid.getNeighbours(cell)
			for n_cell in neighs[:n_neigh]:
				n_cell.birth()

			for state in gol.Cell.STATE:
				if n_neigh in gol.Cell.STATE[state]:
					expected_state = state
					break

			self.assertEqual(expected_state, grid.getCellState(cell))

	def test_grid_generateInitialState(self):
		grid = gol.Grid(100, 100)
		self.assertAlmostEqual(0.0, sum([x.alive() for x in grid]) / float(len(grid)), 1)
		grid.generateInitialState()
		self.assertAlmostEqual(0.5, sum([x.alive() for x in grid]) / float(len(grid)), 1)

	def test_grid_cloneState(self):
		test_matrix = (
			(gol.Cell(0, 0), gol.Cell(0, 1), gol.Cell(0, 2)),
			(gol.Cell(1, 0), gol.Cell(1, 1), gol.Cell(1, 2)),
			(gol.Cell(2, 0), gol.Cell(2, 1), gol.Cell(2, 2))
		)
		grid = gol.Grid(3, 3)
		original_grid_ref = grid._grid
		self.assertTrue(grid._grid is original_grid_ref)
		self.assertFalse(grid._grid is test_matrix)
		test_matrix[1][1].birth()
		grid.cloneState(test_matrix)

		self.assertTrue(grid[1, 1].alive())
		self.assertTrue(grid._grid is original_grid_ref)
		self.assertFalse(grid._grid is test_matrix)

	def test_grid_updateCell(self):
		for n_neigh in range(9):
			grid = gol.Grid(3, 3)
			cell = grid[1, 1]
			neighs = grid.getNeighbours(cell)
			for n_cell in neighs[:n_neigh]:
				n_cell.birth()

			if grid.updateCell(cell):
				cell.birth()
			else:
				cell.death()

			if n_neigh in gol.Cell.STATE["Starving"] or n_neigh in gol.Cell.STATE["Crowded"]:
				self.assertTrue(cell.dead())
				self.assertFalse(cell.alive())
			elif n_neigh in gol.Cell.STATE["Reproducing"]:
				self.assertTrue(cell.alive())
				self.assertFalse(cell.dead())
			elif n_neigh in gol.Cell.STATE["Stable"]:
				if cell.alive():
					self.assertTrue(cell.alive())
					self.assertFalse(cell.dead())
				if cell.dead():
					self.assertTrue(cell.dead())
					self.assertFalse(cell.alive())
			else:
				raise AssertionError("State not registered for {} neighbours".format(n_neigh))

	def test_block_stability(self):
		grid = gol.Grid(6, 6)
		block_cells = (grid[2, 2], grid[2, 3], grid[3, 2], grid[3, 3])
		self._test_stability(grid, block_cells)

	def test_beehive_stability(self):
		grid = gol.Grid(6, 6)
		block_cells = (grid[1, 2], grid[1, 3], grid[2, 1], grid[2, 4], grid[3, 2], grid[3, 3])
		self._test_stability(grid, block_cells)

	def test_well_stability(self):
		grid = gol.Grid(6, 6)
		block_cells = (grid[1, 2], grid[1, 3], grid[2, 1], grid[3, 1], grid[2, 4], grid[3, 4], grid[4, 2], grid[4, 3])
		self._test_stability(grid, block_cells)

	def test_mc_block_stability(self):
		grid = gol.Grid(6, 6, mc_life2death_probs)
		block_cells = (grid[2, 2], grid[2, 3], grid[3, 2], grid[3, 3])
		self._test_stability(grid, block_cells)

	def test_mc_beehive_stability(self):
		grid = gol.Grid(6, 6, mc_life2death_probs)
		block_cells = (grid[1, 2], grid[1, 3], grid[2, 1], grid[2, 4], grid[3, 2], grid[3, 3])
		self._test_stability(grid, block_cells)

	def test_mc_well_stability(self):
		grid = gol.Grid(6, 6, mc_life2death_probs)
		block_cells = (grid[1, 2], grid[1, 3], grid[2, 1], grid[3, 1], grid[2, 4], grid[3, 4], grid[4, 2], grid[4, 3])
		self._test_stability(grid, block_cells)

	def _test_stability(self, grid, block_cells):
		map(lambda x : x.birth(), block_cells)

		for step in range(1000):
			grid.update()

		for cell in grid:
			try:
				if cell in block_cells:
					self.assertTrue(cell.alive())
					self.assertFalse(cell.dead())
				else:
					self.assertTrue(cell.dead())
					self.assertFalse(cell.alive())
			except AssertionError as e:
				raise AssertionError("Error at cell {}: {}".format(cell, e.message))

if __name__ == "__main__":
	unittest.main()


