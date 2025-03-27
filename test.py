import engine.board_and_fields as baf
import engine.engine as eng
import engine.fen_operations as fops

board = baf.Board()
fops.fen_to_board('1n3bnr/r1pq1k1p/p2P4/Pp2p1pP/1PP2p2/B3Q3/R2PKPb1/1N3BNR w - g6 1 15',board)
board.print_board()
eng.tryMove("w",board,4,0,5,0)
board.print_board()
