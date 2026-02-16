class Sudoku:
    def __init__(
        self
        ) -> None:
        """
        Defines the Sudoku class.
        """
        self.board = [[0 for _ in range(9)] for _ in range(9)]


    def initialize(
        self, 
        mode: str ='production'
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
                [0, 0, 0, 0, 1, 7, 0, 0, 3],
                [0, 0, 1, 2, 0, 0, 0, 0, 7],
                [2, 0, 0, 0, 0, 0, 5, 6, 0],
                [1, 3, 0, 0, 7, 0, 9, 0, 8],
                [0, 0, 0, 0, 0, 8, 0, 0, 0],
                [7, 0, 0, 0, 0, 0, 0, 4, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 8, 0, 0, 4, 3, 6, 0, 0],
                [0, 0, 4, 9, 0, 2, 0, 0, 0]
            ]


    def print_board(
        self
        ) -> None:
        """
        Prints the Sudoku board.
        """
        print()
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("---------------------")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("| ", end='')
                print(' ' if self.board[i][j] == 0 else self.board[i][j], end=' ')
            print()
        print()

    
    def is_valid(
        self
        ) -> bool:
        """
        Checks if the Sudoku board is valid.

        Returns:
            bool: True if the board is valid, False otherwise.
        """
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != 0:
                    current = self.board[i][j]
                    for k in range(9):
                        if self.board[i][k] == current and k != j:
                            return False
                        if self.board[k][j] == current and k != i:
                            return False

                    grid_start = ((i // 3) * 3, (j // 3) * 3)

                    


        
        return True