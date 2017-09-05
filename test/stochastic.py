import unittest
import sys
sys.path.append("..")
sys.path.append(".")
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

class Stochastic(unittest.TestCase):
	def _test_mc_chance_n_neighbours(self, prob_map, n_neigh, total_samples=10000):
		how_many_times_survived = 0
		grid = gol.Grid(6, 6, prob_map)
		neigh_list = (grid[2, 2], grid[2, 3], grid[2, 4], grid[3, 2], grid[3, 4], grid[4, 2], grid[4, 3], grid[4, 4])

		for i in range(total_samples):
			for n in range(n_neigh):
				neigh_list[n].birth()
			grid[3, 3].birth()
			grid.update()
			how_many_times_survived += int(grid[3, 3].isDead())
			grid.killAll()
		self.assertAlmostEqual(prob_map[n_neigh], how_many_times_survived / float(total_samples), places=2)

	def test_mc_die_chance_no_neighbours(self):
		mc_no_neigh = {
			0 : 0.10,
			1 : 0.00,
			2 : 0.00,
			3 : 0.00,
			4 : 0.00,
			5 : 0.00,
			6 : 0.00,
			7 : 0.00,
			8 : 0.00
		}
		self._test_mc_chance_n_neighbours(mc_no_neigh, 0)

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(Stochastic)
	unittest.TextTestRunner(verbosity=2).run(suite)


