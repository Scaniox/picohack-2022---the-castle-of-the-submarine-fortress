import pygame as pg
import random as rng
import Sprites as sprites

def check_collidable(sprite):
        return  type(sprite).__name__ in ["Wall", "Block", "Gateway", "Exit"]

class Maze():
    def __init__(self, game, msize, seed):
        # store maze size and seed
        self.game = game
        self.msize = msize
        self.seed = seed

        # initialise sprite groups
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.maze_walls = pg.sprite.Group()
        self.gateways = pg.sprite.Group()
        self.blocks = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.checkpoints = pg.sprite.Group()
        self.keys = pg.sprite.Group()

    def setup(self):
        """initialises the self dependent aspects of the maze:
            sprite generation is dependent on this wall object aready having
            been constructed"""
        # initialise RNG
        rng.seed(self.seed)

        # generate maze layout
        self.generate_layout()

        # convert layout to wall sprites
        def wall_gen(pos):
            return sprites.Wall(self.game, pos)
        self.layout_to_board(wall_gen)

        # find start to end path
        path_end = [self.end[0]-1, self.end[1]]
        self.start_to_end_path = self.get_shortest_path(self.start, path_end)

        # populate
        self.populate()

    def generate_layout(self):
        """generates a maze layout"""
        # uses kruskal's algorithm to generate maze layout
        # init layout array
        layout = [list([True, True, x + y * self.msize[0]] 
                 for x in range(0, self.msize[0])) 
                 for y in range(0, self.msize[1])]

        # generate list of all unchecked walls bellow
        unchecked_walls = []
        # - 1 stops it from checking bottom most walls
        for y in range(0, self.msize[1]-1):
            for x in range(0, self.msize[0]):
                unchecked_walls.append([x,y,0])

        # generate a list of unchecked walls on right
        for y in range(0, self.msize[1]):
            # - 1 stops it from checking right most walls
            for x in range(0, self.msize[0]-1):
                unchecked_walls.append([x,y,1])

        # iterate over all walls randomly, removing them if possible
        while len(unchecked_walls) > 0:
            # select random wall
            wall = rng.choice(unchecked_walls)
            x = wall[0]
            y = wall[1]
            if wall[2]:  # is left right wall
                zone1 = layout[y][x][2]
                zone2 = layout[y][x+1][2]

                # check if this wall merges zones
                if zone1 != zone2:
                    # delete this wall
                    layout[y][x][1] = False

                    # merge zones
                    for row in layout:
                        for node in row:
                            if node[2] == zone2:
                                node[2] = zone1

            else:  # is up down wall
                zone1 = layout[y][x][2]
                zone2 = layout[y+1][x][2]

                # check if this wall merges zones
                if zone1 != zone2:
                    # delete this wall
                    layout[y][x][0] = False

                    # merge zones
                    for row in layout:
                        for node in row:
                            if node[2] == zone2:
                                node[2] = zone1

            # remove wall from unchecked walls
            unchecked_walls.remove(wall)

        # store layout to attribute
        self.layout = layout

    def layout_to_board(self, wall_gen):
        """converts the maze layout to a board and sprites"""
        # adjust wall gen to append created walls to the correct groups
        def wall_gen_group(start_pos):
            wall = wall_gen(start_pos)
            self.all_sprites.add(wall)
            self.maze_walls.add(wall)
            return wall

        # generate board array
        # initalise blank array
        bsize = [2 * self.msize[i] + 1 for i in (0,1)]
        board = [list(False
                for x in range(0, bsize[0]))
                for y in range(0, bsize[1])]

        # place perimiter sprites on board
        for x in range(0, bsize[0]): # top and bottom edges
            board[0][x] = wall_gen_group((x, 0))
            board[bsize[1]-1][x] = wall_gen_group((x, bsize[1]-1))

        for y in range(1, bsize[1]-2): # side edges
            board[y][0] = wall_gen_group((0, y))
            board[y][bsize[0]-1] = wall_gen_group((bsize[0]-1, y))
        board[bsize[1]-2][0] = wall_gen_group((0, bsize[1]-2))

        #place corner sprites on board
        for y in range(2, bsize[1], 2):
            for x in range(2, bsize[0], 2):
                board[y][x] = wall_gen_group((x,y))

        # place edge horizontal edge sprites on board
        for ly in range(self.msize[1]-1):
            for lx in range(self.msize[0]):
                by = 2*ly + 1
                bx = 2*lx + 1

                if self.layout[ly][lx][0]: # wall bellow
                    board[by+1][bx] = wall_gen_group((bx, by+1))

        # place vertical edge sprites on board
        for ly in range(self.msize[1]):
            for lx in range(self.msize[0]-1):
                by = 2*ly + 1
                bx = 2*lx + 1

                if self.layout[ly][lx][1]: # wall right
                    board[by][bx+1] = wall_gen_group((bx+1, by))

        self.board = board
        self.bsize = bsize

        # generate start
        self.start = [1, 1]

        # generate end
        self.end = [bsize[0]-1, bsize[1]-2]
        self.exit = sprites.Exit(self.game, self.end)
        self.all_sprites.add(self.exit)
        # place exit in board
        self.board[-2][-1] = self.exit

    def populate(self):
        """populates the maze with sprites"""
        # populate gateways and blocks

        path_len = len(self.start_to_end_path)
        remaining_colours = [i for i in range(6)] # colours not used so far
        allowed_colours = [] # colours of blocks with no gateway

        node_index = path_len * self.game.config.maze_blocks_start_proportion

        while node_index + 1 < path_len and len(remaining_colours) > 0:
            node_index = round(node_index)

            # select current node from path
            current_node = self.start_to_end_path[node_index]
            next_node = self.start_to_end_path[node_index + 1]

            # branch
            branch_node = self.branch(current_node, [next_node])

            # place block at branch_node
            block_colour = rng.choice(remaining_colours)
            remaining_colours.remove(block_colour)
            allowed_colours.append(block_colour)

            block = sprites.Block(self.game, branch_node, block_colour)
            self.board[branch_node[1]][branch_node[0]] = block
            self.all_sprites.add(block)
            self.blocks.add(block)

            # conditionally set gateway to next node along path
            if rng.random() > self.game.config.maze_gateway_skip_threshold:
                gateway_colour = rng.choice(allowed_colours)
                allowed_colours.remove(gateway_colour)

                gateway = sprites.Gateway(self.game, next_node, gateway_colour)
                self.board[next_node[1]][next_node[0]] = gateway
                self.all_sprites.add(gateway)
                self.gateways.add(gateway)

            # increase node_index
            node_index += path_len * \
                          self.game.config.maze_blocks_distance_proportion

            # increment node index by a small random value
            node_index += rng.random() * self.game.config.maze_gateway_jitter

        # populate keys
        for _ in range(self.game.config.maze_key_count):
            pos = self.random_board_spot()
            while self.board[pos[1]][pos[0]] != False:
                pos = self.random_board_spot()

            key = sprites.Key(self.game, pos)
            self.board[pos[1]][pos[0]] = key
            self.all_sprites.add(key)
            self.keys.add(key)

        # populate checkpoints
        for _ in range(self.game.config.maze_checkpoint_count):
            pos = self.random_board_spot()
            while self.board[pos[1]][pos[0]] != False:
                pos = self.random_board_spot()

            checkpoint = sprites.Checkpoint(self.game, pos)
            self.board[pos[1]][pos[0]] = checkpoint
            self.all_sprites.add(checkpoint)
            self.checkpoints.add(checkpoint)

        # populate enemies
        for _ in range(self.game.config.maze_enemy_count):
            pos = self.random_board_spot()
            while self.board[pos[1]][pos[0]] != False:
                pos = self.random_board_spot()

            enemy = sprites.Enemy(self.game, pos)
            self.board[pos[1]][pos[0]] = enemy
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def get_shortest_path(self, start, end):
        """returns (list) path from start to end"""
        # dijkstra's algorithm

        # trivial path
        if start == end:
            return [start]

        # place start node in nodes to search
        nodes_to_search = [tuple(start)]
        known_nodes = {tuple(start): False}

        while len(nodes_to_search) > 0:
            current_node_pos = nodes_to_search.pop(0)

            for offset in [(0,-1), (0,1), (1,0), (-1,0)]:
                neighbour = tuple([current_node_pos[i] + offset[i] for i in (0,1)])
                # check neighbour is a wall
                if check_collidable(self.board[neighbour[1]][neighbour[0]]):
                    continue

                # check neighbour has already been searched
                if neighbour in known_nodes.keys():
                    continue

                # new node; add to known nodes and append to nodes_to_search
                known_nodes[tuple(neighbour)] = current_node_pos
                nodes_to_search.append(neighbour)

        # use known nodes to construct a path from end to start
        end_to_start = []
        current_node = tuple(end)
        if tuple(current_node) in known_nodes.keys():
            while known_nodes[tuple(current_node)] != False:
                end_to_start.append(current_node)
                current_node = known_nodes[current_node]
            
            end_to_start.append(start)

            # reverse end_to_start to get start_to_end
            return end_to_start[::-1]
        else:
            return([end])

    def branch(self, start_node, known_nodes):
        """branches out from a start node to another node in the maze"""

        nodes_to_search = [start_node]

        while len(nodes_to_search) > 0:

            current_node_pos = nodes_to_search.pop(0)

            for offset in [(0,-1), (0,1), (1,0), (-1,0)]:
                neighbour = [current_node_pos[i] + offset[i] for i in (0,1)]
                neighbour = tuple(neighbour)
                # check neighbour is a wall
                if check_collidable(self.board[neighbour[1]][neighbour[0]]):
                    continue

                # check neighbour has already been searched
                if neighbour in known_nodes:
                    continue

                # new node; add to known nodes and append to nodes_to_search
                known_nodes.append(neighbour)
                nodes_to_search.append(neighbour)

            if rng.random() < self.game.config.maze_branch_stop_threshold:
                break

        return current_node_pos

    def random_board_spot(self):
        """returns (tuple) random point on the board"""
        return [rng.randint(0, self.bsize[i]-1) for i in [0,1]]
