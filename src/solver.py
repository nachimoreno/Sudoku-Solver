from . import sudoku as sk
from itertools import combinations
from collections import deque

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


class HiddenPairSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        In each unit, if two digits appear only in the same two cells,
        removes all other candidates from those two cells.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        units = []
        for row in range(9):
            units.append([(self.sudoku.board[row][c], row, c) for c in range(9)])
        for col in range(9):
            units.append([(self.sudoku.board[r][col], r, col) for r in range(9)])
        for br in range(3):
            for bc in range(3):
                units.append([
                    (self.sudoku.board[br * 3 + r][bc * 3 + c], br * 3 + r, bc * 3 + c)
                    for r in range(3) for c in range(3)
                ])

        for unit in units:
            for da, db in combinations(range(1, 10), 2):
                ab_cells = [(cell, r, c) for cell, r, c in unit
                            if da in cell.candidates or db in cell.candidates]
                if len(ab_cells) != 2:
                    continue
                if not any(da in cell.candidates for cell, _, _ in ab_cells):
                    continue
                if not any(db in cell.candidates for cell, _, _ in ab_cells):
                    continue
                for cell, r, c in ab_cells:
                    for cand in list(cell.candidates):
                        if cand not in (da, db):
                            cell.candidates.remove(cand)
                            eliminated_count += 1
                            if verbose:
                                print(f"HiddenPairSolver: Removed {cand} from cell ({c + 1}, {r + 1}) (hidden pair {{{da},{db}}})")

        if verbose and eliminated_count > 0:
            print(f"HiddenPairSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("HiddenPairSolver: No candidates eliminated.\n")

        return eliminated_count


class HiddenTripleSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        In each unit, if three digits appear only in the same three cells,
        removes all other candidates from those three cells.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        units = []
        for row in range(9):
            units.append([(self.sudoku.board[row][col], row, col) for col in range(9)])
        for col in range(9):
            units.append([(self.sudoku.board[r][col], r, col) for r in range(9)])
        for br in range(3):
            for bc in range(3):
                units.append([
                    (self.sudoku.board[br * 3 + r][bc * 3 + c], br * 3 + r, bc * 3 + c)
                    for r in range(3) for c in range(3)
                ])

        for unit in units:
            for d1, d2, d3 in combinations(range(1, 10), 3):
                triple_cells = [(cell, r, c) for cell, r, c in unit
                                if d1 in cell.candidates or d2 in cell.candidates or d3 in cell.candidates]
                if len(triple_cells) != 3:
                    continue
                if not any(d1 in cell.candidates for cell, _, _ in triple_cells):
                    continue
                if not any(d2 in cell.candidates for cell, _, _ in triple_cells):
                    continue
                if not any(d3 in cell.candidates for cell, _, _ in triple_cells):
                    continue
                for cell, r, c in triple_cells:
                    for cand in list(cell.candidates):
                        if cand not in (d1, d2, d3):
                            cell.candidates.remove(cand)
                            eliminated_count += 1
                            if verbose:
                                print(f"HiddenTripleSolver: Removed {cand} from cell ({c + 1}, {r + 1}) (hidden triple {{{d1},{d2},{d3}}})")

        if verbose and eliminated_count > 0:
            print(f"HiddenTripleSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("HiddenTripleSolver: No candidates eliminated.\n")

        return eliminated_count


class NakedQuadSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        In each unit, if four cells collectively contain only four candidates,
        removes those candidates from all other cells in the unit.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        units = []
        for row in range(9):
            units.append([(self.sudoku.board[row][col], row, col) for col in range(9)])
        for col in range(9):
            units.append([(self.sudoku.board[r][col], r, col) for r in range(9)])
        for br in range(3):
            for bc in range(3):
                units.append([
                    (self.sudoku.board[br * 3 + r][bc * 3 + c], br * 3 + r, bc * 3 + c)
                    for r in range(3) for c in range(3)
                ])

        for unit in units:
            eligible = [(cell, r, c) for cell, r, c in unit if 2 <= len(cell.candidates) <= 4]

            for quad in combinations(eligible, 4):
                quad_positions = {(r, c) for _, r, c in quad}
                quad_set = set().union(*(set(cell.candidates) for cell, _, _ in quad))
                if len(quad_set) != 4:
                    continue

                for cell, r, c in unit:
                    if (r, c) in quad_positions:
                        continue
                    for cand in list(quad_set):
                        if cand in cell.candidates:
                            cell.candidates.remove(cand)
                            eliminated_count += 1
                            if verbose:
                                print(f"NakedQuadSolver: Removed {cand} from cell ({c + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"NakedQuadSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("NakedQuadSolver: No candidates eliminated.\n")

        return eliminated_count


class BoxLineReductionSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        If all occurrences of a candidate in a row or column are confined to a
        single 3x3 box, eliminates that candidate from all other cells in the box.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        for row in range(9):
            for digit in range(1, 10):
                cols = [c for c in range(9) if digit in self.sudoku.board[row][c].candidates]
                if len(cols) < 2:
                    continue
                if len({c // 3 for c in cols}) != 1:
                    continue
                box_col = cols[0] // 3
                box_row = row // 3
                if verbose:
                    print(f"BoxLineReductionSolver: digit {digit} in row {row + 1} confined to box ({box_row + 1},{box_col + 1})")
                for r in range(box_row * 3, box_row * 3 + 3):
                    if r == row:
                        continue
                    for c in range(box_col * 3, box_col * 3 + 3):
                        cell = self.sudoku.board[r][c]
                        if digit in cell.candidates:
                            cell.candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"BoxLineReductionSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

        for col in range(9):
            for digit in range(1, 10):
                rows = [r for r in range(9) if digit in self.sudoku.board[r][col].candidates]
                if len(rows) < 2:
                    continue
                if len({r // 3 for r in rows}) != 1:
                    continue
                box_row = rows[0] // 3
                box_col = col // 3
                if verbose:
                    print(f"BoxLineReductionSolver: digit {digit} in col {col + 1} confined to box ({box_row + 1},{box_col + 1})")
                for r in range(box_row * 3, box_row * 3 + 3):
                    for c in range(box_col * 3, box_col * 3 + 3):
                        if c == col:
                            continue
                        cell = self.sudoku.board[r][c]
                        if digit in cell.candidates:
                            cell.candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"BoxLineReductionSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"BoxLineReductionSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("BoxLineReductionSolver: No candidates eliminated.\n")

        return eliminated_count


class XWingSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        When a candidate appears in exactly 2 cells in each of two rows sharing
        the same two columns, eliminates that candidate from those columns everywhere
        else. Applies symmetrically using columns as the base.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        for digit in range(1, 10):
            # Row-based X-Wing
            row_cols = {}
            for row in range(9):
                cols = [c for c in range(9) if digit in self.sudoku.board[row][c].candidates]
                if len(cols) == 2:
                    row_cols[row] = cols

            for r1, r2 in combinations(row_cols, 2):
                if row_cols[r1] != row_cols[r2]:
                    continue
                c1, c2 = row_cols[r1]
                if verbose:
                    print(f"XWingSolver: X-Wing for digit {digit} at rows {r1 + 1},{r2 + 1} cols {c1 + 1},{c2 + 1}")
                for r in range(9):
                    if r in (r1, r2):
                        continue
                    for c in (c1, c2):
                        cell = self.sudoku.board[r][c]
                        if digit in cell.candidates:
                            cell.candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"XWingSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

            # Column-based X-Wing
            col_rows = {}
            for col in range(9):
                rows = [r for r in range(9) if digit in self.sudoku.board[r][col].candidates]
                if len(rows) == 2:
                    col_rows[col] = rows

            for c1, c2 in combinations(col_rows, 2):
                if col_rows[c1] != col_rows[c2]:
                    continue
                r1, r2 = col_rows[c1]
                if verbose:
                    print(f"XWingSolver: X-Wing for digit {digit} at cols {c1 + 1},{c2 + 1} rows {r1 + 1},{r2 + 1}")
                for c in range(9):
                    if c in (c1, c2):
                        continue
                    for r in (r1, r2):
                        cell = self.sudoku.board[r][c]
                        if digit in cell.candidates:
                            cell.candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"XWingSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"XWingSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("XWingSolver: No candidates eliminated.\n")

        return eliminated_count


class SimpleColoringSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Builds chains of conjugate pairs (units with exactly two occurrences of a
        digit) and alternates two colors. If two same-color cells share a unit, that
        color is impossible and its cells are eliminated. Cells outside the chain that
        see both colors also have the candidate removed.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        def sees(r1, c1, r2, c2):
            return r1 == r2 or c1 == c2 or (r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3)

        for digit in range(1, 10):
            digit_cells = [(r, c) for r in range(9) for c in range(9)
                           if digit in self.sudoku.board[r][c].candidates]

            adj = {pos: set() for pos in digit_cells}

            for row in range(9):
                rc = [(row, c) for c in range(9) if digit in self.sudoku.board[row][c].candidates]
                if len(rc) == 2:
                    adj[rc[0]].add(rc[1])
                    adj[rc[1]].add(rc[0])
            for col in range(9):
                rc = [(r, col) for r in range(9) if digit in self.sudoku.board[r][col].candidates]
                if len(rc) == 2:
                    adj[rc[0]].add(rc[1])
                    adj[rc[1]].add(rc[0])
            for br in range(3):
                for bc in range(3):
                    rc = [(br * 3 + r, bc * 3 + c) for r in range(3) for c in range(3)
                          if digit in self.sudoku.board[br * 3 + r][bc * 3 + c].candidates]
                    if len(rc) == 2:
                        adj[rc[0]].add(rc[1])
                        adj[rc[1]].add(rc[0])

            color = {}

            for start in digit_cells:
                if start in color or not adj[start]:
                    continue

                queue = deque([start])
                color[start] = 0
                component = [start]

                while queue:
                    node = queue.popleft()
                    for neighbor in adj[node]:
                        if neighbor not in color:
                            color[neighbor] = 1 - color[node]
                            component.append(neighbor)
                            queue.append(neighbor)

                contradiction_color = None
                for i in range(len(component)):
                    for j in range(i + 1, len(component)):
                        ra, ca = component[i]
                        rb, cb = component[j]
                        if color[component[i]] == color[component[j]] and sees(ra, ca, rb, cb):
                            contradiction_color = color[component[i]]
                            break
                    if contradiction_color is not None:
                        break

                if contradiction_color is not None:
                    for pos in component:
                        if color[pos] == contradiction_color:
                            r, c = pos
                            if digit in self.sudoku.board[r][c].candidates:
                                self.sudoku.board[r][c].candidates.remove(digit)
                                eliminated_count += 1
                                if verbose:
                                    print(f"SimpleColoringSolver: Removed {digit} from ({c + 1},{r + 1}) (contradiction)")
                    continue

                c0_set = {pos for pos in component if color[pos] == 0}
                c1_set = {pos for pos in component if color[pos] == 1}

                for r, c in digit_cells:
                    if (r, c) in color:
                        continue
                    if digit not in self.sudoku.board[r][c].candidates:
                        continue
                    sees_c0 = any(sees(r, c, cr, cc) for cr, cc in c0_set)
                    sees_c1 = any(sees(r, c, cr, cc) for cr, cc in c1_set)
                    if sees_c0 and sees_c1:
                        self.sudoku.board[r][c].candidates.remove(digit)
                        eliminated_count += 1
                        if verbose:
                            print(f"SimpleColoringSolver: Removed {digit} from ({c + 1},{r + 1}) (sees both colors)")

        if verbose and eliminated_count > 0:
            print(f"SimpleColoringSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("SimpleColoringSolver: No candidates eliminated.\n")

        return eliminated_count


class SkyscraperSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        When a candidate appears exactly twice in two rows sharing exactly one
        column, any cell that sees both non-shared endpoint cells has the candidate
        removed. Applies symmetrically using columns as the base.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        def sees(r1, c1, r2, c2):
            return r1 == r2 or c1 == c2 or (r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3)

        for digit in range(1, 10):
            # Row-based skyscraper
            row_cols = {}
            for row in range(9):
                cols = [c for c in range(9) if digit in self.sudoku.board[row][c].candidates]
                if len(cols) == 2:
                    row_cols[row] = cols

            for r1, r2 in combinations(row_cols, 2):
                shared = set(row_cols[r1]) & set(row_cols[r2])
                if len(shared) != 1:
                    continue
                shared_col = next(iter(shared))
                tip1_col = next(c for c in row_cols[r1] if c != shared_col)
                tip2_col = next(c for c in row_cols[r2] if c != shared_col)
                pattern = {(r1, tip1_col), (r1, shared_col), (r2, tip2_col), (r2, shared_col)}

                for r in range(9):
                    for c in range(9):
                        if (r, c) in pattern:
                            continue
                        if digit not in self.sudoku.board[r][c].candidates:
                            continue
                        if sees(r, c, r1, tip1_col) and sees(r, c, r2, tip2_col):
                            self.sudoku.board[r][c].candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"SkyscraperSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

            # Column-based skyscraper
            col_rows = {}
            for col in range(9):
                rows = [r for r in range(9) if digit in self.sudoku.board[r][col].candidates]
                if len(rows) == 2:
                    col_rows[col] = rows

            for c1, c2 in combinations(col_rows, 2):
                shared = set(col_rows[c1]) & set(col_rows[c2])
                if len(shared) != 1:
                    continue
                shared_row = next(iter(shared))
                tip1_row = next(r for r in col_rows[c1] if r != shared_row)
                tip2_row = next(r for r in col_rows[c2] if r != shared_row)
                pattern = {(tip1_row, c1), (shared_row, c1), (tip2_row, c2), (shared_row, c2)}

                for r in range(9):
                    for c in range(9):
                        if (r, c) in pattern:
                            continue
                        if digit not in self.sudoku.board[r][c].candidates:
                            continue
                        if sees(r, c, tip1_row, c1) and sees(r, c, tip2_row, c2):
                            self.sudoku.board[r][c].candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"SkyscraperSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"SkyscraperSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("SkyscraperSolver: No candidates eliminated.\n")

        return eliminated_count


class SwordfishSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Extends X-Wing to three rows: when a candidate appears 2-3 times in each of
        three rows and their column positions cover exactly three columns, eliminates
        that candidate from those columns in all other rows. Applies symmetrically
        using columns as the base.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        for digit in range(1, 10):
            # Row-based swordfish
            row_cols = {}
            for row in range(9):
                cols = [c for c in range(9) if digit in self.sudoku.board[row][c].candidates]
                if 2 <= len(cols) <= 3:
                    row_cols[row] = cols

            for r1, r2, r3 in combinations(row_cols, 3):
                col_union = set(row_cols[r1]) | set(row_cols[r2]) | set(row_cols[r3])
                if len(col_union) != 3:
                    continue
                if verbose:
                    print(f"SwordfishSolver: Swordfish for digit {digit} at rows {r1 + 1},{r2 + 1},{r3 + 1}")
                for r in range(9):
                    if r in (r1, r2, r3):
                        continue
                    for c in col_union:
                        cell = self.sudoku.board[r][c]
                        if digit in cell.candidates:
                            cell.candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"SwordfishSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

            # Column-based swordfish
            col_rows = {}
            for col in range(9):
                rows = [r for r in range(9) if digit in self.sudoku.board[r][col].candidates]
                if 2 <= len(rows) <= 3:
                    col_rows[col] = rows

            for c1, c2, c3 in combinations(col_rows, 3):
                row_union = set(col_rows[c1]) | set(col_rows[c2]) | set(col_rows[c3])
                if len(row_union) != 3:
                    continue
                if verbose:
                    print(f"SwordfishSolver: Swordfish for digit {digit} at cols {c1 + 1},{c2 + 1},{c3 + 1}")
                for c in range(9):
                    if c in (c1, c2, c3):
                        continue
                    for r in row_union:
                        cell = self.sudoku.board[r][c]
                        if digit in cell.candidates:
                            cell.candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"SwordfishSolver: Removed {digit} from cell ({c + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"SwordfishSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("SwordfishSolver: No candidates eliminated.\n")

        return eliminated_count


class XYWingSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Finds a bivalue pivot {X,Y} that sees one wing {X,Z} and another wing {Y,Z}.
        Regardless of the pivot's value, Z is eliminated from every cell that sees
        both wings.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        def sees(r1, c1, r2, c2):
            return (r1, c1) != (r2, c2) and (
                r1 == r2 or c1 == c2 or (r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3)
            )

        bivalue = [(r, c) for r in range(9) for c in range(9)
                   if len(self.sudoku.board[r][c].candidates) == 2]

        for pr, pc in bivalue:
            x, y = self.sudoku.board[pr][pc].candidates

            for wr1, wc1 in bivalue:
                if (wr1, wc1) == (pr, pc) or not sees(pr, pc, wr1, wc1):
                    continue
                cands1 = self.sudoku.board[wr1][wc1].candidates
                if x not in cands1:
                    continue
                z_candidates = [v for v in cands1 if v != x]
                if len(z_candidates) != 1 or z_candidates[0] == y:
                    continue
                z = z_candidates[0]

                for wr2, wc2 in bivalue:
                    if (wr2, wc2) in ((pr, pc), (wr1, wc1)):
                        continue
                    if not sees(pr, pc, wr2, wc2):
                        continue
                    if set(self.sudoku.board[wr2][wc2].candidates) != {y, z}:
                        continue

                    if verbose:
                        print(f"XYWingSolver: pivot ({pr + 1},{pc + 1})[{x},{y}] "
                              f"wing1 ({wr1 + 1},{wc1 + 1})[{x},{z}] "
                              f"wing2 ({wr2 + 1},{wc2 + 1})[{y},{z}]")

                    for r in range(9):
                        for c in range(9):
                            if (r, c) in ((pr, pc), (wr1, wc1), (wr2, wc2)):
                                continue
                            if z not in self.sudoku.board[r][c].candidates:
                                continue
                            if sees(r, c, wr1, wc1) and sees(r, c, wr2, wc2):
                                self.sudoku.board[r][c].candidates.remove(z)
                                eliminated_count += 1
                                if verbose:
                                    print(f"XYWingSolver: Removed {z} from cell ({c + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"XYWingSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("XYWingSolver: No candidates eliminated.\n")

        return eliminated_count


class XYZWingSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Finds a trivalue pivot {X,Y,Z} that sees wing {X,Z} and wing {Y,Z}.
        Because the pivot also holds Z, the digit can only be eliminated from cells
        that see all three of pivot, wing1, and wing2.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        def sees(r1, c1, r2, c2):
            return (r1, c1) != (r2, c2) and (
                r1 == r2 or c1 == c2 or (r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3)
            )

        trivalue = [(r, c) for r in range(9) for c in range(9)
                    if len(self.sudoku.board[r][c].candidates) == 3]
        bivalue  = [(r, c) for r in range(9) for c in range(9)
                    if len(self.sudoku.board[r][c].candidates) == 2]

        for pr, pc in trivalue:
            xyz = set(self.sudoku.board[pr][pc].candidates)

            for z in list(xyz):
                x, y = sorted(xyz - {z})

                for wr1, wc1 in bivalue:
                    if not sees(pr, pc, wr1, wc1):
                        continue
                    if set(self.sudoku.board[wr1][wc1].candidates) != {x, z}:
                        continue

                    for wr2, wc2 in bivalue:
                        if (wr2, wc2) == (wr1, wc1):
                            continue
                        if not sees(pr, pc, wr2, wc2):
                            continue
                        if set(self.sudoku.board[wr2][wc2].candidates) != {y, z}:
                            continue

                        if verbose:
                            print(f"XYZWingSolver: pivot ({pr + 1},{pc + 1}){sorted(xyz)} "
                                  f"wing1 ({wr1 + 1},{wc1 + 1})[{x},{z}] "
                                  f"wing2 ({wr2 + 1},{wc2 + 1})[{y},{z}]")

                        for r in range(9):
                            for c in range(9):
                                if (r, c) in ((pr, pc), (wr1, wc1), (wr2, wc2)):
                                    continue
                                if z not in self.sudoku.board[r][c].candidates:
                                    continue
                                if sees(r, c, pr, pc) and sees(r, c, wr1, wc1) and sees(r, c, wr2, wc2):
                                    self.sudoku.board[r][c].candidates.remove(z)
                                    eliminated_count += 1
                                    if verbose:
                                        print(f"XYZWingSolver: Removed {z} from cell ({c + 1}, {r + 1})")

        if verbose and eliminated_count > 0:
            print(f"XYZWingSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("XYZWingSolver: No candidates eliminated.\n")

        return eliminated_count


class UniqueRectangleSolver(Solver):
    def run(
        self,
        verbose: bool = False
    ) -> int:
        """
        Detects Unique Rectangle Type 1: when three corners of a 2x2 rectangle
        spanning at least two boxes each hold only the two UR candidates, placing
        either digit in the fourth corner would create a deadly (ambiguous) pattern.
        Both UR digits are therefore eliminated from the fourth corner.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            int: Number of candidates eliminated.
        """
        eliminated_count = 0

        for r1, r2 in combinations(range(9), 2):
            for c1, c2 in combinations(range(9), 2):
                if r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3:
                    continue  # all four corners in the same box — no deadly pattern possible

                corners = [(r1, c1), (r1, c2), (r2, c1), (r2, c2)]
                cells = [self.sudoku.board[r][c] for r, c in corners]

                if any(cell.value != 0 for cell in cells):
                    continue

                for da, db in combinations(range(1, 10), 2):
                    if not all(da in cell.candidates and db in cell.candidates for cell in cells):
                        continue

                    ur_pair = {da, db}
                    floor_indices = [i for i, cell in enumerate(cells)
                                     if set(cell.candidates) == ur_pair]
                    if len(floor_indices) != 3:
                        continue

                    roof_idx = next(i for i in range(4) if i not in floor_indices)
                    rr, rc = corners[roof_idx]
                    roof_cell = self.sudoku.board[rr][rc]

                    if verbose:
                        print(f"UniqueRectangleSolver: UR Type 1 digits {{{da},{db}}} roof at ({rr + 1},{rc + 1})")

                    for digit in (da, db):
                        if digit in roof_cell.candidates:
                            roof_cell.candidates.remove(digit)
                            eliminated_count += 1
                            if verbose:
                                print(f"UniqueRectangleSolver: Removed {digit} from cell ({rc + 1}, {rr + 1})")

        if verbose and eliminated_count > 0:
            print(f"UniqueRectangleSolver: Eliminated {eliminated_count} candidates.\n")
        if verbose and eliminated_count == 0:
            print("UniqueRectangleSolver: No candidates eliminated.\n")

        return eliminated_count

