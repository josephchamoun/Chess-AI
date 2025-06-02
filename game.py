import chess

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.selected_square = None

    def get_legal_moves(self, square):

        """Get all legal moves for the piece at the given square"""
        legal_moves = []

        for move in self.board.legal_moves:
            if move.from_square == square:
                legal_moves.append(move.to_square)

        return legal_moves


    def try_move(self, from_square, to_square):
        
        piece = self.get_piece_at(from_square)

        if piece and piece.piece_type == chess.PAWN:
            target_rank = chess.square_rank(to_square)
            if (piece.color == chess.WHITE and target_rank == 7) or (piece.color == chess.BLACK and target_rank == 0):
                move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
            else:
                move = chess.Move(from_square, to_square)
        else:
            move = chess.Move(from_square, to_square)

        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False


    def get_piece_at(self, square):
        return self.board.piece_at(square)

    def is_white_turn(self):
        return self.board.turn == chess.WHITE
    
    def is_check(self):
        return self.board.is_check()
    
    def get_king_square(self, color):
        if color == chess.WHITE:
            return self.board.king(chess.WHITE)
        else:
            return self.board.king(chess.BLACK)

    def is_game_over(self):
        return self.board.is_game_over()

    def get_result(self):
        if self.board.is_checkmate():
            return "Checkmate"
        elif self.board.is_stalemate():
            return "Stalemate"
        elif self.board.is_insufficient_material():
            return "Draw by insufficient material"
        else:
            return "Game over"

    def reset(self):
        self.board.reset()
