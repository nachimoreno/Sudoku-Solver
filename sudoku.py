class Cell:
    def __init__(
        self,
        value: int
    ) -> None:
        """
        Defines the Cell class.
        """
        self.value = value
        self.candidates = []

    
    def __repr__(
        self
        ) -> str:
        """
        Returns the string representation of the cell.
        """
        return str(self.value)


class Sudoku:
    def __init__(
        self
        ) -> None:
        """
        Defines the Sudoku class.
        """
        self.board = [[Cell(0) for _ in range(9)] for _ in range(9)]


    def initialize(
        self, 
        mode: str = 'production'
        ) -> None:
        """
        Initializes the Sudoku board based on the specified mode.

        Args:
            mode (str): The mode to initialize the board in.
                        'production': Initializes the board with a random valid Sudoku puzzle.
                        'debug': Initializes the board with a test Sudoku puzzle.
        """
        if not mode in ['production', 'debug']:
            raise ValueError("Invalid mode. Mode must be 'production' or 'debug'.")

        if mode == 'production':
            pass
        
        elif mode == 'debug':
            self.board = [
                [Cell(0), Cell(0), Cell(0), Cell(0), Cell(1), Cell(7), Cell(0), Cell(0), Cell(3)],
                [Cell(0), Cell(0), Cell(1), Cell(2), Cell(0), Cell(0), Cell(0), Cell(0), Cell(7)],
                [Cell(2), Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(5), Cell(6), Cell(0)],
                [Cell(1), Cell(3), Cell(0), Cell(0), Cell(7), Cell(0), Cell(9), Cell(0), Cell(8)],
                [Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(8), Cell(0), Cell(0), Cell(0)],
                [Cell(7), Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(4), Cell(0)],
                [Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(0), Cell(0)],
                [Cell(0), Cell(8), Cell(0), Cell(0), Cell(4), Cell(3), Cell(6), Cell(0), Cell(0)],
                [Cell(0), Cell(0), Cell(4), Cell(9), Cell(0), Cell(2), Cell(0), Cell(0), Cell(0)]
            ]


    def print_board(
        self
        ) -> None:
        """
        Prints the Sudoku board.
        """
        print()
        for row in range(9):
            if row % 3 == 0 and row != 0:
                print("---------------------")
            for col in range(9):
                if col % 3 == 0 and col != 0:
                    print("| ", end='')
                print(' ' if self.board[row][col].value == 0 else self.board[row][col].value, end=' ')
            print()
        print()


    def get_row(
        self,
        x: int,
        ret_cells: bool = False
    ) -> list[int]:
        """
        Fetches the column of the given cell.

        Args:
            x (int): The row of the cell.

        Returns:
            list[int]: The column of the cell.
        """
        if ret_cells: return [self.board[x][row] for row in range(9)]
        return [self.board[x][row].value for row in range(9)]


    def get_column(
        self,
        y: int,
        ret_cells: bool = False
    ) -> list[int]:
        """
        Fetches the column of the given cell.

        Args:
            y (int): The column of the cell.

        Returns:
            list[int]: The column of the cell.
        """
        if ret_cells: return [self.board[col][y] for col in range(9)]
        return [self.board[col][y].value for col in range(9)]


    def get_grid(
        self,
        x: int,
        y: int,
        ret_cells: bool = False
    ) -> list[int]:
        """
        Fetches the 3x3 grid of the given cell.

        Args:
            x (int): The row of the cell.
            y (int): The column of the cell.

        Returns:
            list[int]: The 3x3 grid of the cell.
        """
        grid_start_row = (x // 3) * 3
        grid_start_col = (y // 3) * 3
        if ret_cells: return [self.board[row][col] for row in range(grid_start_row, grid_start_row + 3) for col in range(grid_start_col, grid_start_col + 3)]
        return [self.board[row][col].value for row in range(grid_start_row, grid_start_row + 3) for col in range(grid_start_col, grid_start_col + 3)]

    
    def is_valid(
        self,
        verbose: bool = False
        ) -> bool:
        """
        Checks if the Sudoku board is valid.

        Args:
            verbose (bool): Whether to print verbose output.

        Returns:
            bool: True if the board is valid, False otherwise.
        """
        for row in range(9):
            for col in range(9):
                if self.board[row][col].value != 0:
                    current = self.board[row][col].value
                    if self.get_row(row).count(current) > 1:
                        if verbose: print(f"Invalid board: Duplicate number {current} in row {row}\n")
                        return False
                    if self.get_column(col).count(current) > 1:
                        if verbose: print(f"Invalid board: Duplicate number {current} in column {col}\n")
                        return False
                    if self.get_grid(row, col).count(current) > 1:
                        if verbose: print(f"Invalid board: Duplicate number {current} in 3x3 grid at ({row // 3}, {col // 3})\n")
                        return False
        
        if verbose: print("Valid board\n")
        return True