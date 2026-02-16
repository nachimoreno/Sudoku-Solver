import sudoku as sk

game = sk.Sudoku()
game.initialize(mode='debug')
game.board[0][1] = 2
game.print_board()

print(game.is_valid())