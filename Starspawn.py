from PIL import Image, ImageFilter, ImageColor
from queue import SimpleQueue as queue
from enum import Enum
import random

size = 160
scale = 1

auto_offset = True
border = False

## Initial File Imports

with open("star.save", "rb") as save:
    data = save.readline()
    
sheet_small = Image.open("SPsmall.png")    
sheet_large = Image.open("SP.png")

empty_small = Image.new("RGBA", (12, 12), ImageColor.colormap["white"])
empty_large = Image.new("RGBA", (24, 24), ImageColor.colormap["white"])

def tileAt(x, y):
    small = sheet_small.crop((x*12, y*12, (x+1)*12, (y+1)*12))
    large = sheet_large.crop((x*24, y*24, (x+1)*24, (y+1)*24))
    return large, small
    
def transparent(image):
    result = image.copy()
    result.putalpha(128)
    return result

## Tile Definitions

class Border(Enum):
    TOP = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    BOTTOM = (0, -1)
    
    def opposite(self):
        if self == Border.TOP:
            return Border.BOTTOM
        if self == Border.LEFT:
            return Border.RIGHT
        if self == Border.RIGHT:
            return Border.LEFT
        if self == Border.BOTTOM:
            return Border.TOP
            
    @staticmethod
    def sheet_pos(neighbor_set):
        x, y = 0, 0
        if Border.LEFT in neighbor_set:
            if Border.RIGHT in neighbor_set:
                x = 3
            else:
                x = 0
        else:
            if Border.RIGHT in neighbor_set:
                x = 2
            else:
                x = 1
        if Border.TOP in neighbor_set:
            if Border.BOTTOM in neighbor_set:
                y = 3
            else:
                y = 0
        else:
            if Border.BOTTOM in neighbor_set:
                y = 2
            else:
                y = 1
        return x, y

class Block():
    all_blocks = dict()
    tiles = (tileAt(0, 0),)
    colors = ((158, 87, 21),)
    index = 4
    def __init__(self, offset, modifier):
        self.tile = self.tiles[0]
        self.color = self.colors[0]
            
    def get_tile(self, neighbors, small=False):
        if small:
            return self.tile[1]
        else:
            return self.tile[0]
        
    def add_neighbor(self, pos, index):
        pass
        
    def remove_neighbor(self, pos, index):
        pass
        
    def clear_neighbors(self):
        pass
        
    @staticmethod
    def from_data(data):
        block_type = Block.all_blocks[int(data[0])]
        offset = int(data[3])
        modifier = int(data[4])
        return block_type(offset, modifier)
        
        
