import pygame
import random
#from queue import Queue

pygame.init()

#Set display options
WIDTH, HEIGHT  = 600, 700
BG_COLOUR      = "white"
NUM_FONT       = pygame.font.SysFont('comicsans', 20)
NUM_COLOURS    = {1: "black", 2: "blue", 3: "green", 4:"red", 5: "purple", 6: "orange", 7: "pink", 8:"yellow"}
RECT_COLOUR    = (110, 110, 110)
CLICK_COLOUR   = (200, 200, 200)

#Make a window for the game
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Minesweeper")

# Game setup parameters
ROWS, COLS = 10, 10
MINES = 15
SIZE  = WIDTH / ROWS

# get the neighbors of a grid cell
def get_neighbours(row, col, rows, cols):
    neighbours = []

    if row > 0: # Up
        neighbours.append((row-1, col))
    if row < rows - 1: # down
        neighbours.append((row + 1, col))
    if col > 0: #left
        neighbours.append((row, col-1))
    if col < (cols - 1): # right
        neighbours.append((row, col + 1))
    if row > 0 and col > 0: # diagonal up left
        neighbours.append((row - 1, col -1))
    if row > 0 and col < (cols-1): # diagonal up right
        neighbours.append((row - 1, col + 1))
    if row < (rows - 1) and col > 0: #diagonal bottom left
        neighbours.append((row + 1, col - 1))
    if row < (rows - 1) and col < (cols - 1): # diagonal bottom right
        neighbours.append((row + 1, col + 1))
    
    return neighbours

# make grid
def create_mine_field(rows, cols, mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    mines_created = 0
    while mines_created < mines:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        if pos in mine_positions:
            continue
        
        mines_created += 1
        mine_positions.add(pos)
        field[row][col] = -1
        neighbors = get_neighbours(row, col, rows, cols)
        for neighbor in neighbors:
            if neighbor in mine_positions: continue
            field[neighbor[0]][neighbor[1]] += 1
    
    return field


#draw window
def draw(win, field, cover_field):
    win.fill(BG_COLOUR)

    for i, row in enumerate(field):
        y = SIZE * i
        for j, value in enumerate(row):
            x = SIZE * j

            is_covered = cover_field[i][j] == 0

            # draw rectangle
            if is_covered:
                pygame.draw.rect(win, RECT_COLOUR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue
            else:
                pygame.draw.rect(win, CLICK_COLOUR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)

            # label number
            if value > 0:
                text = NUM_FONT.render(str(value), 1, NUM_COLOURS[value])
                win.blit(text, (x + SIZE/2 - text.get_width()/2, y + SIZE/2 - text.get_height()/2 ))

    pygame.display.update()

# what squared did we click on?
def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my // SIZE)
    col = int(mx // SIZE)

    return row, col

# when we click on a zero, it need to spring all the zeros and the surrounding numbers, one layer deep.
def uncover_from_position(row, col, cover_field, field):
    # using a queue to hold all the values we need to check
    q = []
    q.append((row, col))

    while len(q) > 0:
        current = q.pop()

        neighbours = get_neighbours(*current, ROWS, COLS)
        for r,c in neighbours:
            cover_field[r][c] = 1
            if field[r][c] == 0:
                q.append((r,c))


# Main loop
def main():
    run = True
    field = create_mine_field(ROWS, COLS, MINES)
    cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue
                cover_field[row][col] = 1
                uncover_from_position(row, col, cover_field, field)

        draw(WIN, field, cover_field)
    
    pygame.quit()

if __name__ == "__main__":
    main()