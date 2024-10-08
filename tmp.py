import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
width, height = 300, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Define the shapes of the tetrominoes
shapes = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

# Define the colors for each shape
shape_colors = [CYAN, YELLOW, MAGENTA, BLUE, ORANGE, GREEN, RED]

# Set up the game grid
grid_width, grid_height = 10, 20
grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

# Set up the game clock
clock = pygame.time.Clock()

# Define the Tetromino class
class Tetromino:
    def __init__(self):
        self.shape = random.choice(shapes)
        self.color = shape_colors[shapes.index(self.shape)]
        self.x = grid_width // 2 - len(self.shape[0]) // 2
        self.y = 0

    def move(self, dx, dy):
        if self.is_valid_move(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotate(self):
        rotated_shape = list(zip(*self.shape[::-1]))
        if self.is_valid_move(0, 0, rotated_shape):
            self.shape = rotated_shape

    def is_valid_move(self, dx, dy, shape=None):
        if shape is None:
            shape = self.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x, new_y = self.x + x + dx, self.y + y + dy
                    if (new_x < 0 or new_x >= grid_width or
                        new_y >= grid_height or
                        (new_y >= 0 and grid[new_y][new_x])):
                        return False
        return True

# Game loop
current_piece = Tetromino()
game_over = False

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_piece.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                current_piece.move(1, 0)
            elif event.key == pygame.K_DOWN:
                current_piece.move(0, 1)
            elif event.key == pygame.K_UP:
                current_piece.rotate()

    # Move the piece down
    if not current_piece.move(0, 1):
        # If the piece can't move down, place it on the grid
        for y, row in enumerate(current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid[current_piece.y + y][current_piece.x + x] = current_piece.color

        # Check for completed rows
        completed_rows = [i for i, row in enumerate(grid) if all(row)]
        for row in completed_rows:
            del grid[row]
            grid.insert(0, [0 for _ in range(grid_width)])

        # Create a new piece
        current_piece = Tetromino()
        if not current_piece.is_valid_move(0, 0):
            game_over = True

    # Clear the screen
    screen.fill(BLACK)

    # Draw the grid
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, (x * 30, y * 30, 30, 30))
                pygame.draw.rect(screen, WHITE, (x * 30, y * 30, 30, 30), 1)

    # Draw the current piece
    for y, row in enumerate(current_piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, current_piece.color,
                                 ((current_piece.x + x) * 30, (current_piece.y + y) * 30, 30, 30))
                pygame.draw.rect(screen, WHITE,
                                 ((current_piece.x + x) * 30, (current_piece.y + y) * 30, 30, 30), 1)

    # Update the display
    pygame.display.flip()

    # Control the game speed
    clock.tick(5)

# Quit the game
pygame.quit()
