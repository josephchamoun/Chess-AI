import pygame
from game import ChessGame
from evaluations import MinMax
import chess

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

TEXT_COLOR_DARK = (40, 40, 40) # Dark grey for general text
TEXT_COLOR_WHITE = (255, 255, 255) # White text
TEXT_COLOR_WIN = (0, 150, 0) # Green for win message
TEXT_COLOR_LOSS = (150, 0, 0) # Dark red for loss message
TEXT_COLOR_DRAW = (100, 100, 100) # Grey for draw message

INFO_PANEL_BG = (70, 70, 70) # Dark grey background for the info panel

# --- Pygame Setup ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Chess GUI")

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
pygame.font.init() # Initialize font module
FONT_DEFAULT = pygame.font.SysFont("Arial", 28, bold=True)
FONT_SCORE = pygame.font.SysFont("Arial", 36, bold=True) # Slightly smaller score font
FONT_MESSAGE = pygame.font.SysFont("Arial", 48, bold=True)

# --- Drawing Functions ---

def draw_turn_info(game):
    turn_text = "White's Turn" if game.is_white_turn() else "Black's Turn"
    text_surface = FONT_DEFAULT.render(turn_text, True, TEXT_COLOR_WHITE)

    # Position the turn info in the info panel (centered)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, WIDTH + INFO_PANEL_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def game_score(game):
    minmax = MinMax()
    score = minmax.evaluate_board(game.board)

    # Determine score text color
    if score > 0:
        score_color = TEXT_COLOR_WIN
    elif score < 0:
        score_color = TEXT_COLOR_LOSS
    else:
        score_color = TEXT_COLOR_WHITE # Neutral for zero score

    score_text = f"Score: {score:.1f}" # Format score to one decimal place
    text_surface = FONT_SCORE.render(score_text, True, score_color)

    # NEW POSITION: Top-left of the info panel, with some padding
    text_rect = text_surface.get_rect(midleft=(20, WIDTH + INFO_PANEL_HEIGHT // 2)) # 20px from left edge
    screen.blit(text_surface, text_rect)

def highlight_square(square, color):
    """Draws a semi-transparent colored overlay on a square."""
    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA) # Create a surface with alpha channel
    s.fill(color)
    row = 7 - chess.square_rank(square)
    col = chess.square_file(square)
    screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def highlight_legal_move(square, is_capture):
    """Highlights legal moves, differentiating between empty squares and captures."""
    if is_capture:
        highlight_square(square, HIGHLIGHT_CAPTURE)
    else:
        # Draw a small transparent circle in the center for empty squares
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        
        # Outer darker circle for subtle depth
        pygame.draw.circle(screen, HIGHLIGHT_LEGAL_MOVE_DOT, (center_x, center_y), SQUARE_SIZE // 4)
        # Inner colored circle
        pygame.draw.circle(screen, HIGHLIGHT_LEGAL_MOVE_RING, (center_x, center_y), SQUARE_SIZE // 5)


def display_message(screen, message, result_type):
    """Displays game over messages with a semi-transparent overlay."""
    # Draw a semi-transparent overlay over the entire screen
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Dark, mostly opaque
    screen.blit(overlay, (0, 0))

    # Determine message color based on result
    if "White wins" in message:
        msg_color = TEXT_COLOR_WIN
    elif "Black wins" in message:
        msg_color = TEXT_COLOR_LOSS
    elif "Draw" in message:
        msg_color = TEXT_COLOR_DRAW
    else:
        msg_color = TEXT_COLOR_WHITE # Default for other messages

    text_surface = FONT_MESSAGE.render(message, True, msg_color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)) # Centered on screen
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def draw_board(game):
    """Draws the chessboard and pieces."""
    colors = [pygame.Color(BOARD_LIGHT), pygame.Color(BOARD_DARK)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Get the chess.square object
            square = chess.square(col, 7 - row) # chess.square expects file, then rank (col, row from bottom)
            
            piece = game.get_piece_at(square)
            if piece:
                color_letter = 'w' if piece.color == chess.WHITE else 'b'
                img = pieces[color_letter + piece.symbol().upper()]
                screen.blit(img, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Draw a strong border around the board
    pygame.draw.rect(screen, BOARD_BORDER_COLOR, (0, 0, WIDTH, WIDTH), 3) # (x, y, width, height), thickness

# Convert mouse click to square
def get_square(pos):
    """Converts pixel coordinates to a chess.square object."""
    x, y = pos
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE) # Flip y-axis for chess.square (0-7 from bottom)
    return chess.square(col, row)

# --- Main Game Loop ---
def main():
    game = ChessGame()
    clock = pygame.time.Clock()
    running = True
    selected_square = None
    legal_moves_for_selected = [] # Store chess.Move objects or target squares

    while running:
        # Check for game over
        if game.is_game_over():
            result = game.get_result()
            display_message(screen, "Game Over! " + result, result)
            pygame.time.wait(3000) # Wait 3 seconds
            game.reset() # Reset the game for a new round
            selected_square = None
            legal_moves_for_selected = []

        # Drawing sequence
        screen.fill(INFO_PANEL_BG) # Fill the entire screen with a consistent background

        draw_board(game)

        # Highlight king if in check
        if game.is_check():
            check_square = game.get_king_square(game.board.turn)
            highlight_square(check_square, CHECK_HIGHLIGHT)
        
        # Highlight selected square
        if selected_square is not None:
            highlight_square(selected_square, HIGHLIGHT_SELECTED)
            # Highlight legal moves
            for move in legal_moves_for_selected:
                target_square = move.to_square
                is_capture = game.get_piece_at(target_square) is not None # Check if target square has a piece
                highlight_legal_move(target_square, is_capture)

        # Draw info panel elements
        draw_turn_info(game)
        game_score(game) # Now draws in the new position

        pygame.display.flip()
        clock.tick(60) # Cap frame rate at 60 FPS

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = get_square(pygame.mouse.get_pos())
                piece = game.get_piece_at(square)

                if selected_square is None:
                    # No square selected, try to select a piece of the current player's color
                    if piece and piece.color == game.board.turn:
                        selected_square = square
                        # Get legal moves for the selected piece
                        legal_moves_for_selected = [
                            move for move in game.board.legal_moves if move.from_square == selected_square
                        ]
                else:
                    # A square is already selected, try to make a move
                    move_made = False
                    for move in legal_moves_for_selected:
                        if move.from_square == selected_square and move.to_square == square:
                            if game.try_move(selected_square, square): # try_move handles promotion
                                move_made = True
                                break
                    
                    if not move_made: # If the attempted move was not legal or tried to pick up new piece
                        # If clicking on a different piece of the same color, re-select
                        if piece and piece.color == game.board.turn:
                            selected_square = square
                            legal_moves_for_selected = [
                                move for move in game.board.legal_moves if move.from_square == selected_square
                            ]
                        else: # Deselect if clicking an empty square or opponent's piece
                            selected_square = None
                            legal_moves_for_selected = []
                    else: # Move was successfully made
                        selected_square = None
                        legal_moves_for_selected = []

    pygame.quit()

if __name__ == "__main__":
    main()