class BlockBordered(Block):
    light_color = (203, 109, 17)
    dark_color = (125, 66, 9)
    generated = False
    sheets = []
    
    
    def __init__(self, offset, modifier):
        super().__init__(offset, modifier)
        self.neighbors = set()
        if not type(self).generated:
            self.sheets.append(self.generate_borders(self.tile))
            type(self).generated = True
        self.sheet, self.sheet_small = self.sheets[0]
            
    def get_tile(self, small=False):
        x, y = Border.sheet_pos(self.neighbors)
        if small:
            return self.sheet_small.crop(x*12, y*12, (x+1)*12, (y+1)*12)
        else:
            return self.sheet_small.crop(x*24, y*24, (x+1)*24, (y+1)*24)
        
    def add_neighbor(self, pos, index):
        self.neighbors.add(pos)
        
    def remove_neighbor(self, pos):
        self.neighbors.remove(pos, index)
        
    def clear_neighbors(self):
        self.neighbors.clear()
        
    def generate_borders(self, tile):
        sheet = Image.new("RGBA", (96, 96), ImageColor.colormap["white"])
        sheet_small = Image.new("RGBA", (48, 48), ImageColor.colormap["white"])
        px = sheet.load()
        px_small = sheet_small.load()
        for i in range(4):
            for j in range(4):
                sheet.paste(tile[0], (i*24, j*24))
                sheet_small.paste(tile[1], (i*12, j*12))
        
        edge_set = set((0, 23, 24, 47, 48, 71, 72, 95))         
        for i in range(96):
            # general edges
            # top
            px[95-i, 0] = self.light_color
            px[95-i, 72] = self.light_color
            # right
            px[95, 95-i] = self.light_color
            px[71, 95-i] = self.light_color
            # bottom
            px[i, 95] = self.dark_color
            px[i, 71] = self.dark_color
            # left
            px[0, i] = self.dark_color
            px[72, i] = self.dark_color
            
            if i not in edge_set:
                # bevel
                # top
                px[95-i, 1] = self.light_color
                px[95-i, 73] = self.light_color
                # right
                px[94, 95-i] = self.light_color
                px[70, 95-i] = self.light_color
                # bottom
                px[i, 94] = self.dark_color
                px[i, 70] = self.dark_color
                # left
                px[1, i] = self.dark_color
                px[73, i] = self.dark_color

        for i in range(48):
            # general edges
            # top
            px_small[47-i, 0] = self.light_color
            px_small[47-i, 36] = self.light_color
            # right
            px_small[47, 47-i] = self.light_color
            px_small[35, 47-i] = self.light_color
            # bottom
            px_small[i, 47] = self.dark_color
            px_small[i, 35] = self.dark_color
            # left
            px_small[0, i] = self.dark_color
            px_small[36, i] = self.dark_color
            
            if i not in edge_set:
                # bevel
                # top
                px_small[47-i, 1] = self.light_color
                px_small[47-i, 37] = self.light_color
                # right
                px_small[46, 47-i] = self.light_color
                px_small[34, 47-i] = self.light_color
                # bottom
                px_small[i, 46] = self.dark_color
                px_small[i, 34] = self.dark_color
                # left
                px_small[1, i] = self.dark_color
                px_small[37, i] = self.dark_color
                
            
        return sheet, sheet_small
                
    
class BlockAct(Block):
    # blue (boost)
    tiles = (tileAt(6, 2),)
    colors = ((0, 138, 255),)
    index = 0
    
class BlockBalk(Block):
    # d_green (anchor)
    tiles = (tileAt(4, 2), tileAt(5, 2))
    colors = ((173, 173, 25),)
    index = 1
    
    
class BlockCalm(Block):
    # l_blue (ice)
    tiles = (tileAt(0, 3),)
    colors = ((163, 237, 255),)
    index = 2
    
class BlockDeath(Block):
    # spooky scary
    colors = ((0, 0, 0),)
    index = 3
    
class BlockDeathGhost(Block):
    # spooky scary
    colors = ((208, 208, 208),)
    index = 3
    
class BlockDeathWandering(Block):
    # spooky scary
    colors = ((208, 208, 208),)
    index = 3
    
