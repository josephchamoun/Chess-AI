import pygame
import sys
import subprocess
import math

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Master")
icon = pygame.Surface((32, 32))
icon.fill((0, 0, 0))
pygame.display.set_icon(icon)

# Colors
BG_COLOR = (240, 237, 230)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (181, 136, 99)
GOLD = (212, 175, 55)
HIGHLIGHT = (255, 215, 0)
TEXT_COLOR = (50, 50, 50)
BUTTON_COLOR = (120, 81, 45)
BUTTON_HOVER = (150, 101, 56)

# Fonts
title_font = pygame.font.SysFont("Times New Roman", 60, bold=True)
button_font = pygame.font.SysFont("Arial", 32)
copyright_font = pygame.font.SysFont("Arial", 16)

# Clock for controlling animations
clock = pygame.time.Clock()
FPS = 60

# Load chess piece images (placeholders)
try:
    king_img = pygame.image.load("chess_pieces/king.png")
    king_img = pygame.transform.scale(king_img, (80, 80))
except:
    # Fallback: create a simple crown shape
    king_img = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.polygon(king_img, GOLD, [(40, 10), (50, 30), (65, 30), (55, 45), 
                                          (65, 60), (15, 60), (25, 45), (15, 30), (30, 30)])

# Button class with animations
class Button:
    def __init__(self, text, rect):
        self.text = text
        self.rect = rect
        self.original_rect = rect.copy()
        self.color = BUTTON_COLOR
        self.hover_animation = 0
        self.is_hovered = False
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update hover animation
        if self.is_hovered:
            self.hover_animation = min(1.0, self.hover_animation + 0.1)
        else:
            self.hover_animation = max(0.0, self.hover_animation - 0.1)
            
        # Apply animation effects
        hover_expand = 10 * self.hover_animation
        self.rect.width = self.original_rect.width + hover_expand
        self.rect.height = self.original_rect.height + hover_expand
        self.rect.x = self.original_rect.x - hover_expand / 2
        self.rect.y = self.original_rect.y - hover_expand / 2
        
        # Interpolate color
        r = BUTTON_COLOR[0] + (BUTTON_HOVER[0] - BUTTON_COLOR[0]) * self.hover_animation
        g = BUTTON_COLOR[1] + (BUTTON_HOVER[1] - BUTTON_COLOR[1]) * self.hover_animation
        b = BUTTON_COLOR[2] + (BUTTON_HOVER[2] - BUTTON_COLOR[2]) * self.hover_animation
        self.color = (r, g, b)
        
    def draw(self):
        # Draw button with rounded corners
        pygame.draw.rect(screen, self.color, self.rect, border_radius=12)
        pygame.draw.rect(screen, GOLD, self.rect, width=2, border_radius=12)
        
        # Draw text
        text_surf = button_font.render(self.text, True, BG_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# Create buttons with consistent spacing
buttons = {}
button_texts = ["Player vs Player", "Player vs AI", "AI vs AI", "Exit"]
for i, text in enumerate(button_texts):
    buttons[text] = Button(text, pygame.Rect(WIDTH // 2 - 150, 220 + i * 90, 300, 60))

# Animation variables
time_passed = 0
particles = []

def create_checkerboard():
    board_size = 200
    square_size = board_size // 8
    board_surf = pygame.Surface((board_size, board_size))
    
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(board_surf, color, (col * square_size, row * square_size, square_size, square_size))
    
    return board_surf

def create_particles():
    # Create new particles
    if len(particles) < 30 and pygame.time.get_ticks() % 200 < 20:
        particles.append({
            'x': pygame.time.get_ticks() % WIDTH,
            'y': HEIGHT + 10,
            'size': pygame.time.get_ticks() % 4 + 2,
            'speed': pygame.time.get_ticks() % 3 + 1
        })
    
    # Update and draw particles
    for particle in particles[:]:
        particle['y'] -= particle['speed']
        alpha = min(255, max(0, particle['y']))
        pygame.draw.circle(screen, (GOLD[0], GOLD[1], GOLD[2], alpha), 
                           (particle['x'], particle['y']), particle['size'])
        
        if particle['y'] < -10:
            particles.remove(particle)

def draw_menu():
    # Fill background
    screen.fill(BG_COLOR)
    
    # Draw decorative elements
    time_passed = pygame.time.get_ticks() / 1000
    
    # Animated background pattern
    for i in range(20):
        opacity = 20 + 10 * math.sin(time_passed + i * 0.1)
        line_color = (DARK_BROWN[0], DARK_BROWN[1], DARK_BROWN[2], opacity)
        line_width = 2
        pygame.draw.line(screen, line_color, (0, i * 30), (WIDTH, i * 30), line_width)
        pygame.draw.line(screen, line_color, (i * 40, 0), (i * 40, HEIGHT), line_width)
    
    # Draw checkerboard in the background
    board_surf = create_checkerboard()
    board_rect = board_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
    board_angle = 15 * math.sin(time_passed * 0.2)
    rotated_board = pygame.transform.rotate(board_surf, board_angle)
    rotated_rect = rotated_board.get_rect(center=board_rect.center)
    screen.blit(rotated_board, rotated_rect)
    
    # Create glowing effect for the title
    glow_offset = math.sin(time_passed * 2) * 2
    
    # Draw decorative chess piece
    piece_x = WIDTH // 4
    piece_y = HEIGHT // 4
    piece_bounce = 5 * math.sin(time_passed * 3)
    screen.blit(king_img, (piece_x - king_img.get_width() // 2, 
                          piece_y - king_img.get_height() // 2 + piece_bounce))
    
    # Draw mirrored chess piece on the right
    screen.blit(pygame.transform.flip(king_img, True, False), 
                (WIDTH - piece_x - king_img.get_width() // 2, 
                 piece_y - king_img.get_height() // 2 + piece_bounce))
    
    # Draw title with shadow
    title = title_font.render("Chess Master", True, DARK_BROWN)
    title_shadow = title_font.render("Chess Master", True, GOLD)
    shadow_offset = 2 + glow_offset
    screen.blit(title_shadow, (WIDTH // 2 - title_shadow.get_width() // 2 + shadow_offset, 
                               80 + shadow_offset))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    
    # Draw buttons
    for button in buttons.values():
        button.update()
        button.draw()
    
    # Draw particles
    create_particles()
    
    # Draw copyright
    copyright_text = copyright_font.render("© Chess Master 2025", True, TEXT_COLOR)
    screen.blit(copyright_text, (WIDTH - copyright_text.get_width() - 10, HEIGHT - 30))
    
    pygame.display.flip()

def main_menu():
    while True:
        clock.tick(FPS)
        
        draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for text, button in buttons.items():
                    if button.is_hovered:
                        if text == "Player vs Player":
                            launch_game("pvp")
                        elif text == "Player vs AI":
                            launch_game("ai")
                        elif text == "AI vs AI":
                            launch_game("ai_vs_ai")
                        elif text == "Exit":
                            pygame.quit()
                            sys.exit()

def launch_game(mode):
    if mode == "pvp":
        subprocess.run(["python", "chess_board.py"])
    elif mode == "ai":
        print("Launching Player vs AI mode...")
        subprocess.run(["python", "player_vs_ai.py"])
    elif mode == "ai_vs_ai":
        print("Launching AI vs AI mode...")
        subprocess.run(["python", "ai_vs_ai.py"])

if __name__ == "__main__":
    main_menu()