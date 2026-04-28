from . import sudoku as sk
from itertools import combinations

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
            if verbose: print(f"Processing row {row + 1}\n")

            for col in range(9):
                if verbose: print(f"Processing cell ({col + 1}, {row + 1})")
                current_cell = self.sudoku.board[row][col]

                # Skip check if cell is not empty
                if current_cell.value != 0:
                    if verbose:print(f"Cell ({row + 1}, {col + 1}) already contains a value ({current_cell.value}).\n")
                    continue

                current_cell.candidates = [i for i in range(1, 10)]

                # Remove all numbers that already exist in the 3x3 grid
                cell_grid = set(self.sudoku.get_grid(row, col))
                cell_grid.remove(0) # Remove non-values from check
                if verbose: print(f"Current Cell's Grid: {cell_grid}")
                current_cell.explain = f"Cell's Grid Last Pass: {cell_grid}\n"

                for k in cell_grid:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}")

                # Remove all numbers that already exist in the column
                cell_column = set(self.sudoku.get_column(col))
                cell_column.remove(0)
                if verbose: print(f"Current Cell's Column: {cell_column}")
                current_cell.explain += f"Cell's Column Last Pass: {cell_column}\n"

                for k in cell_column:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}")

                # Remove all numbers that already exist in the row
                cell_row = set(self.sudoku.get_row(row))
                cell_row.remove(0)
                if verbose: print(f"Current Cell's Row: {cell_row}")
                current_cell.explain += f"Cell's Row Last Pass {cell_row}"

                for k in cell_row:
                    if k in current_cell.candidates:
                        current_cell.candidates.remove(k)
                if verbose: print(f"Current Cell's Candidates: {current_cell.candidates}\n")

    def update_candidates(
        self,
        row: int,
        col: int,
        value: int
    ) -> None:
        """
        Removes a placed value from the candidates of all peers in the same row, column, and grid.

        Args:
            row (int): The row of the placed cell.
            col (int): The column of the placed cell.
            value (int): The value that was placed.
        """
        peers = set(self.sudoku.get_row(row, ret_cells=True))
        peers.update(self.sudoku.get_column(col, ret_cells=True))
        peers.update(self.sudoku.get_grid(row, col, ret_cells=True))

        for peer in peers:
            if value in peer.candidates:
                peer.candidates.remove(value)

    
class NakedSingleSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Checks if any candidate is the only remaining candidate for a cell, and then places it.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of cells filled.
        """
        filled_count = 0

        for row in range(9):
            for col in range(9):
                current_cell = self.sudoku.board[row][col]

                if current_cell.value != 0:
                    continue

                if len(current_cell.candidates) == 1:
                    current_cell.value = current_cell.candidates[0]
                    current_cell.candidates = []
                    self.update_candidates(row, col, current_cell.value)
                    filled_count += 1
                    if verbose:
                        print(f"NakedSingleSolver: Placed {current_cell.value} in cell ({row + 1}, {col + 1}).")
                        print()

        if verbose and filled_count > 0:
            print(f"NakedSingleSolver: Filled {filled_count} cells.\n")

        if verbose and filled_count == 0:
            print("NakedSingleSolver: No naked singles found.\n")

        return filled_count


class HiddenSingleSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Checks if any number can only have one possible position in a row, column, or grid, and if so, place it.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of cells filled.
        """
        filled_count = 0

        candidate_counts = {i: 0 for i in range(1, 10)}

        for row in range(9):
            candidate_counts_row = candidate_counts.copy()
            row_cells = self.sudoku.get_row(row, ret_cells=True)

            for cell in row_cells:
                for candidate in cell.candidates:
                    candidate_counts_row[candidate] += 1

            for candidate, count in candidate_counts_row.items():
                if count == 1:
                    if verbose: print(f"HiddenSingleSolver: Found single {candidate} in row {row + 1}")

                    for cell in row_cells:
                        if candidate == cell.value:
                            continue

                    cell_pos = 0
                    for cell in row_cells:
                        if candidate in cell.candidates:
                            cell.value = candidate
                            cell.candidates = []
                            self.update_candidates(row, cell_pos, candidate)
                            filled_count += 1
                            if verbose:
                                print(f"HiddenSingleSolver: Placed {candidate} in cell ({cell_pos + 1}, {row + 1})")
                        cell_pos += 1

        for col in range(9):
            candidate_counts_col = candidate_counts.copy()
            col_cells = self.sudoku.get_column(col, ret_cells=True)

            for cell in col_cells:
                for candidate in cell.candidates:
                    candidate_counts_col[candidate] += 1

            for candidate, count in candidate_counts_col.items():
                if count == 1:
                    if verbose: print(f"HiddenSingleSolver: Found single {candidate} in column {col + 1}")

                    for cell in col_cells:
                        if candidate == cell.value:
                            continue

                    cell_pos = 0
                    for cell in col_cells:
                        if candidate in cell.candidates:
                            cell.value = candidate
                            cell.candidates = []
                            self.update_candidates(cell_pos, col, candidate)
                            filled_count += 1
                            if verbose:
                                print(f"HiddenSingleSolver: Placed {candidate} in cell ({col + 1}, {cell_pos + 1})")
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
                        if verbose: print(f"HiddenSingleSolver: Found single {candidate} in grid ({x + 1}, {y + 1})")

                        for cell in grid_cells:
                            if candidate == cell.value:
                                continue

                        cell_pos = 0
                        for cell in grid_cells:
                            if candidate in cell.candidates:
                                cell.value = candidate
                                cell.candidates = []
                                self.update_candidates(x * 3 + cell_pos // 3, y * 3 + cell_pos % 3, candidate)
                                filled_count += 1
                                if verbose:
                                    print(f"HiddenSingleSolver: Placed {candidate} in cell ({x * 3 + cell_pos % 3 + 1}, {x * 3 + cell_pos // 3 + 1})")
                            cell_pos += 1

        if verbose and filled_count > 0:
            print(f"HiddenSingleSolver: Filled {filled_count} cells.\n")

        if verbose and filled_count == 0:
            print("HiddenSingleSolver: No hidden singles found.\n")

        return filled_count


class NakedPairSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Checks if any two cells in a row, column, or grid have the same two candidates, and if so, removes those
        candidates from the other cells in the same row, column, or grid.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        for row in range(9):
            row_cells = self.sudoku.get_row(row, ret_cells=True)

            for cell in row_cells:
                if len(cell.candidates) != 2:
                    continue

                potential_naked_pair = cell.candidates

                for other_cell in row_cells:
                    if other_cell is cell:  # Bug 1: skip self-match
                        continue
                    if other_cell.candidates == potential_naked_pair:
                        naked_pair = potential_naked_pair
                        if verbose: print(f"NakedPairSolver: Found pair {naked_pair} in row {row + 1}")

                        for i, target in enumerate(row_cells):  # Bug 3: renamed to target
                            if target.candidates == naked_pair:
                                continue
                            for candidate in naked_pair:
                                if candidate in target.candidates:
                                    target.candidates.remove(candidate)
                                    eliminated_count += 1
                                    if verbose:
                                        print(f"NakedPairSolver: Removed {candidate} from cell ({i + 1}, {row + 1})")
                        break

        for col in range(9):
            col_cells = self.sudoku.get_column(col, ret_cells=True)

            for cell in col_cells:
                if len(cell.candidates) != 2:
                    continue

                potential_naked_pair = cell.candidates

                for other_cell in col_cells:
                    if other_cell is cell:
                        continue
                    if other_cell.candidates == potential_naked_pair:
                        naked_pair = potential_naked_pair
                        if verbose: print(f"NakedPairSolver: Found pair {naked_pair} in column {col + 1}")

                        for i, target in enumerate(col_cells):
                            if target.candidates == naked_pair:
                                continue
                            for candidate in naked_pair:
                                if candidate in target.candidates:
                                    target.candidates.remove(candidate)
                                    eliminated_count += 1
                                    if verbose:
                                        print(f"NakedPairSolver: Removed {candidate} from cell ({col + 1}, {i + 1})")
                        break

        for x in range(3):
            for y in range(3):
                grid_cells = self.sudoku.get_grid(x * 3, y * 3, ret_cells=True)

                for cell in grid_cells:
                    if len(cell.candidates) != 2:
                        continue

                    potential_naked_pair = cell.candidates

                    for other_cell in grid_cells:
                        if other_cell is cell:
                            continue
                        if other_cell.candidates == potential_naked_pair:
                            naked_pair = potential_naked_pair
                            if verbose: print(f"NakedPairSolver: Found pair {naked_pair} in grid ({x + 1}, {y + 1})")

                            for i, target in enumerate(grid_cells):
                                if target.candidates == naked_pair:
                                    continue
                                for candidate in naked_pair:
                                    if candidate in target.candidates:
                                        target.candidates.remove(candidate)
                                        eliminated_count += 1
                                        if verbose:
                                            print(f"NakedPairSolver: Removed {candidate} from cell ({x * 3 + i // 3 + 1}, {y * 3 + i % 3 + 1})")
                            break

        if verbose and eliminated_count > 0:
            print(f"NakedPairSolver: Eliminated {eliminated_count} candidates.\n")

        if verbose and eliminated_count == 0:
            print("NakedPairSolver: No candidates eliminated.\n")

        return eliminated_count


class NakedTripleSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Checks if any three cells in a row, column, or grid collectively contain only three candidates,
        and if so, removes those candidates from all other cells in the same unit.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        for row in range(9):
            row_cells = self.sudoku.get_row(row, ret_cells=True)
            eligible = [cell for cell in row_cells if 2 <= len(cell.candidates) <= 3]

            for cell_a, cell_b, cell_c in combinations(eligible, 3):
                triple = set(cell_a.candidates) | set(cell_b.candidates) | set(cell_c.candidates)
                if len(triple) != 3:
                    continue
                if verbose: print(f"NakedTripleSolver: Found triple {sorted(triple)} in row {row + 1}")

                for i, target in enumerate(row_cells):
                    if target is cell_a or target is cell_b or target is cell_c:
                        continue
                    for candidate in triple:
                        if candidate in target.candidates:
                            target.candidates.remove(candidate)
                            eliminated_count += 1
                            if verbose:
                                print(f"NakedTripleSolver: Removed {candidate} from cell ({i + 1}, {row + 1})")

        for col in range(9):
            col_cells = self.sudoku.get_column(col, ret_cells=True)
            eligible = [cell for cell in col_cells if 2 <= len(cell.candidates) <= 3]

            for cell_a, cell_b, cell_c in combinations(eligible, 3):
                triple = set(cell_a.candidates) | set(cell_b.candidates) | set(cell_c.candidates)
                if len(triple) != 3:
                    continue
                if verbose: print(f"NakedTripleSolver: Found triple {sorted(triple)} in column {col + 1}")

                for i, target in enumerate(col_cells):
                    if target is cell_a or target is cell_b or target is cell_c:
                        continue
                    for candidate in triple:
                        if candidate in target.candidates:
                            target.candidates.remove(candidate)
                            eliminated_count += 1
                            if verbose:
                                print(f"NakedTripleSolver: Removed {candidate} from cell ({col + 1}, {i + 1})")

        for x in range(3):
            for y in range(3):
                grid_cells = self.sudoku.get_grid(x * 3, y * 3, ret_cells=True)
                eligible = [cell for cell in grid_cells if 2 <= len(cell.candidates) <= 3]

                for cell_a, cell_b, cell_c in combinations(eligible, 3):
                    triple = set(cell_a.candidates) | set(cell_b.candidates) | set(cell_c.candidates)
                    if len(triple) != 3:
                        continue
                    if verbose: print(f"NakedTripleSolver: Found triple {sorted(triple)} in grid ({x + 1}, {y + 1})")

                    for i, target in enumerate(grid_cells):
                        if target is cell_a or target is cell_b or target is cell_c:
                            continue
                        for candidate in triple:
                            if candidate in target.candidates:
                                target.candidates.remove(candidate)
                                eliminated_count += 1
                                if verbose:
                                    print(f"NakedTripleSolver: Removed {candidate} from cell ({x * 3 + i // 3 + 1}, {y * 3 + i % 3 + 1})")

        if verbose and eliminated_count > 0:
            print(f"NakedTripleSolver: Eliminated {eliminated_count} candidates.\n")

        if verbose and eliminated_count == 0:
            print("NakedTripleSolver: No candidates eliminated.\n")

        return eliminated_count


class PointingPairsSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        For each 3x3 box, if a candidate digit appears only in cells that share
        the same row or column, eliminates that digit from all other cells in that
        row or column outside the box. Handles both pointing pairs (2 cells) and
        pointing triples (3 cells).

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        for box_row in range(3):
            for box_col in range(3):
                for digit in range(1, 10):
                    aligned = [
                        (self.sudoku.board[r][c], r, c)
                        for r in range(box_row * 3, box_row * 3 + 3)
                        for c in range(box_col * 3, box_col * 3 + 3)
                        if digit in self.sudoku.board[r][c].candidates
                    ]

                    if len(aligned) < 2:
                        continue

                    rows = {r for _, r, _ in aligned}
                    cols = {c for _, _, c in aligned}

                    if len(rows) == 1:
                        target_row = next(iter(rows))
                        if verbose:
                            size = "triple" if len(aligned) == 3 else "pair"
                            print(f"PointingPairsSolver: Found pointing {size} for digit {digit} in box ({box_row + 1}, {box_col + 1}) along row {target_row + 1}")

                        for c in range(9):
                            if box_col * 3 <= c < box_col * 3 + 3:
                                continue
                            cell = self.sudoku.board[target_row][c]
                            if digit in cell.candidates:
                                cell.candidates.remove(digit)
                                eliminated_count += 1
                                if verbose:
                                    print(f"PointingPairsSolver: Removed {digit} from cell ({c + 1}, {target_row + 1})")

                    if len(cols) == 1:
                        target_col = next(iter(cols))
                        if verbose:
                            size = "triple" if len(aligned) == 3 else "pair"
                            print(f"PointingPairsSolver: Found pointing {size} for digit {digit} in box ({box_row + 1}, {box_col + 1}) along column {target_col + 1}")

                        for r in range(9):
                            if box_row * 3 <= r < box_row * 3 + 3:
                                continue
                            cell = self.sudoku.board[r][target_col]
                            if digit in cell.candidates:
                                cell.candidates.remove(digit)
                                eliminated_count += 1
                                if verbose:
                                    print(f"PointingPairsSolver: Removed {digit} from cell ({target_col + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"PointingPairsSolver: Eliminated {eliminated_count} candidates.\n")

        if verbose and eliminated_count == 0:
            print("PointingPairsSolver: No candidates eliminated.\n")

        return eliminated_count