class BlockDirt(Block):
    # dirt
    tiles = (tileAt(0, 4), tileAt(0, 5), tileAt(0, 6), tileAt(0, 7))
    colors = ((158, 87, 21), (129, 51, 0))
    index = 4
    
    def __init__(self, offset, modifier):
        super().__init__(offset, modifier)
        tile = random.randint(0, 3)
        self.tile = self.tiles[tile]
        self.color = colors[tile // 2]
    
class BlockFury(Block):
    # orange (arrow)
    tiles = (tileAt(0, 2), tileAt(1, 2), tileAt(2, 2), tileAt(3, 2), )
    colors = ((255, 168, 0),)
    index = 5
              
    def __init__(self, offset, modifier):
        # TODO: Verify modifier
        super().__init__(offset, modifier)
        if modifier == 0:
            self.tile = self.tiles[3]
        else:
            if offset == 2:
                self.tile = self.tiles[0]
            elif offset == 0:
                self.tile = self.tiles[1]
            else:
                self.tile = self.tiles[2]
    
    
class BlockHate(Block):
    # red (mine)
    tiles = (tileAt(6, 1), tileAt(7, 3))
    colors = ((237, 0, 0),)
    index = 6           
    
    def __init__(self, offset, modifier):
        # TODO: Correct offset
        super().__init__(offset, modifier)
        if offset == 1:
            self.tile = self.tiles[0]
        else:
            self.tile = self.tiles[1]
    
class BlockLove(Block):
    # pink (love)
    tiles = (tileAt(0, 1), tileAt(1, 1), tileAt(2, 1), tileAt(3, 1))
    colors = ((255, 85, 205),)
    index = 7
    
    def __init__(self, offset, modifier):
        self.tile = random.choice(tiles)
        self.color = self.colors[0]
    
    
class BlockPortal(Block):
    # portal
    tiles = (tileAt(4, 3), tileAt(5, 3))
    colors = ((109, 129, 144), (255, 254, 199))
    index = 11
    
    def __init__(self, offset, modifier):
        # TODO: Correct offset
        super().__init__(offset, modifier)
        if offset == 1:
            self.tile = self.tiles[0]
            self.color = self.colors[0]
        else:
            self.tile = self.tiles[1]
            self.color = self.colors[1]
    
class BlockRock(BlockBordered):
    # structure
    tiles = (tileAt(7, 2),)
    colors = ((109, 129, 144),)
    index = 10
    light_color = (139, 164, 182)
    dark_color = (60, 79, 94)
    
class BlockVine(BlockBordered):
    # green (garden)
    tiles = (tileAt(1, 3),)
    colors = ((148, 232, 16),)
    index = 8  
    light_color = (196, 254, 37)
    dark_color = (119, 216, 3)
    sheets = []
    def __init__(self, offset, modifier):
        if BlockVine.generated == False:
            for i in range(8):
                rotate = (i % 4) * 90
                flip = i // 4
                tile = [self.tiles[0][0].copy(), self.tiles[0][1].copy()]
                if flip:
                    tile[0] = tile[0].transpose(Image.FLIP_LEFT_RIGHT)
                    tile[1] = tile[1].transpose(Image.FLIP_LEFT_RIGHT)
                tile[0] = tile[0].rotate(rotate)
                tile[1] = tile[1].rotate(rotate)
                self.sheets.append(self.generate_borders(tile))
            BlockVine.generated = True
        super().__init__(offset, modifier)
        self.sheet, self.sheet_small = random.choice(sheets)
    
    
class BlockVoid(Block):
    # void
    pass
    
class BlockWill(Block):
    # purple (pylon)
    tiles = (tileAt(4, 1), tileAt(5, 1))
    colors = ((153, 98, 223),)
    index = 9
    
    def __init__(self, offset, modifier):
        super().__init__(offset, modifier)
        self.tile = random.choice(tiles)

## SP Block Dictionaries

Block.all_blocks[BlockAct.index] = BlockAct
Block.all_blocks[BlockBalk.index] = BlockBalk
Block.all_blocks[BlockCalm.index] = BlockCalm
Block.all_blocks[BlockDeath.index] = BlockDeath
Block.all_blocks[BlockDirt.index] = BlockDirt
Block.all_blocks[BlockFury.index] = BlockFury
Block.all_blocks[BlockHate.index] = BlockHate
Block.all_blocks[BlockLove.index] = BlockLove
Block.all_blocks[BlockPortal.index] = BlockPortal
Block.all_blocks[BlockRock.index] = BlockRock
Block.all_blocks[BlockVine.index] = BlockVine
Block.all_blocks[BlockWill.index] = BlockWill

            
## SPBoard Class and Functions

class SPBoard():
    def __init__(self, size, scale, border, auto_offset):
        self.view_size = size * (2 if border else 1)
        self.size = size
        self.scale = scale
        self.border = border
        self.auto_offset = auto_offset
        self.xoffset = 0
        self.yoffset = 0
        self.rendered = False
        self.map = dict()
        self.invisible = dict()
        self.gateways = set()
        self.structs = set()
        self.user = set()
        
    def place(self, x, y, block):
        x = x % self.view_size
        y = y % self.view_size
        x_draw = (x + self.xoffset) % self.view_size
        y_draw = (y + self.yoffset) % self.view_size
        self.map[(x, y)] = block
        self.set_neighbors(x, y)
            
    def set_neighbors(self, x, y):
        block = self.map[(x, y)]
        for neighbor, dir in neighbors((x, y)):
            if neighbor in self.map:
                block_near = self.map[neighbor]
                block.neighbors.add(dir, block_near.index)
                block_near.neighbors.add(dir.opposite(), block_near.index)
                             
    def remove_neighbors(self, x, y):
        block = self.map[(x, y)]
        for neighbor, dir in neighbors((x, y)):
            if neighbor in self.map:
                block_near = self.map[neighbor]
                block.neighbors.remove(dir, block_near.index)
                block_near.neighbors.remove(dir.opposite(), block_near.index)   
    
    def show(self, x, y):
        if (x, y) in self.invisible:
            self.map[(x, y)] = self.invisible[(x, y)]
            self.set_neighbors(x, y)
            self.invisible.pop((x, y))
        
    def hide(self, x, y):
        if (x, y) in self.map:
            self.invisible[(x, y)] = self.map[(x, y)]
            self.remove_neighbors(x, y)
            self.map.pop((x, y))
            
            
    def shift(self, xoffset, yoffset):
        self.check_render()
        xsplit = self.view_size - xoffset
        ysplit = self.view_size - yoffset
        for image, scale in [(self.image, 1), (self.tile_image, 12), (self.original, 24)]:
            tl = image.crop((0, 0, xsplit*scale, ysplit*scale))
            tr = image.crop((xsplit*scale, 0, self.view_size*scale, ysplit*scale))
            bl = image.crop((0, ysplit*scale, xsplit*scale, self.view_size*scale))
            br = image.crop((xsplit*scale, ysplit*scale, self.view_size*scale, self.view_size*scale))
            image.paste(tl, (xoffset*scale, yoffset*scale))
            image.paste(tr, (0, yoffset*scale))
            image.paste(bl, (xoffset*scale, 0))
            image.paste(br, (0, 0))        
            
    def render(self):
        self.image = Image.new("RGBA", (self.view_size, self.view_size), ImageColor.colormap["white"])
        self.tile_image = Image.new("RGBA", (self.view_size*12, self.view_size*12), ImageColor.colormap["white"])
        self.original = Image.new("RGBA", (self.view_size*24, self.view_size*24), ImageColor.colormap["white"])
        self.px = self.image.load()
        for coord in self.map:
            block = self.map[coord]
    
    def check_render(self):
        if not self.rendered:
            self.render()
            self.rendered = True
        
    def view_px(self):
        self.check_render()
        if self.scale == 1:
            output = self.image
        else:
            output = self.image.resize((self.size*self.scale, self.size*self.scale))
        output.show()
        
    def view_small(self):
        self.check_render()
        if self.scale == 1:
            output = self.tile_image
        else:
            output = self.tile_image.resize((self.size*self.scale, self.size*self.scale))
        output.show()
        
    def view_original(self):
        self.check_render()
        if self.scale == 1:
            output = self.original
        else:
            output = self.original.resize((self.size*self.scale, self.size*self.scale))
        output.show()

## Board Creation and Data Extraction

board = SPBoard(size, scale, border, auto_offset)

data_entries = data.split(b"\x06")

data_extract = [d[1:].split(b",")[:5] for d in data_entries]
data_tiles = [[*d[:4], *d[4].split(b'|')] for d in data_extract if len(d) == 5]

for tile in data_tiles:
    block = Block.from_data(tile)
    x = int(block[1])
    y = int(block[2])
    board.place(x, y, block)     
        
## Data Refining
        
        # TODO: This       
data_mem = [d for d in data_entries if chr(d[1]).isupper() and str(d[1:4], "utf-8") != "SUB"]

visible = set()
gateways = set()
structs = set()
user = set()

for tile in data_tiles:
    coord = (int(tile[1]), int(tile[2]))
    visible.add(coord)
    if int(tile[0]) == 10:
        structs.add(coord)
    elif int(tile[0]) == 11:
        gateways.add(coord)
    else:
        user.add(coord)

## Logical Tile Generators

def perimeter(start, radius):
    for i in range(-radius, radius+1):
        yield (start[0] + radius) % 160, (start[1] + i) % 160
        yield (start[0] - radius) % 160, (start[1] + i) % 160
        yield (start[0] + i) % 160, (start[1] + radius) % 160
        yield (start[0] + i) % 160, (start[1] - radius) % 160

def surround(start, rel):
    for i in range(-2, 3):
        for j in range(-2, 3):
            coord = ((start[0] + i) % 160, (start[1] + j) % 160)
            c_rel = (rel[0]+i, rel[1]+j)
            yield coord, c_rel
            
def neighbors(start):
    for dir in Border:
            yield ((start[0] + dir[0]) % 160, (start[1] + dir[1]) % 160), dir
            

## Post-processing

def find_cell(start):
    first = (start, (0, 0))
    gateway = None
    bounds = [0, 0, 0, 0]
    next = queue()
    search = set()
    structs = set()
    next.put(first)
    while not next.empty():
        for cell in surround(*next.get()):
            if cell not in search:
                search.add(cell)
                if cell[0] in tiles:
                    tile_type = int(tiles[cell[0]][0])
                    if tile_type == 10:
                        structs.add(cell[0])
                        next.put(cell)
                        if (cell[1][0] < bounds[0]):
                            bounds[0] = cell[1][0]
                        if (cell[1][1] < bounds[1]):
                            bounds[1] = cell[1][1]
                        if (cell[1][0] > bounds[2]):
                            bounds[2] = cell[1][0]
                        if (cell[1][1] > bounds[3]):
                            bounds[3] = cell[1][1]
                    if tile_type == 11:
                        gateway = cell[0]
    island_size = (bounds[2] - bounds[0], bounds[3] - bounds[1])
    return structs, gateway, island_size
    
def on_bound(cell):
    for tile in perimeter(cell, 12):
        if tile in user:
            return True
    return False
    
def can_see(tiles):
    for tile in tiles:
        if on_bound(tile):
            return True
    return False
    
"""
unsearched_structs = structs.copy()
found_structs = set()

while len(unsearched_structs) > 0:
    next = unsearched_structs.pop()
    uncheck, gateway, island_size = find_cell(next)
    for struct in uncheck:
        if struct in unsearched_structs:
            unsearched_structs.remove(struct)
    found_structs.add((next, gateway, island_size))
    if not can_see(uncheck):
        for tile in uncheck:
            visible.remove(tile)
            board.remove(*tile)
            board.remove_tile(*tile)
        if gateway:
            visible.remove(gateway)
            board.remove(*gateway)
            board.remove_tile(*gateway)
            

if auto_offset:            
    row_written = [0 for i in range(board.size)]            
    col_written = [0 for i in range(board.size)]
    
    for row in range(board.size):
        for col in range(board.size):
            if (col, row) in visible:
                row_written[row] = 1
                break
    
    for col in range(board.size):
        for row in range(board.size):
            if (col, row) in visible:
                col_written[col] = 1
                break
                
    xoffset = 0
    yoffset = 0
    if len(visible) > 0:
        index = 0
        run_max = 0
        while index < size:
            if col_written[index]:
                index += 1
            else:
                start = index
                run = 0
                while not col_written[index]:
                    run += 1
                    index = (index + 1) % 160
                if run > run_max:
                    run_max = run
                    xoffset = board.size - ((start + run // 2) % board.size)
        index = 0
        run_max = 0
        while index < board.size:
            if row_written[index]:
                index += 1
            else:
                start = index
                run = 0
                while not row_written[index]:
                    run += 1
                    index += 1
                if run > run_max:
                    run_max = run
                    yoffset = board.size - ((start + run // 2) % board.size)

    print(xoffset, yoffset)
    board.shift(xoffset, yoffset)
"""








