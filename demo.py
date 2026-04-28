from src.sudoku import Sudoku
from src.solver import Solver, NakedSingleSolver, HiddenSingleSolver, PointingPairsSolver, NakedPairSolver, NakedTripleSolver
from src.loop import solve_loop

game = Sudoku()
game.initialize(mode='debug', pattern_number=3)
print("Initial game board:\n")
game.print_board()
game.is_valid(verbose=True)

solver = Solver(game)
solver.populate_candidates()

placers = [
    NakedSingleSolver(game),
    HiddenSingleSolver(game),
]

eliminators = [
    PointingPairsSolver(game),
    NakedPairSolver(game),
    NakedTripleSolver(game),
]

solve_loop(
    game,
    placers,
    eliminators,
    output_prefix="outputs/board",
    mode="step",
    verbose=True,
)
