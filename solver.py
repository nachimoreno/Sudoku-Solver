import sudoku as sk

class Solver:
    def __init__(
        self,
        sudoku: sk.Sudoku
        ) -> None:
        """
        Initializes the Solver class.

        Args:
            sudoku (sk.Sudoku): The Sudoku board to solve.
        """
        self.sudoku = sudoku

    def populate_candidates(
        self, 
        verbose: bool = False
        ) -> None:
        """
        Populates the candidates for each cell on the board.

        Args:
            verbose (bool): Whether to print verbose output.
        """
        for i in range(9):
            if verbose: print(f"Processing row {i}\n")

            for j in range(9):
                if verbose: print(f"Processing cell ({i}, {j})")
                current_cell = self.sudoku.board[i][j]

                # Skip check if cell is not empty
                if current_cell.value != 0:
                    continue

                current_cell.candidates = [i for i in range(1, 10)]

                # Remove all numbers that already exist in the 3x3 grid
                grid = set(self.sudoku.get_grid(i, j))
                grid.remove(0)
                if verbose: print(f"Current Cell's Grid: {grid}")

                for k in grid:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}")

                # Remove all numbers that already exist in the column
                column = set(self.sudoku.get_column(j))
                column.remove(0)
                if verbose: print(f"Current Cell's Column: {column}")

                for k in column:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}")

                # Remove all numbers that already exist in the row
                row = set(self.sudoku.get_row(i))
                row.remove(0)
                if verbose: print(f"Current Cell's Row: {row}")

                for k in row:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}\n")


    def solve_naked_singles(
        self,
        verbose: bool = False
        ) -> None:
        """
        Checks if any candidate is the only remaining candidate for a cell, and then places it.

        Args:
            verbose (bool): Whether to print verbose output.
        """
        for i in range(9):
            for j in range(9):
                current_cell = self.sudoku.board[i][j]

                # Skip check if cell is not empty
                if current_cell.value != 0:
                    continue

                if len(current_cell.candidates) == 1:
                    current_cell.value = current_cell.candidates[0]
                    current_cell.candidates = []
                    if verbose: print(f"Naked Single: Placed {current_cell.value} in cell ({i}, {j})")

        
        def solve_hidden_singles(
            self,
            verbose: bool = False
        ) -> None:
            """
            Checks if any number can only have one possible position in a row, column, or grid, and if so, place it.

            Args:
                verbose (bool): Whether to print verbose output.
            """

            candidate_counts = {i: 0 for i in range(1, 10)}




        def solve_naked_pairs(): pass


        def solve_naked_triples(): pass


        def solve_hidden_pairs(): pass


        def solve_hidden_triples(): pass



game = sk.Sudoku()
game.initialize(mode='debug')
game.print_board()
game.is_valid(verbose=True)
solver = Solver(game)
solver.populate_candidates()
solver.replace_naked_singles()
game.print_board()