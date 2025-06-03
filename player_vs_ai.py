import pygame
from game import ChessGame  # Assumes ChessGame class is in game.py
import chess
from evaluations import MinMax  # Assumes MinMax class is in evaluations.py
from minmax import find_best_move  # Assumes find_best_move function is in minmax.py

pygame.init()

# --- Constants for colors and dimensions ---
WIDTH, HEIGHT = 640, 700
SQUARE_SIZE = WIDTH // 8
INFO_PANEL_HEIGHT = HEIGHT - WIDTH # Space below the board for info

# Colors for the board
BOARD_LIGHT = (230, 205, 170) # Light wood
BOARD_DARK = (170, 125, 90)   # Dark wood
BOARD_BORDER_COLOR = (50, 50, 50) # Dark grey for board border

# Colors for highlights and text
HIGHLIGHT_SELECTED = (255, 215, 0, 150) # Gold, semi-transparent
HIGHLIGHT_LEGAL_MOVE_DOT = (0, 0, 0, 50) # Small, transparent dark dot for empty squares
HIGHLIGHT_LEGAL_MOVE_RING = (100, 150, 255, 100) # Soft blue, semi-transparent ring
HIGHLIGHT_CAPTURE = (200, 50, 50, 150) # Reddish, semi-transparent for captures
CHECK_HIGHLIGHT = (255, 0, 0, 180) # More opaque red for check

TEXT_COLOR_WHITE = (255, 255, 255) # White text for info panel
TEXT_COLOR_WIN = (0, 150, 0) # Green for positive score/win message
TEXT_COLOR_LOSS = (150, 0, 0) # Dark red for negative score/loss message
TEXT_COLOR_DRAW = (100, 100, 100) # Grey for draw message
TEXT_COLOR_PHASE = (0, 150, 200) # Blue for game phase info

INFO_PANEL_BG = (70, 70, 70) # Dark grey background for the info panel

# --- Pygame Setup ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Chess GUI (Player vs AI)")

# Load images
pieces = {}
for color in ['w', 'b']:
    for piece in ['P', 'R', 'N', 'B', 'Q', 'K']:
        try:
            img = pygame.image.load(f"images/{color}{piece}.png")
            img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
            pieces[color + piece] = img
        except pygame.error:
            print(f"Error loading image: images/{color}{piece}.png. Make sure the 'images' folder exists and contains all piece images.")
            # Fallback for missing images (you might want a placeholder)
            pieces[color + piece] = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            pieces[color + piece].fill((100, 100, 100)) # Gray square as placeholder

# --- Font Setup ---
pygame.font.init()
FONT_DEFAULT = pygame.font.SysFont("Arial", 28, bold=True)
FONT_SCORE_PHASE = pygame.font.SysFont("Arial", 24, bold=True)
FONT_MESSAGE = pygame.font.SysFont("Arial", 48, bold=True)

# --- Drawing Functions ---

