import chess
import math

class MinMax:

    central_squares = [
        chess.E4, chess.E5, chess.D4, chess.D5,
        chess.C4, chess.C5, chess.F4, chess.F5,      
    ]

    def get_piece_value(self, piece):
        if piece is None:
            return 0
        piece_type = piece.piece_type
        if piece_type == chess.PAWN:
            return 1
        elif piece_type == chess.KNIGHT:
            return 3
        elif piece_type == chess.BISHOP:
            return 3
        elif piece_type == chess.ROOK:
            return 5
        elif piece_type == chess.QUEEN:
            return 9
        elif piece_type == chess.KING:
            return 0 
        return 0

    def get_game_phase(self, board):

        total_material = 0
        piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9
        }

        for piece_type in piece_values:
            total_material += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            total_material += len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

        if total_material >= 50: 

            white_developed_knights_bishops = 0
            black_developed_knights_bishops = 0

            
            if board.piece_at(chess.B1) != chess.Piece(chess.KNIGHT, chess.WHITE): white_developed_knights_bishops += 1
            if board.piece_at(chess.G1) != chess.Piece(chess.KNIGHT, chess.WHITE): white_developed_knights_bishops += 1
            if board.piece_at(chess.C1) != chess.Piece(chess.BISHOP, chess.WHITE): white_developed_knights_bishops += 1
            if board.piece_at(chess.F1) != chess.Piece(chess.BISHOP, chess.WHITE): white_developed_knights_bishops += 1
            
            
            if board.piece_at(chess.B8) != chess.Piece(chess.KNIGHT, chess.BLACK): black_developed_knights_bishops += 1
            if board.piece_at(chess.G8) != chess.Piece(chess.KNIGHT, chess.BLACK): black_developed_knights_bishops += 1
            if board.piece_at(chess.C8) != chess.Piece(chess.BISHOP, chess.BLACK): black_developed_knights_bishops += 1
            if board.piece_at(chess.F8) != chess.Piece(chess.BISHOP, chess.BLACK): black_developed_knights_bishops += 1

          
            if white_developed_knights_bishops >= 2 or black_developed_knights_bishops >= 2:
                return "Middlegame"
            else:
                return "Opening"
        elif total_material >= 20: 
            return "Middlegame"
        else:
            return "Endgame"

    def evaluate_pieces_deployment(self, board):
        score = 0
        
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                       
                        if square not in [chess.B1, chess.G1, chess.C1, chess.F1]:
                            score += 0.2
                       
                        if piece.piece_type == chess.KNIGHT and square in [chess.C3, chess.F3, chess.D2, chess.E2]:
                            score += 0.1
                else: 
                    if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                        if square not in [chess.B8, chess.G8, chess.C8, chess.F8]:
                            score -= 0.2
                        if piece.piece_type == chess.KNIGHT and square in [chess.C6, chess.F6, chess.D7, chess.E7]:
                            score -= 0.1
        
        # bishops blocked by pawns
        # white
        if board.piece_at(chess.C1) == chess.Piece(chess.BISHOP, chess.WHITE) and board.piece_at(chess.D2) == chess.Piece(chess.PAWN, chess.WHITE):
            score -= 0.3
        if board.piece_at(chess.F1) == chess.Piece(chess.BISHOP, chess.WHITE) and board.piece_at(chess.E2) == chess.Piece(chess.PAWN, chess.WHITE):
            score -= 0.3
        
        # black
        if board.piece_at(chess.C8) == chess.Piece(chess.BISHOP, chess.BLACK) and board.piece_at(chess.D7) == chess.Piece(chess.PAWN, chess.BLACK):
            score += 0.3
        if board.piece_at(chess.F8) == chess.Piece(chess.BISHOP, chess.BLACK) and board.piece_at(chess.E7) == chess.Piece(chess.PAWN, chess.BLACK):
            score += 0.3

        return score

    def evaluate_pawn_structure(self, board, color):
        score = 0
        files = [0] * 8  
        
        pawns = board.pieces(chess.PAWN, color)
        for square in pawns:
            file = chess.square_file(square)
            files[file] += 1
        
       
        for file_count in files:
            if file_count > 1:
                score -= 0.5 * (file_count - 1)  
        
        #isolated pawns
        for file in range(8):
            if files[file] > 0:
                has_neighbor = False
                for adj_file in [file - 1, file + 1]:
                    if 0 <= adj_file <= 7 and files[adj_file] > 0:
                        has_neighbor = True
                        break
                
                if not has_neighbor:
                    score -= 0.5 * files[file]  
        
        #(pawns protecting each other diagonally)
        for square in pawns:
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            direction = 1 if color == chess.WHITE else -1
            
            for file_offset in [-1, 1]:
                if 0 <= file + file_offset <= 7:
                    protector_rank = rank - direction
                    if 0 <= protector_rank <= 7:
                        protector_square = chess.square(file + file_offset, protector_rank)
                        protector = board.piece_at(protector_square)
                        if protector and protector.piece_type == chess.PAWN and protector.color == color:
                            score += 0.2 
        
        return score

    def evaluate_king_safety_combined(self, board, color):
        score = 0
        king_square = board.king(color)
        if king_square is None:
            return 0 

        # Pawn shield around the king
        rank = chess.square_rank(king_square)
        file = chess.square_file(king_square)
        direction = 1 if color == chess.WHITE else -1
        
        pawn_shield_score = 0
        for file_offset in [-1, 0, 1]:
            pawn_file = file + file_offset
            
            pawn_rank_front = rank + direction
            if 0 <= pawn_file <= 7 and 0 <= pawn_rank_front <= 7:
                square_front = chess.square(pawn_file, pawn_rank_front)
                piece_front = board.piece_at(square_front)
                if piece_front and piece_front.piece_type == chess.PAWN and piece_front.color == color:
                    pawn_shield_score += 0.15
            
            # Check squares two ranks in front of the king (for castled positions)
            pawn_rank_further = rank + 2 * direction
            if 0 <= pawn_file <= 7 and 0 <= pawn_rank_further <= 7 and file_offset != 0: # Exclude directly in front
                 square_further = chess.square(pawn_file, pawn_rank_further)
                 piece_further = board.piece_at(square_further)
                 if piece_further and piece_further.piece_type == chess.PAWN and piece_further.color == color:
                    pawn_shield_score += 0.05 # Smaller bonus for further pawns

        score += pawn_shield_score
        
        # Penalize for direct attacks on squares around the king
        opponent_color = not color
        threat_count = 0
        # Iterate over squares surrounding the king
        for r_offset in [-1, 0, 1]:
            for f_offset in [-1, 0, 1]:
                if r_offset == 0 and f_offset == 0:
                    continue # Skip the king's own square
                
                target_rank = rank + r_offset
                target_file = file + f_offset
                
                if 0 <= target_rank <= 7 and 0 <= target_file <= 7:
                    target_square = chess.square(target_file, target_rank)
                    if board.is_attacked_by(opponent_color, target_square):
                        threat_count += 1
        
        score -= threat_count * 0.15 # Penalty for squares around the king being attacked

        
        if color == chess.WHITE:
            if board.has_kingside_castling_rights or board.has_queenside_castling_rights:
                if king_square == chess.G1: score += 0.3
                elif king_square == chess.C1: score += 0.2
        else: 
            if board.has_kingside_castling_rights or board.has_queenside_castling_rights:
                if king_square == chess.G8: score -= 0.3
                elif king_square == chess.C8: score -= 0.2
                
        return score

    def evaluate_king_activity(self, king_square):
        
        if king_square is None:
            return 0
        distance_to_center = min([chess.square_distance(king_square, square) for square in self.central_squares])
        return -distance_to_center * 0.15 

    def evaluate_passed_pawns(self, board, color):
        score = 0
        enemy_color = not color
        pawns = board.pieces(chess.PAWN, color)

        promotion_rank = 7 if color == chess.WHITE else 0

        for square in pawns:
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            
            is_passed = True
            for df in [-1, 0, 1]:
                adj_file = file + df
                if 0 <= adj_file <= 7:
                    if color == chess.WHITE:
                        for r in range(rank + 1, 8):
                            sq = chess.square(adj_file, r)
                            if board.piece_type_at(sq) == chess.PAWN and board.color_at(sq) == enemy_color:
                                is_passed = False
                                break
                    else: 
                        for r in range(rank - 1, -1, -1):
                            sq = chess.square(adj_file, r)
                            if board.piece_type_at(sq) == chess.PAWN and board.color_at(sq) == enemy_color:
                                is_passed = False
                                break
                if not is_passed:
                    break
                    
            if is_passed:
                distance_to_promote = abs(promotion_rank - rank)
                if distance_to_promote == 1:
                    score += 2.0  
                elif distance_to_promote == 2:
                    score += 1.0  
                else:
                    score += 0.5  
        return score

    def check_connected_rooks(self, board, color):
        final_score = 0
        rooks = list(board.pieces(chess.ROOK, color)) 
        if len(rooks) < 2: 
            return 0
        
       
        for i in range(len(rooks)):
            for j in range(i + 1, len(rooks)):
                rook1_square = rooks[i]
                rook2_square = rooks[j]
                
                # Check if they are on the same rank or file and there are no pieces between them
                if chess.square_rank(rook1_square) == chess.square_rank(rook2_square):
                    rank = chess.square_rank(rook1_square)
                    start_file = min(chess.square_file(rook1_square), chess.square_file(rook2_square)) + 1
                    end_file = max(chess.square_file(rook1_square), chess.square_file(rook2_square))
                    is_connected = True
                    for file in range(start_file, end_file):
                        if board.piece_at(chess.square(file, rank)) is not None:
                            is_connected = False
                            break
                    if is_connected:
                        final_score += 0.5 
                elif chess.square_file(rook1_square) == chess.square_file(rook2_square):
                    file = chess.square_file(rook1_square)
                    start_rank = min(chess.square_rank(rook1_square), chess.square_rank(rook2_square)) + 1
                    end_rank = max(chess.square_rank(rook1_square), chess.square_rank(rook2_square))
                    is_connected = True
                    for rank in range(start_rank, end_rank):
                        if board.piece_at(chess.square(file, rank)) is not None:
                            is_connected = False
                            break
                    if is_connected:
                        final_score += 0.5 
        return final_score

    def evaluate_checkmate_or_draw(self, board):
        if board.is_checkmate():
            return 1000 if board.turn == chess.BLACK else -1000 
        if board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition() or board.is_seventyfive_moves():
            return 0 
        return 0

    def evaluate_rook_movement(self, board):
        score = 0
        for color in [chess.WHITE, chess.BLACK]:
            rooks = board.pieces(chess.ROOK, color)
            pawns = board.pieces(chess.PAWN, color)
            
            direction_factor = 1 if color == chess.WHITE else -1

            for rook_square in rooks:
                rook_file = chess.square_file(rook_square)
                rook_rank = chess.square_rank(rook_square)

                # Check for open files
                is_open_file = True
                for rank_idx in range(8):
                    pawn_at_file = board.piece_at(chess.square(rook_file, rank_idx))
                    if pawn_at_file and pawn_at_file.piece_type == chess.PAWN and pawn_at_file.color == color:
                        is_open_file = False
                        break
                if is_open_file:
                    score += direction_factor * 0.4 

                # Check for semi-open files (opponent pawns only)
                is_semi_open_file = False
                if not is_open_file: 
                    is_semi_open_file = True
                    for rank_idx in range(8):
                        pawn_at_file = board.piece_at(chess.square(rook_file, rank_idx))
                        if pawn_at_file and pawn_at_file.piece_type == chess.PAWN and pawn_at_file.color == color:
                            is_semi_open_file = False
                            break
                    if is_semi_open_file:
                        score += direction_factor * 0.2 # Bonus for a semi-open file

                #if rook is blocked by own pawns on its file
                for pawn_square in pawns:
                    if chess.square_file(pawn_square) == rook_file:
                        if color == chess.WHITE and chess.square_rank(pawn_square) > rook_rank:
                            score -= 0.1 * direction_factor
                        elif color == chess.BLACK and chess.square_rank(pawn_square) < rook_rank:
                            score -= 0.1 * direction_factor
        return score

    def evaluate_mobility(self, board):

        white_mobility = 0
        black_mobility = 0
        
      
        original_turn = board.turn
        
        
        board.turn = chess.WHITE
        white_mobility = len(list(board.legal_moves))
        
        
        board.turn = chess.BLACK
        black_mobility = len(list(board.legal_moves))
        
        
        board.turn = original_turn
        
        
        return 0.05 * (white_mobility - black_mobility)

    def evaluate_center_control(self, board):

        score = 0
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        extended_center = [chess.C3, chess.D3, chess.E3, chess.F3, 
                           chess.C4, chess.F4, 
                           chess.C5, chess.F5, 
                           chess.C6, chess.D6, chess.E6, chess.F6]
        

        for square in center_squares:
            piece = board.piece_at(square)
            if piece:
                value = 0.5
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        

        for square in center_squares:
            white_attackers = len(board.attackers(chess.WHITE, square))
            black_attackers = len(board.attackers(chess.BLACK, square))
            score += 0.1 * (white_attackers - black_attackers)
        

        for square in extended_center:
            white_attackers = len(board.attackers(chess.WHITE, square))
            black_attackers = len(board.attackers(chess.BLACK, square))
            score += 0.05 * (white_attackers - black_attackers)
        
        return score

    def evaluate_attacks(self, board): 
            score = 0

            for color in [chess.WHITE, chess.BLACK]:
                factor = 1 if color == chess.WHITE else -1
                
                
                attacking_pieces_bitboard = (
                    board.pieces(chess.KNIGHT, color)
                    | board.pieces(chess.BISHOP, color)
                    | board.pieces(chess.ROOK, color)
                    | board.pieces(chess.QUEEN, color)
                )

                
                for attacker_square in attacking_pieces_bitboard:
                    for target_square in board.attacks(attacker_square):
                        piece = board.piece_at(target_square)
                        if piece and piece.color != color:
                            value = self.get_piece_value(piece)
                            defenders = board.attackers(not color, target_square)

                            if not defenders:
                                score += factor * value * 0.5  # Attack on undefended piece
                            else:
                                score += factor * value * 0.2  # Pressure on defended piece
            return score

    def evaluate_board(self, board):

        terminal_score = self.evaluate_checkmate_or_draw(board)
        if terminal_score != 0:
            return terminal_score

        score = 0
        game_phase = self.get_game_phase(board)


        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.get_piece_value(piece)
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value

        
        score += self.evaluate_pawn_structure(board, chess.WHITE) * 0.8
        score -= self.evaluate_pawn_structure(board, chess.BLACK) * 0.8
        
       
        score += self.evaluate_mobility(board) * 0.1 

       
        score += self.evaluate_center_control(board) * 0.7 

        
        if game_phase == "Opening" or game_phase == "Middlegame":
            score += self.evaluate_king_safety_combined(board, chess.WHITE) * 1.5 
            score -= self.evaluate_king_safety_combined(board, chess.BLACK) * 1.5
        elif game_phase == "Endgame":
            
            white_king_square = board.king(chess.WHITE)
            black_king_square = board.king(chess.BLACK)
            if white_king_square:
                score += self.evaluate_king_activity(white_king_square) * 0.5
            if black_king_square:
                score -= self.evaluate_king_activity(black_king_square) * 0.5

        
        if game_phase == "Opening":
            score += self.evaluate_pieces_deployment(board) * 1.0 
            
            for square in [chess.E4, chess.D4]:
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                    score += 0.5
            for square in [chess.D5, chess.E5]:
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                    score -= 0.5

        elif game_phase == "Middlegame":
            
            score += self.middle_game_knight_deployement(board) * 0.7
           
            score += self.check_connected_rooks(board, chess.WHITE) * 0.4
            score -= self.check_connected_rooks(board, chess.BLACK) * 0.4
            
            score += self.evaluate_rook_movement(board) * 0.3
            
        elif game_phase == "Endgame":
            
            score += self.evaluate_passed_pawns(board, chess.WHITE) * 2.0 
            score -= self.evaluate_passed_pawns(board, chess.BLACK) * 2.0

            
            score += self.close_pawns_to_promote(board) * 1.5 

        
        score += self.evaluate_attacks(board) * 0.6 

        return score
    
  

    def middle_game_knight_deployement(self, board):
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue

            if piece.piece_type == chess.KNIGHT:
                knight_rank = chess.square_rank(square)
                knight_file = chess.square_file(square)

                if piece.color == chess.WHITE:
                    
                    if (knight_rank == 4 and 1 < knight_file < 6): score += 0.3 
                    elif knight_rank == 5: score += 0.5 
                    elif knight_rank == 6: score += 1.5 
                elif piece.color == chess.BLACK:
                    if (knight_rank == 3 and 1 < knight_file < 6): score -= 0.3 
                    elif knight_rank == 2: score -= 0.5
                    elif knight_rank == 1: score -= 1.5
        return score

    def close_pawns_to_promote(self, board):
        score = 0
        for color in [chess.WHITE, chess.BLACK]:
            pawns = board.pieces(chess.PAWN, color)
            promotion_rank = 7 if color == chess.WHITE else 0

            for square in pawns:
                rank = chess.square_rank(square)
                distance = abs(promotion_rank - rank)

                if distance == 1: 
                    bonus = 2
                elif distance == 2: 
                    bonus = 1
                elif distance == 3: 
                    bonus = 0.5
                elif distance ==0:
                    bonus == 9
                else:
                    bonus = 0
                
                score += bonus if color == chess.WHITE else -bonus
        return score