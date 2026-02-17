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
        for row in range(9):
            if verbose: print(f"Processing row {row}\n")

            for col in range(9):
                if verbose: print(f"Processing cell ({row}, {col})")
                current_cell = self.sudoku.board[row][col]

                # Skip check if cell is not empty
                if current_cell.value != 0:
                    continue

                current_cell.candidates = [i for i in range(1, 10)]

                # Remove all numbers that already exist in the 3x3 grid
                cell_grid = set(self.sudoku.get_grid(row, col))
                cell_grid.remove(0)
                if verbose: print(f"Current Cell's Grid: {cell_grid}")

                for k in cell_grid:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}")

                # Remove all numbers that already exist in the column
                cell_column = set(self.sudoku.get_column(col))
                cell_column.remove(0)
                if verbose: print(f"Current Cell's Column: {cell_column}")

                for k in cell_column:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}")

                # Remove all numbers that already exist in the row
                cell_row = set(self.sudoku.get_row(row))
                cell_row.remove(0)
                if verbose: print(f"Current Cell's Row: {cell_row}")

                for k in cell_row:
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
        for row in range(9):
            for col in range(9):
                current_cell = self.sudoku.board[row][col]

                # Skip check if cell is not empty
                if current_cell.value != 0:
                    continue

                if len(current_cell.candidates) == 1:
                    current_cell.value = current_cell.candidates[0]
                    current_cell.candidates = []
                    if verbose: print(f"Naked Single: Placed {current_cell.value} in cell ({row}, {col})")
                    self.populate_candidates()

        
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

        for row in range(9): # Calculate candidate counts for each row
            candidate_counts_row = candidate_counts.copy()
            row_cells = self.sudoku.get_row(row, ret_cells=True)

            for cell in row_cells:
                for candidate in cell.candidates:
                    candidate_counts_row[candidate] += 1

            for candidate, count in candidate_counts_row.items():
                if count == 1:
                    if verbose: print(f"Hidden Single: Found single {candidate} in row {row}")

                    for cell in row_cells:
                        if candidate == cell.value:
                            continue

                    cell_pos = 0
                    for cell in row_cells:
                        if candidate in cell.candidates:
                            cell.value = candidate
                            cell.candidates = []
                            if verbose: print(f"Hidden Single: Placed {candidate} in cell ({cell_pos + 1}, {row + 1})")
                            self.populate_candidates()
                        cell_pos += 1

        for col in range(9): # Calculate candidate counts for each column
            candidate_counts_col = candidate_counts.copy()
            col_cells = self.sudoku.get_column(col, ret_cells=True)

            for cell in col_cells:
                for candidate in cell.candidates:
                    candidate_counts_col[candidate] += 1

            for candidate, count in candidate_counts_col.items():
                if count == 1:
                    if verbose: print(f"Hidden Single: Found single {candidate} in column {col}")

                    for cell in col_cells:
                        if candidate == cell.value:
                            continue

                    cell_pos = 0
                    for cell in col_cells:
                        if candidate in cell.candidates:
                            cell.value = candidate
                            cell.candidates = []
                            if verbose: print(f"Hidden Single: Placed {candidate} in cell ({col + 1}, {cell_pos + 1})")
                            self.populate_candidates()
                        cell_pos += 1

        for x in range(3):
            for y in range(3):
                candidate_counts_grid = candidate_counts.copy()
                grid_cells = self.sudoku.get_grid(x * 3, y * 3, ret_cells=True)

                for cell in grid_cells:
                    for candidate in cell.candidates:
                        candidate_counts_grid[candidate] += 1

                for candidate, count in candidate_counts_grid.items():
                    if count == 1:
                        if verbose: print(f"Hidden Single: Found single {candidate} in grid ({x}, {y})")

                        for cell in grid_cells:
                            if candidate == cell.value:
                                continue

                        cell_pos = 0
                        for cell in grid_cells:
                            if candidate in cell.candidates:
                                cell.value = candidate
                                cell.candidates = []
                                if verbose: print(f"Hidden Single: Placed {candidate} in grid ({x}, {y})")
                                self.populate_candidates()
                            cell_pos += 1


    def solve_naked_pairs(): pass


    def solve_naked_triples(): pass


    def solve_hidden_pairs(): pass


    def solve_hidden_triples(): pass