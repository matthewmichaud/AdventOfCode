from collections import deque
import networkx as nx

class Unit:
    def __init__(self, unit_type, x, y, d):
        self.unit_type = unit_type
        self.x = x
        self.y = y
        self.is_alive = True
        self.hp = 200
        self.attack_damage = d

    def pos(self):
        return self.x, self.y

    def attack(self, damage):
        if self.is_alive:
            self.hp -= damage
            if self.hp <= 0:
                self.is_alive = False

# finds nodes in tarets that have the same shortest path distance from start
# without visiting a node in excluded_nodes
def find_closest(graph, excluded_nodes, start, targets):
    if start not in graph:
        return [], None
    seen = set()
    q = deque([(start, 0)])
    found_dist = None
    closest = []
    while q:
        cell, dist = q.popleft()
        if found_dist is not None and dist > found_dist:
            return closest, found_dist
        if cell in seen or cell in excluded_nodes:
            continue
        seen.add(cell)
        if cell in targets:
            found_dist = dist
            closest.append(cell)
        for n in graph.neighbors(cell):
            if n not in seen:
                q.append((n, dist + 1))
    return closest, found_dist

def neighbors(x, y):
    return [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]

def reading_order(pos):
    return pos[1], pos[0]

def solve(d, no_elves_die):
    input_data = open('2018/inputs/2018_15_input.txt').read()
    data = [list(line) for line in input_data.split('\n')]

    # extract characters / units from the grid and replace with dots
    units = []
    for y in range(len(data)):
        for x in range(len(data[0])):
            t = data[y][x]
            if t in 'GE':
                units.append(Unit(t, x, y, 3 if t == 'G' else d))
                data[y][x] = '.'

    # build graph
    G = nx.Graph()
    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x] == '.':
                for (x2, y2) in neighbors(x, y):
                    if 0 <= x2 < len(data[0]) and 0 <= y2 < len(data) and data[y2][x2] == '.':
                        G.add_edge((x, y), (x2, y2))

    round = 0
    while True:
        order = sorted(units, key=lambda c: reading_order(c.pos()))

        for idx, c in enumerate(order):
            if not c.is_alive:
                continue

            # get all opposing units and their positions
            enemies = [e for e in units if e.unit_type != c.unit_type and e.is_alive]
            enemy_positions = [e.pos() for e in enemies]

            # get all cells immediately next to the current unit
            nearby_cells = neighbors(*c.pos())

            # get enemies in range
            enemy_positions_in_range = [p for p in nearby_cells if p in enemy_positions]

            # if no enemies in range, take a step towards
            if not enemy_positions_in_range:
                # get all open positions in grid next to enemey
                surrounding = []
                for e in enemies:
                    surrounding.extend(neighbors(*e.pos()))
                surrounding = [s for s in surrounding if s in G]

                # get all units positions except for the current one
                excluded_nodes = [e.pos() for e in units if e.is_alive and e != c]
                closest_targets, dist = find_closest(G, excluded_nodes, c.pos(), surrounding)

                if closest_targets:
                    # choose the closest by reading order
                    choice = min(closest_targets, key=reading_order)

                    # find the next cell which has a shortest path of the same distance
                    for s in sorted(nearby_cells, key=reading_order):
                        _, d = find_closest(G, excluded_nodes, s, [choice])
                        if d == dist - 1:
                            c.x, c.y = s
                            break

                # update enemies in range if it has changed
                enemy_positions_in_range = [p for p in neighbors(*c.pos()) if p in enemy_positions]

            if enemy_positions_in_range:
                # get the enemy objects at those positions
                enemies = [e for e in enemies if e.pos() in enemy_positions_in_range]

                # find the enemy with lowest health and attack
                lowest_health = min(enemies, key=lambda e: (e.hp, reading_order(e.pos())))
                lowest_health.attack(c.attack_damage)

                # if part 2, return early if an elf dies
                if no_elves_die and lowest_health.unit_type == 'E' and not lowest_health.is_alive:
                    return False, 0

                # check to see if there is only one unit type left
                alive = set(e.unit_type for e in units if e.is_alive)
                if len(alive) == 1:
                    # handle edge case when last enemy dies at end of turn
                    if idx == len(order) - 1:
                        round += 1
                    return True, round * sum(e.hp for e in units if e.is_alive)

        round += 1

_, score = solve(3, False)
print('Part 1 Answer:', score)

i = 3
while True:
    no_elves_die, score = solve(i, True)
    if no_elves_die:
        print('Part 2 Answer:', score)
        break
    i += 1