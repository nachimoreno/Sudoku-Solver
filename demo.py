from sudoku import Sudoku
from solver import Solver

game = Sudoku()
game.initialize(mode='debug')
game.print_board()
game.is_valid(verbose=True)

solver = Solver(game)
solver.populate_candidates()

for i in range(5):
    solver.solve_naked_singles(verbose=True)
    solver.solve_hidden_singles(verbose=True)
    game.print_board()