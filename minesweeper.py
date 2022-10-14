import pygame
import random
import time
#from queue import Queue

pygame.init()

#Set display options
WIDTH, HEIGHT  = 600, 700
BG_COLOUR      = "white"
NUM_FONT       = pygame.font.SysFont('comicsans', 20)
NUM_COLOURS    = {1: "black", 2: "blue", 3: "green", 4:"red", 5: "purple", 6: "orange", 7: "pink", 8:"yellow"}
RECT_COLOUR    = (110, 110, 110)
CLICK_COLOUR   = (200, 200, 200)
FLAG_COLOUR    = "red"
MINE_COLOUR    = "black"
LOST_FONT      = pygame.font.SysFont('comicsans', 100)
LOST_COLOUR    = "orange"
WON_FONT       = pygame.font.SysFont('comicsans', 100)
WON_COLOUR     = "green"
TIME_FONT      = pygame.font.SysFont('comicsans', 30)
FLAG_FONT      = pygame.font.SysFont('comicsans', 26)

#Make a window for the game
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Minesweeper")

# Game setup parameters
ROWS, COLS = 10, 10
MINES = 15
SIZE  = WIDTH / ROWS
N_FLAGS = MINES

# get the neighbors of a grid cell
def get_neighbours(row, col, rows, cols):
    neighbours = []

    if row > 0: # Up
        neighbours.append((row - 1, col))
    if row < (rows - 1): # down
        neighbours.append((row + 1, col))
    if col > 0: #left
        neighbours.append((row, col - 1))
    if col < (cols - 1): # right
        neighbours.append((row, col + 1))
    if row > 0 and col > 0: # diagonal up left
        neighbours.append((row - 1, col - 1))
    if row > 0 and col < (cols - 1): # diagonal up right
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

# player lost outcome
def draw_lost(win, text_val):
    text = LOST_FONT.render(text_val, 1, LOST_COLOUR)
    win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
    pygame.display.update()

# player lost outcome
def draw_won(win, text_val):
    text = WON_FONT.render(text_val, 1, WON_COLOUR)
    win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
    pygame.display.update()

#draw window
def draw(win, field, cover_field, current_time, flag_count):
    win.fill(BG_COLOUR)

    time_text = TIME_FONT.render(f"Time: {round(current_time)} s", 1, "black")
    win.blit(time_text, (10, HEIGHT - time_text.get_height()))

    flag_text = FLAG_FONT.render(f"Flag counter: {flag_count} of {N_FLAGS} (right click)", 1, "black")
    win.blit(flag_text, (10, HEIGHT - time_text.get_height() * 2))

    for i, row in enumerate(field):
        y = SIZE * i
        for j, value in enumerate(row):
            x = SIZE * j

            is_covered = cover_field[i][j] == 0
            is_mine = value == -1

            # draw flags
            if cover_field[i][j] == -2:
                pygame.draw.rect(win, FLAG_COLOUR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue

            # draw rectangle
            if is_covered:
                pygame.draw.rect(win, RECT_COLOUR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue
            else:
                pygame.draw.rect(win, CLICK_COLOUR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                if is_mine:
                    pygame.draw.circle(win, MINE_COLOUR, (x + SIZE/2, y + SIZE/2), (SIZE/2) - 3)

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
def uncover_from_position(row, col, cover_field, field, n_flags, flags):
    # using a queue to hold all the values we need to check
    q = []
    q.append((row, col))
    visited = set()

    while len(q) > 0:       # run through all elements in the queue
        current = q.pop()   
        cover_field[current[0]][current[1]] = 1

        if field[current[0]][current[1]] == 0:
            neighbours = get_neighbours(*current, ROWS, COLS)
            for r, c in neighbours:
                if (r, c) in visited: continue

                if cover_field[r][c] == -2: 
                    n_flags += 1
                    flags.remove((r,c))
                cover_field[r][c] = 1   # Our turn clicked a 0, so we want to uncover all the neighbours
                                        # if any of the uncovered neighbors are also zero, add them to the queue
                if (field[r][c] == 0):
                    q.append((r,c))
                visited.add((r,c))

    return cover_field, n_flags

def reset_game():
    field       = create_mine_field(ROWS, COLS, MINES)
    cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    flags       = set()
    flag_count  = N_FLAGS
    lost        = False
    won         = False

    return field, cover_field, flags, flag_count, lost, won

# Main loop
def main():
    run = True
    
    field, cover_field, flags, flag_count, lost, won = reset_game()

    start_time = 0
    clicked    = False
    
    while run:
        if start_time > 0:
            current_time = time.time() - start_time
        else:
            current_time = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                # make sure we aren't off grid
                if row >= ROWS or col >= COLS:
                    continue

                mouse_pressed =  pygame.mouse.get_pressed()
                # left click
                if mouse_pressed[0]:
                    if not clicked: start_time = time.time()
                    clicked = True
                    if cover_field[row][col] != -2:
                        cover_field, flag_count = uncover_from_position(row, col, cover_field, field, flag_count, flags)
                        # check win and lose conditions
                        if field[row][col] < 0:
                            lost = True
                        if (sum(sum(cover_field, [])) + (2 * (N_FLAGS - flag_count))) == (ROWS * COLS - MINES): 
                            won = True
                # right click
                elif mouse_pressed[2]:
                    # place flag
                    if (row, col) in flags:
                        cover_field[row][col] = 0
                        flags.remove((row, col))
                        flag_count += 1
                    elif (flag_count > 0) and (cover_field[row][col] == 0):
                        flags.add((row, col))
                        cover_field[row][col] = -2
                        flag_count -= 1
        draw(WIN, field, cover_field, current_time, flag_count)
        
        if lost:
            draw_lost(WIN, "GAME OVER")
            pygame.time.delay(5000)
            # reset
            field, cover_field, flags, flag_count, lost, won = reset_game()
        if won:
            draw_won(WIN, "YOU WON!")
            pygame.time.delay(5000)
            # reset
            field, cover_field, flags, flag_count, lost, won = reset_game()
    
    pygame.quit()

if __name__ == "__main__":
    main()