import pygame
import random
from random import choice
from collections import defaultdict, deque

pygame.font.init()
pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
tile_size = 35

columns = SCREEN_WIDTH//tile_size
rows = SCREEN_HEIGHT//tile_size

run = True
clock = pygame.time.Clock()
class Cell:
    """A class for each cell in the maze"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'bottom': True, 'left': True, 'right': True} # each wall is set to a boolean, true if it exists and false if not
        self.visited = False
        self.thickness = 2

    def draw(self, screen):
        """draws each wall that is 'up' as a red line"""
        x = self.x*tile_size
        y = self.y*tile_size

        if self.walls['top']:
            pygame.draw.line(screen, (255,0,0), (x, y), (x + tile_size, y), self.thickness)
        if self.walls['bottom']:
            pygame.draw.line(screen, (255, 0, 0), (x, y + tile_size), (x + tile_size, y + tile_size), self.thickness)
        if self.walls['right']:
            pygame.draw.line(screen, (255, 0, 0), (x + tile_size, y), (x + tile_size, y + tile_size), self.thickness)
        if self.walls['left']:
            pygame.draw.line(screen, (255, 0, 0), (x, y), (x, y + tile_size), self.thickness)

    def check_cell(self,x,y):
        """checks if a cell exists (not out of bounds)"""
        index = lambda x,y: x+y*columns
        if x<0 or x>columns-1 or y<0 or y>rows-1:
            return False
        return self.grid[index(x, y)]

    def check_neighbor(self, grid):
        """chooses a random, existing, non-visited neighbor"""
        self.grid = grid
        neigh = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neigh.append(top)
        if right and not right.visited:
            neigh.append(right)
        if bottom and not bottom.visited:
            neigh.append(bottom)
        if left and not left.visited:
            neigh.append(left)

        if neigh:
            return choice(neigh)
        else:
            return False

    def get_walls(self):
        """returns which walls of a cell exists"""
        walls = []
        x = self.x * tile_size
        y = self.y * tile_size

        if self.walls['top']:
            walls.append(pygame.Rect((x, y), (tile_size, self.thickness)))
        if self.walls['right']:
            walls.append(pygame.Rect((x + tile_size, y), (self.thickness, tile_size)))
        if self.walls['bottom']:
            walls.append(pygame.Rect((x, y + tile_size), (tile_size, self.thickness)))
        if self.walls['left']:
            walls.append(pygame.Rect((x, y), (self.thickness, tile_size)))
        return walls

def remove_walls(current, next):
    """deletes a wall inbetween two cells"""
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False

def random_remove_walls(current, next):
    """deletes the other wall of the cell (opposite of remove_walls function)"""
    dx = current.x - next.x
    if current.x > 1 and next.x > 1 and current.x < columns -1 and next.x < columns -1:
        if dx == -1:
            current.walls['left'] = False
            next.walls['right'] = False
        elif dx == 1:
            current.walls['right'] = False
            next.walls['left'] = False
    dy = current.y - next.y
    if current.y > 1 and next.y > 1 and current.y < rows -1 and next.y < rows-1:
        if dy == -1:
            current.walls['top'] = False
            next.walls['bottom'] = False
        elif dy == 1:
            current.walls['bottom'] = False
            next.walls['top'] = False

from collections import deque

def generate_maze():
    """randomly generates a maze using DFS"""
    grid = [Cell(column, row) for row in range(rows) for column in range(columns)]
    stack = deque([])
    stack.append(grid[0])
    counter = 0
    current_cell = grid[0]

    while counter < len(grid)-1:
        current_cell.visited = True
        next_cell = current_cell.check_neighbor(grid)
        if next_cell:
            next_cell.visited = True
            stack.append(next_cell)
            remove_walls(current_cell, next_cell)
            surprise = choice([1,2,3])
            if surprise <= 1:
                random_remove_walls(current_cell, next_cell)


            counter += 1
            current_cell = next_cell
        elif stack:
            choose = choice([1,2])
            if choose == 1:
                current_cell = stack.pop()
            elif choose == 2:
                current_cell = stack.popleft()


    return grid

def collide_q_mark(rect, x,y):
    """tests if an object collides with a wall"""
    hyp_player = rect.move(x,y)
    if hyp_player.collidelist(walls) == -1:
        return False
    return True


def maze_to_graph(maze):
    """converts the maze object into a graph dictionary"""
    graph = defaultdict(list)

    for cell in maze:
        x, y = cell.x, cell.y

        if not cell.walls['top'] and y > 0 and not maze[(y - 1) * columns + x].walls['bottom']:
            graph[(x, y)].append((x, y - 1))

        if not cell.walls['bottom'] and y < rows - 1 and not maze[(y + 1) * columns + x].walls['top']:
            graph[(x, y)].append((x, y + 1))

        if not cell.walls['left'] and x > 0 and not maze[y * columns + (x - 1)].walls['right']:
            graph[(x, y)].append((x - 1, y))

        if not cell.walls['right'] and x < columns - 1 and not maze[y * columns + (x + 1)].walls['left']:
            graph[(x, y)].append((x + 1, y))

    return graph

maze_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
maze = generate_maze()
graph = maze_to_graph(maze)

from heapq import heappop, heappush, heapify

def dijkstra(G, s1, s2):
    """this is actually BFS ignore the title"""
    Q = deque([[s1]])
    E = set([s1])

    while Q:
        V = Q.popleft()
        if V[-1] == s2:
            return V
        for W in G[V[-1]]:
            if W not in E:
                Q.append(V+[W])
                E.add(W)

recently_visited = set()

player = pygame.Rect((5,5,25,25))
goal = pygame.Rect((SCREEN_WIDTH-30,SCREEN_HEIGHT-30,25,25))

a = [145,215,285,355,425,495,565,635,705,775,845,915,985,1055,1125,1195,1265,1335]
b = [145,215,285,355,425,495,565,635]

random_enemy = pygame.Rect(choice(a),choice(b),25,25)
random_enemy2 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy3 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy4 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy5 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy6 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy7 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy8 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy9 = pygame.Rect(choice(a), choice(b), 25, 25)
random_enemy10 = pygame.Rect(choice(a), choice(b), 25, 25)

direct = [(3, 0), (-3, 0), (0, 3), (0, -3)]

directions = {'random_enemy': choice(direct),
              'random_enemy2': choice(direct),
              'random_enemy3': choice(direct),
              'random_enemy4': choice(direct),
              'random_enemy5': choice(direct),
              'random_enemy6': choice(direct),
              'random_enemy7': choice(direct),
              'random_enemy8': choice(direct),
              'random_enemy9': choice(direct),
              'random_enemy10': choice(direct),
              }

def random_move_enemy(enemy, enemy_name):
    """moves the enemy object in a random direction until it hits a wall, then changes directions"""
    global directions
    dx, dy = directions[enemy_name]

    next_position = (enemy.x + dx, enemy.y + dy)

    if collide_q_mark(enemy, dx, dy):
        # If it collides with a wall, pick a new direction
        possible_directions = [(3, 0), (-3, 0), (0, 3), (0, -3)]
        opposite_direction = (-dx, -dy)

        # Remove opposite direction to prevent reversing
        possible_directions.remove(opposite_direction)

        valid_directions = [d for d in possible_directions if not collide_q_mark(enemy, d[0], d[1])]

        if not valid_directions:
            valid_directions = [directions[enemy_name]]

        directions[enemy_name] = choice(valid_directions)

    enemy.move_ip(*directions[enemy_name])

walls = sum([cell.get_walls() for cell in maze], [])

def color_cells_in_range(player, grid, range_size=4):
    """colors cells a specific color if within a 4 block path of the player"""
    player_x, player_y = player.x // tile_size, player.y // tile_size

    for dx in range(-range_size, range_size + 1):
        for dy in range(-range_size, range_size + 1):
            target_x = player_x + dx
            target_y = player_y + dy

            if 0 <= target_x < columns and 0 <= target_y < rows:
                cell = grid[target_y * columns + target_x]
                if len(dijkstra(graph, (player_x, player_y), (target_x, target_y))) <= 5:
                    pygame.draw.rect(screen, (50, 0, 0), pygame.Rect(cell.x * tile_size, cell.y * tile_size, tile_size, tile_size))

def color_cells_in_range2(player, grid, range_size=3):
    """colors the cells within a 3 block path of the player"""
    player_x, player_y = player.x // tile_size, player.y // tile_size

    for dx in range(-range_size, range_size + 1):
        for dy in range(-range_size, range_size + 1):
            target_x = player_x + dx
            target_y = player_y + dy

            if 0 <= target_x < columns and 0 <= target_y < rows:
                cell = grid[target_y * columns + target_x]
                if len(dijkstra(graph, (player_x, player_y), (target_x, target_y))) <= 4:
                    pygame.draw.rect(screen, (75, 0, 0), pygame.Rect(cell.x * tile_size, cell.y * tile_size, tile_size, tile_size))

def color_cells_in_range3(player, grid, range_size=2):
    """colors in a 2 block path"""
    player_x, player_y = player.x // tile_size, player.y // tile_size

    for dx in range(-range_size, range_size + 1):
        for dy in range(-range_size, range_size + 1):
            target_x = player_x + dx
            target_y = player_y + dy

            if 0 <= target_x < columns and 0 <= target_y < rows:
                cell = grid[target_y * columns + target_x]
                if len(dijkstra(graph, (player_x, player_y), (target_x, target_y))) <= 3:
                    pygame.draw.rect(screen, (100, 0, 0), pygame.Rect(cell.x * tile_size, cell.y * tile_size, tile_size, tile_size))


def color_cells_in_range4(player, grid, range_size=1):
    """colors cells within a 1 block path of the player"""
    player_x, player_y = player.x // tile_size, player.y // tile_size

    for dx in range(-range_size, range_size + 1):
        for dy in range(-range_size, range_size + 1):
            target_x = player_x + dx
            target_y = player_y + dy

            if 0 <= target_x < columns and 0 <= target_y < rows:
                cell = grid[target_y * columns + target_x]
                if len(dijkstra(graph, (player_x, player_y), (target_x, target_y))) <= 2:
                    pygame.draw.rect(screen, (125, 0, 0), pygame.Rect(cell.x * tile_size, cell.y * tile_size, tile_size, tile_size))

def draw_maze():
    """draws the cells of the maze"""
    for cell in maze:
        cell.draw(screen)

def in_range4(e, p):
    """tests if an enemy is within a 4 block path of the player"""
    if abs((e.x // tile_size) - (p.x // tile_size)) <= 4 and abs((e.y // tile_size) - (p.y // tile_size)) <= 4:
        if len(dijkstra(graph, (p.x//tile_size, p.y//tile_size), (e.x//tile_size, e.y//tile_size))) <= 5:
            return True
    return False

def in_range3(e, p):
    """tests if an enemy is within a 3 block path of the player"""
    if abs((e.x // tile_size) - (p.x // tile_size)) <= 3 and abs((e.y // tile_size) - (p.y // tile_size)) <= 3:
        if len(dijkstra(graph, (p.x // tile_size, p.y // tile_size), (e.x // tile_size, e.y // tile_size))) <= 4:
            return True
    return False

def in_range2(e, p):
    """tests if an enemy is within a 2 block path of the player"""
    if abs((e.x // tile_size) - (p.x // tile_size)) <= 2 and abs((e.y // tile_size) - (p.y // tile_size)) <= 2:
        if len(dijkstra(graph, (p.x // tile_size, p.y // tile_size), (e.x // tile_size, e.y // tile_size))) <= 3:
            return True
    return False

def in_range1(e, p):
    """tests if an enemy is within a 1 block path of the player"""
    if abs((e.x // tile_size) - (p.x // tile_size)) <= 1 and abs((e.y // tile_size) - (p.y // tile_size)) <= 1:
        if len(dijkstra(graph, (p.x // tile_size, p.y // tile_size), (e.x // tile_size, e.y // tile_size))) <= 2:
            return True
    return False

def draw_enemy(en):
    """draws the enemy a specific color depending on closeness to player"""
    if in_range1(en, player):
        pygame.draw.rect(screen, (255, 0, 0), en)
    elif in_range2(en, player):
        pygame.draw.rect(screen, (200, 0, 0), en)
    elif in_range3(en, player):
        pygame.draw.rect(screen, (175, 0, 0), en)
    elif in_range4(en, player):
        pygame.draw.rect(screen, (150, 0, 0), en)
    else:
        pygame.draw.rect(screen, (0, 0, 0), en)


matthew = pygame.image.load("matthew_win.png").convert()
tinymatthew = pygame.transform.scale(matthew,(467,700))
matthew2 = pygame.image.load("matthew_win2.png").convert()
tinymatthew2 = pygame.transform.scale(matthew2,(467,700))
matthew3 = pygame.image.load("IMG_3636.PNG").convert()
tinymatthew3 = pygame.transform.scale(matthew3,(467,700))
youwin = pygame.image.load("youwin.png").convert()
tinyyouwin = pygame.transform.scale(youwin,(700,200))

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill((0,0,0))
    color_cells_in_range(player, maze)
    color_cells_in_range2(player, maze)
    color_cells_in_range3(player, maze)
    color_cells_in_range4(player, maze)

    draw_maze()



    pygame.draw.rect(screen, ('#1fd9e3'), player)
    pygame.draw.rect(screen, (0,255,0), goal)

    draw_enemy(random_enemy)
    draw_enemy(random_enemy2)
    draw_enemy(random_enemy3)
    draw_enemy(random_enemy4)
    draw_enemy(random_enemy5)
    draw_enemy(random_enemy6)
    draw_enemy(random_enemy7)
    draw_enemy(random_enemy8)
    draw_enemy(random_enemy9)
    draw_enemy(random_enemy10)

    key = pygame.key.get_pressed()
    if key[pygame.K_a] == True:
        if collide_q_mark(player, -5, 0)== False:
            player.move_ip(-5, 0)

    elif key[pygame.K_d] == True:
        if collide_q_mark(player, 5, 0) == False:
            player.move_ip(5, 0)

    elif key[pygame.K_w] == True:
        if collide_q_mark(player, 0, -5) == False:
            player.move_ip(0, -5)

    elif key[pygame.K_s] == True:
        if collide_q_mark(player, 0, 5) == False:
            player.move_ip(0, 5)

    elif key[pygame.K_e] == True:
        for move in dijkstra(graph,(player.x//tile_size,player.y//tile_size),(39,19)):
            pygame.draw.rect(screen, (0, 50, 50), pygame.Rect((move[0] * tile_size)+10, (move[1] * tile_size)+10, tile_size-20, tile_size-20))

    elif key[pygame.K_f] == True:
        player.x = SCREEN_WIDTH-30
        player.y = SCREEN_HEIGHT-30


    random_move_enemy(random_enemy, 'random_enemy')
    random_move_enemy(random_enemy2,'random_enemy2')
    random_move_enemy(random_enemy3,'random_enemy3')
    random_move_enemy(random_enemy4,'random_enemy4')
    random_move_enemy(random_enemy5,'random_enemy5')
    random_move_enemy(random_enemy6, 'random_enemy6')
    random_move_enemy(random_enemy7, 'random_enemy7')
    random_move_enemy(random_enemy8, 'random_enemy8')
    random_move_enemy(random_enemy9, 'random_enemy9')
    random_move_enemy(random_enemy10, 'random_enemy10')

    if player.colliderect(random_enemy) or player.colliderect(random_enemy2) or player.colliderect(random_enemy3) or player.colliderect(random_enemy4) or player.colliderect(random_enemy5) or player.colliderect(random_enemy6) or player.colliderect(random_enemy7) or player.colliderect(random_enemy8) or player.colliderect(random_enemy9) or player.colliderect(random_enemy10):
        player.x = 5
        player.y = 5


    if player.colliderect(goal):
        screen.fill((0, 255, 0))
        screen.blit(tinymatthew,(0,0),)
        screen.blit(tinymatthew2, (934,0))
        screen.blit(tinymatthew3, (467,0))
        screen.blit(tinyyouwin,(350,500))



    pygame.display.flip()
    clock.tick(25)