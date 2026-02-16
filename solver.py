import sudoku as sk

game = sk.Sudoku()
game.initialize(mode='debug')
game.board[0][1].value = 2
game.print_board()
game.is_valid()