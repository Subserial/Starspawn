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

class Block():
    tiles = (tileAt(0, 0),)
    colors = ((158, 87, 21),)
    index = 4
    def __init__(self, data):
        self.tile = self.tiles[0]
        self.color = self.colors[0]
        
    def get_sprite(self, small=False):
        if small:
            return self.tile[1]
        else:
            return self.tile[0]
            
    def get_tile(self, neighbors, small=False):
        return self.get_sprite(small)
        
    def add_neighbor(self, pos):
        pass
        
    def remove_neighbor(self, pos):
        pass
        
    def clear_neighbors(self):
        pass
        
        
class BlockBordered(Block):
    light_color = (203, 109, 17)
    dark_color = (125, 66, 9)
    generated = False
    sheets = []
    def __init__(self, data):
        super().__init__(data)
        self.neighbors = set()
        if not type(self).generated:
            self.sheets.append(self.generate_borders(self.tile))
            type(self).generated = True
        
    def add_neighbor(self, pos):
        self.neighbors.add(pos)
        
    def remove_neighbor(self, pos):
        self.neighbors.remove(pos)
        
    def clear_neighbors(self):
        self.neighbors.clear()
        
    def generate_borders(self, tile):
        sheet = Image.new("RGBA", (144, 72), ImageColor.colormap["white"])
        sheet_small = Image.new("RGBA", (72, 36), ImageColor.colormap["white"])
        px = sheet.load()
        px_small = sheet_small.load()
        for i in range(3):
            sheet.paste(tile[0], (72+i*24, 24))
            sheet.paste(tile[0], (96, i*24))
            sheet_small.paste(tile[1], (36+i*12, 12))
            sheet_small.paste(tile[1], (48, i*12))
            for j in range(3):
                sheet.paste(tile[0], (i*24, j*24))
                sheet_small.paste(tile[1], (i*12, j*12))
        
        edge_set = set((0, 23, 24, 47, 48, 71)) 
        for i in range(72):
            # top
            px[71-i, 0] = self.light_color
            px[143-i, 24] = self.light_color
            # right
            px[71, 71-i] = self.light_color
            px[119, 71-i] = self.light_color
            # bottom
            px[i, 71] = self.dark_color
            px[i+72, 47] = self.dark_color
            # left
            px[0, i] = self.dark_color
            px[96, i] = self.dark_color                        
            
            if i not in edge_set and i >= 24 and i <= 47:
                # top
                px[71-i, 1] = self.light_color
                px[143-i, 25] = self.light_color
                # right
                px[70, 71-i] = self.light_color
                px[118, 71-i] = self.light_color
                # bottom
                px[i, 70] = self.dark_color
                px[i+72, 46] = self.dark_color
                # left
                px[1, i] = self.dark_color
                px[97, i] = self.dark_color
                
                # top
                px[143-i, 1] = self.light_color
                px[143-i, 0] = self.light_color
                # right
                px[142, 71-i] = self.light_color
                px[143, 71-i] = self.light_color
                # bottom
                px[i+72, 70] = self.dark_color
                px[i+72, 71] = self.dark_color
                # left
                px[73, i] = self.dark_color
                px[72, i] = self.dark_color
                
            elif i not in edge_set:
                # top
                px[71-i, 1] = self.light_color
                px[143-i, 25] = self.light_color
                # right
                px[70, 71-i] = self.light_color
                px[118, 71-i] = self.light_color
                # bottom
                px[i, 70] = self.dark_color
                px[i+72, 46] = self.dark_color
                # left
                px[1, i] = self.dark_color
                px[97, i] = self.dark_color
                
            elif i >= 24 and i <= 47:
                # top
                px[143-i, 0] = self.light_color
                # right
                px[143, 71-i] = self.light_color
                # bottom
                px[i+72, 71] = self.dark_color
                # left
                px[72, i] = self.dark_color
                
                       
                    
        
        for i in range(36):
            # top
            px_small[35-i, 0] = self.light_color
            px_small[71-i, 12] = self.light_color
            # right
            px_small[35, 35-i] = self.light_color
            px_small[59, 35-i] = self.light_color
            # bottom
            px_small[i, 35] = self.dark_color
            px_small[i+36, 23] = self.dark_color
            # left
            px_small[0, i] = self.dark_color
            px_small[48, i] = self.dark_color
            
            if i >= 1 and i <= 34:
                # top
                px_small[71-i, 11] = self.light_color
                px_small[35-i, 1] = self.light_color
                # right
                px_small[58, 35-i] = self.light_color
                px_small[34, 35-i] = self.light_color
                # bottom
                px_small[i+36, 22] = self.dark_color
                px_small[i, 34] = self.dark_color
                # left
                px_small[47, i] = self.dark_color
                px_small[1, i] = self.dark_color
            
                if i >= 12 and i <= 23:
                    # top
                    px_small[71-i, 0] = self.light_color
                    px_small[71-i, 11] = self.light_color
                    # right
                    px_small[71, 35-i] = self.light_color
                    px_small[58, 35-i] = self.light_color
                    # bottom
                    px_small[i+36, 35] = self.dark_color
                    px_small[i+36, 22] = self.dark_color
                    # left
                    px_small[47, i] = self.dark_color
                    px_small[36, i] = self.dark_color
                
            
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
    
    def __init__(self, data):
        tile = random.randint(0, 3)
        self.tile = self.tiles[tile]
        self.color = colors[tile // 2]
    
class BlockFury(Block):
    # orange (arrow)
    tiles = (tileAt(0, 2), tileAt(1, 2), tileAt(2, 2), tileAt(3, 2), )
    colors = ((255, 168, 0),)
    index = 5
              
    def __init__(self, data):
        # TODO: Verify modifier
        if data.modifier == 0:
            self.tile = self.tiles[3]
        else:
            if data.offset == 2:
                self.tile = self.tiles[0]
            elif data.offset == 0:
                self.tile = self.tiles[1]
            else:
                self.tile = self.tiles[2]
    
    
class BlockHate(Block):
    # red (mine)
    tiles = (tileAt(6, 1), tileAt(7, 3))
    colors = ((237, 0, 0),)
    index = 6           
    
    def __init__(self, data):
        # TODO: Correct offset
        if data.offset == 1:
            self.tile = self.tiles[0]
        else:
            self.tile = self.tiles[1]
        self.color = self.colors[0]
    
    
class BlockLove(Block):
    # pink (love)
    tiles = (tileAt(0, 1), tileAt(1, 1), tileAt(2, 1), tileAt(3, 1))
    colors = ((255, 85, 205),)
    index = 7
    
    def __init__(self, data):
        self.tile = self.tiles[random.randint(0, 3)]
        self.color = self.colors[0]
    
    
class BlockPortal(Block):
    # portal
    tiles = (tileAt(4, 3), tileAt(5, 3))
    colors = ((109, 129, 144), (255, 254, 199))
    index = 11
    
    def __init__(self, data):
        # TODO: Correct offset
        if data.offset == 1:
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
              
    def get_tile(self, neighbors, small=False):
        # TODO: Border
        return self.get_sprite(small)
    
    
class BlockVine(BlockBordered):
    # green (garden)
    tiles = (tileAt(1, 3),)
    colors = ((148, 232, 16),)
    index = 8  
    light_color = (196, 254, 37)
    dark_color = (119, 216, 3)
    sheets = []
    def __init__(self, data):
        if BlockVine.generated == False:
            for i in range(8):
                rotate = (i % 4) * 90
                flip = i // 4
                tile = list(self.tiles[0])
                if flip:
                    tile[0] = tile[0].transpose(Image.FLIP_LEFT_RIGHT)
                    tile[1] = tile[1].transpose(Image.FLIP_LEFT_RIGHT)
                tile[0] = tile[0].rotate(rotate)
                tile[1] = tile[1].rotate(rotate)
                self.sheets.append(self.generate_borders(tile))
        super().__init__(data) 
        self.sheet, self.sheet_small = self.sheets[random.randint(0, 7)]
        self.color = self.colors[0]
                
    def get_tile(self, neighbors, small=False):
        # TODO: Border
        return self.get_sprite(small)
    
    
class BlockVoid(Block):
    # void
    pass
    
class BlockWill(Block):
    # purple (pylon)
    tiles = (tileAt(4, 1), tileAt(5, 1))
    colors = ((153, 98, 223),)
    index = 9
    
class Block2Calm(Block):
    # Calm 2: Die Calmer
    tiles = (tileAt(0, 3),)
    colors = ((163, 237, 255),)
    index = 22

## SP Block Dictionaries

blocks = dict()
blocks[BlockAct.index] = BlockAct
blocks[BlockBalk.index] = BlockBalk
blocks[BlockCalm.index] = BlockCalm
blocks[BlockDeath.index] = BlockDeath
blocks[BlockDirt.index] = BlockDirt
blocks[BlockFury.index] = BlockFury
blocks[BlockHate.index] = BlockHate
blocks[BlockLove.index] = BlockLove
blocks[BlockPortal.index] = BlockPortal
blocks[BlockRock.index] = BlockRock
blocks[BlockVine.index] = BlockVine
blocks[BlockWill.index] = BlockWill
blocks[Block2Calm.index] = Block2Calm



"""
class Tile():
    self.__init__(self, name, index, color, sprites):
      """  

tiles = dict()
name = dict()
color = dict()
sprites_small = dict()
sprites_large = dict()

def register_tile(tile, index, value, regions):
    name[index] = tile
    color[index] = value  
    types_small = dict()
    types_large = dict()
    for region in regions:
        bounds_small = (region[0]*12, region[1]*12, (region[0]+1)*12, (region[1]+1)*12)
        bounds_large = (region[0]*24, region[1]*24, (region[0]+1)*24, (region[1]+1)*24)
        tile_small = sheet_small.crop(bounds_small)
        tile_large = sheet_large.crop(bounds_large)
        types_small[region[2]] = tile_small
        types_large[region[2]] = tile_large
    sprites_small[index] = types_small
    sprites_large[index] = types_large

register_tile("boost",     0,  (0,   138, 255), ((6, 2, 0),))       
register_tile("anchor",    1,  (173, 173, 25),  ((4, 2, 0), (5, 2, 1)))    
register_tile("ice",       2,  (163, 237, 255), ((0, 3, 0),))    
register_tile("grass",     3,  (115, 212, 0),   ((0, 0, 0), (1, 0, 1), (2, 0, 2), (3, 0, 3)))
register_tile("dirt",      4,  (125, 66,  9),   ((4, 0, 0), (5, 0, 1), (6, 0, 2), (7, 0, 3)))   
register_tile("arrow",     5,  (255, 168, 0),   ((0, 2, 2), (1, 2, 4), (2, 2, 0), (3, 2, 3), (3, 3, 1)))
register_tile("mine",      6,  (224, 52,  52),  ((6, 1, 0), (7, 1, 1), (7, 3, 2)))
register_tile("love",      7,  (255, 85,  205), ((0, 1, 0), (1, 1, 1), (2, 1, 2), (3, 1, 3)))
register_tile("garden",    8,  (148, 232, 16),  ((1, 3, 0),))
register_tile("pylon",     9,  (153, 98,  223), ((4, 1, 0), (5, 1, 1)))
register_tile("structure", 10, (109, 129, 144), ((7, 2, 0),))
register_tile("gateway",   11, (139, 164, 182), ((4, 3, 0), (5, 3, 1)))


            
## SPBoard Class and Functions

class SPBoard():
    def __init__(self, size, scale, border, auto_offset):
        self.view_size = size * (2 if border else 1)
        self.px = self.image.load()
        self.size = size
        self.scale = scale
        self.border = border
        self.auto_offset = auto_offset
        self.xoffset = 0
        self.yoffset = 0
        self.rendered = False
        self.map = dict()
        self.invisible = dict()
        
    def place(self, x, y, block_type, data):
        x = x % self.view_size
        y = y % self.view_size
        x_draw = (x + self.xoffset) % self.view_size
        y_draw = (y + self.yoffset) % self.view_size
        block = block_type(data)
        self.map[(x, y)] = block
        self.set_neighbors(x, y)
            
    def set_neighbors(self, x, y):
        block = self.map[(x, y)]
        for neighbor, dir in neighbors((x, y)):
            if neighbor in self.map:
                block_near = self.map[neighbor]
                if block.index == block_near.index:
                    block.neighbors.add(dir)
                    block_near.neighbors.add(dir.opposite())
                             
    def remove_neighbors(self, x, y):
        block = self.map[(x, y)]
        for neighbor, dir in neighbors((x, y)):
            if neighbor in self.map:
                block_near = self.map[neighbor]
                if block.index == block_near.index:
                    block.neighbors.remove(dir)
                    block_near.neighbors.remove(dir.opposite())   
    
    def show(self, x, y):
        if (x, y) in self.invisible:
            self.map[(x, y)] = self.invisible[(x, y)]
            self.invisible.pop((x, y))
            self.set_neighbors(x, y)
        
    def hide(self, x, y):
        if (x, y) in self.map:
            self.invisible[(x, y)] = self.map[(x, y)]
            self.map.pop((x, y))
            self.remove_neighbors(x, y)
            
            
    def shift(self, xoffset, yoffset):
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
"""
## Board Creation and Data Extraction

board = SPBoard(size, scale, border, auto_offset)

data_entries = data.split(b"\x06")
entries = data.split(b"\x06\x17")

data_extract = [d[1:17].split(b",")[:5] for d in data_entries]
data_tiles = [d for d in data_extract if len(d) == 5]

for block in data_tiles:
    tile = int(block[0])
    x = int(block[1])
    y = int(block[2])
    offset = int(block[3])
    modifier = int(block[4].split(b'|')[0])
    tiles[(x, y)] = block
    if tile in color:
        board.place(x, y, color[tile])
        board.place_tile(x, y, tile, offset, modifier)
    else:
        board.place(x, y, (0,0,0)) 
        
## Data Refining
               
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
"""
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