def draw_info_panel(game):
    """Draws the turn info, score, and game phase in the dedicated info panel."""
    # Fill the info panel background
    pygame.draw.rect(screen, INFO_PANEL_BG, (0, WIDTH, WIDTH, INFO_PANEL_HEIGHT))

    # --- Turn Info ---
    turn_text = "White's Turn" if game.is_white_turn() else "Black's Turn"
    text_surface = FONT_DEFAULT.render(turn_text, True, TEXT_COLOR_WHITE)
    # Centered horizontally in the info panel
    text_rect = text_surface.get_rect(center=(WIDTH // 2, WIDTH + INFO_PANEL_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

    # --- Score (Evaluation) ---
    evaluator = MinMax()
    score = evaluator.evaluate_board(game.board)

    # Determine score text color
    if score > 0:
        score_color = TEXT_COLOR_WIN
    elif score < 0:
        score_color = TEXT_COLOR_LOSS
    else:
        score_color = TEXT_COLOR_WHITE

    score_text = f"Score: {score:.2f}"
    score_surface = FONT_SCORE_PHASE.render(score_text, True, score_color)
    # Position on the left side of the info panel, slightly above center
    score_rect = score_surface.get_rect(midleft=(20, WIDTH + INFO_PANEL_HEIGHT // 2 - 15))
    screen.blit(score_surface, score_rect)

    # --- Game Phase ---
    phase = evaluator.get_game_phase(game.board)
    phase_text = f"Phase: {phase.capitalize()}" # Capitalize the phase name
    phase_surface = FONT_SCORE_PHASE.render(phase_text, True, TEXT_COLOR_PHASE)
    # Position on the left side of the info panel, slightly below center
    phase_rect = phase_surface.get_rect(midleft=(20, WIDTH + INFO_PANEL_HEIGHT // 2 + 15))
    screen.blit(phase_surface, phase_rect)


def highlight_square(square, color):
    """Draws a semi-transparent colored overlay on a square."""
    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    s.fill(color)
    row = 7 - chess.square_rank(square)
    col = chess.square_file(square)
    screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def highlight_legal_move(square, is_capture):
    """Highlights legal moves, differentiating between empty squares and captures."""
    if is_capture:
        highlight_square(square, HIGHLIGHT_CAPTURE)
    else:
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        
        pygame.draw.circle(screen, HIGHLIGHT_LEGAL_MOVE_DOT, (center_x, center_y), SQUARE_SIZE // 4)
        pygame.draw.circle(screen, HIGHLIGHT_LEGAL_MOVE_RING, (center_x, center_y), SQUARE_SIZE // 5)

def display_message(message, result_type):
    """Displays game over messages with a semi-transparent overlay."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Dark, mostly opaque overlay
    screen.blit(overlay, (0, 0))

    if "White wins" in message:
        msg_color = TEXT_COLOR_WIN
    elif "Black wins" in message:
        msg_color = TEXT_COLOR_LOSS
    elif "Draw" in message:
        msg_color = TEXT_COLOR_DRAW
    else:
        msg_color = TEXT_COLOR_WHITE

    text_surface = FONT_MESSAGE.render(message, True, msg_color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def draw_board(game):
    """Draws the chessboard and pieces."""
    colors = [pygame.Color(BOARD_LIGHT), pygame.Color(BOARD_DARK)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            square = chess.square(col, 7 - row)
            piece = game.get_piece_at(square)
            if piece:
                color_letter = 'w' if piece.color == chess.WHITE else 'b'
                img = pieces[color_letter + piece.symbol().upper()]
                screen.blit(img, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    pygame.draw.rect(screen, BOARD_BORDER_COLOR, (0, 0, WIDTH, WIDTH), 3)

def get_square(pos):
    """Converts pixel coordinates to a chess.square object."""
    x, y = pos
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE)
    return chess.square(col, row)

def main():
    game = ChessGame()
    clock = pygame.time.Clock()
    running = True
    selected_square = None
    legal_moves_for_selected = [] 

    AI_DEPTH = 4 
    PLAYER_COLOR = chess.BLACK 

    while running:
      
        if game.is_game_over():
            result = game.get_result()
            display_message("Game Over! " + result, result)
            pygame.time.wait(3000)
            game.reset()
            selected_square = None
            legal_moves_for_selected = []
            continue 

        
        screen.fill(INFO_PANEL_BG) 
        draw_board(game)

        
        if game.is_check():
            check_square = game.get_king_square(game.board.turn)
            highlight_square(check_square, CHECK_HIGHLIGHT)
        
    
        if selected_square is not None:
            highlight_square(selected_square, HIGHLIGHT_SELECTED)
            for move in legal_moves_for_selected:
                target_square = move.to_square
                is_capture = game.get_piece_at(target_square) is not None
                highlight_legal_move(target_square, is_capture)

        draw_info_panel(game)
        pygame.display.flip()
        clock.tick(60)

        # --- AI Turn ---
        if game.board.turn != PLAYER_COLOR: 
            pygame.time.wait(500)
            print("AI is thinking...") 
            best_move = find_best_move(game.board, AI_DEPTH)
            if best_move:
                print(f"AI makes move: {best_move.uci()}") 
                
                game.try_move(best_move.from_square, best_move.to_square)
           
            selected_square = None
            legal_moves_for_selected = []
            continue 

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
               
                mouse_y = pygame.mouse.get_pos()[1]
                if mouse_y >= WIDTH: 
                    continue 

                square = get_square(pygame.mouse.get_pos())
                piece = game.get_piece_at(square)

                if selected_square is None:
            
                    if piece and piece.color == PLAYER_COLOR:
                        selected_square = square
                
                        legal_moves_for_selected = [
                            move for move in game.board.legal_moves if move.from_square == selected_square
                        ]
                else:
               
                    move_made = False
                    for move in legal_moves_for_selected:
                        if move.from_square == selected_square and move.to_square == square:
                       
                            if game.try_move(move.from_square, move.to_square):
                                move_made = True
                                break
                    
                    if not move_made:
                 
                
                        if piece and piece.color == PLAYER_COLOR:
                            selected_square = square 
                            legal_moves_for_selected = [
                                move for move in game.board.legal_moves if move.from_square == selected_square
                            ]
                        else: 
                            selected_square = None
                            legal_moves_for_selected = []
                    else:
                        selected_square = None
                        legal_moves_for_selected = []

    pygame.quit()

if __name__ == "__main__":
    main()