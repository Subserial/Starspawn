from PIL import Image, ImageFilter, ImageColor
from queue import SimpleQueue as queue
from enum import Enum
import argparse, random

## Argument Parsing

parser = argparse.ArgumentParser(description="Visualizer for Starseed Pilgrim", usage="%(prog)s [options]")
parser.add_argument("-f", "--file", nargs="?", default="star.save", help="save file location (default: star.save)")
parser.add_argument("-b", "--border", action='store_true', help="Enable 2x tile mode")
parser.add_argument("-s", "--scale", nargs=1, type=float, default=1, help="scale image linearly")

group_hidden = parser.add_mutually_exclusive_group()
group_hidden.add_argument("-r", "--radius", nargs=1, type=int, default=10, help="set island hide radius (default 10)")
group_hidden.add_argument("-v", "--visible", action='store_true', help="reveal all tiles")

group_offset = parser.add_mutually_exclusive_group()
group_offset.add_argument('-o', '--offset', nargs=2, type=int, action='store', default=[0, 0], metavar = ("X", "Y"), help="manually offset image")
parser.add_argument("-a", "--auto", action="store_true", help="automatically offset image based on unoccupied rows or columns")

group_tile = parser.add_mutually_exclusive_group()
group_tile.add_argument("-t", "--tile", action='store_true', help='use 12x12 tileset (EXPERIMENTAL)')
group_tile.add_argument("-p", "--pixel", action='store_true', help='use pixel tileset')

## Initial File Imports

sheet_small = Image.open("SPsmall.png")    
sheet_large = Image.open("SP.png")

empty_small = Image.new("RGBA", (12, 12), ImageColor.colormap["white"])
empty_large = Image.new("RGBA", (24, 24), ImageColor.colormap["white"])

def tileAt(x, y):
    small = sheet_small.crop((x*12, y*12, (x+1)*12, (y+1)*12))
    large = sheet_large.crop((x*24, y*24, (x+1)*24, (y+1)*24))
    return large, small
    
def translucent(image):
    result = image.copy()
    result.putalpha(128)
    return result

## Logical Tile Generators

def perimeter(start, radius, mod):
    for i in range(-radius, radius+1):
        yield (start[0] + radius) % mod, (start[1] + i) % mod
        yield (start[0] - radius) % mod, (start[1] + i) % mod
        yield (start[0] + i) % mod, (start[1] + radius) % mod
        yield (start[0] + i) % mod, (start[1] - radius) % mod

def surround(start, rel, mod):
    for i in range(-2, 3):
        for j in range(-2, 3):
            coord = ((start[0] + i) % mod, (start[1] + j) % mod)
            c_rel = (rel[0]+i, rel[1]+j)
            yield coord, c_rel
            
def neighbors(start, mod):
    for dir in Border:
            yield ((start[0] + dir.value[0]) % mod, (start[1] + dir.value[1]) % mod), dir

## Tile Definitions

class Border(Enum):
    TOP = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    BOTTOM = (0, 1)
    
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
                x = 1
            else:
                x = 2
        else:
            if Border.RIGHT in neighbor_set:
                x = 0
            else:
                x = 3
        if Border.TOP in neighbor_set:
            if Border.BOTTOM in neighbor_set:
                y = 1
            else:
                y = 2
        else:
            if Border.BOTTOM in neighbor_set:
                y = 0
            else:
                y = 3
        return x, y

class Block():
    all_blocks = dict()
    tiles = (tileAt(0, 0),)
    colors = ((158, 87, 21),)
    index = 4
    def __init__(self, offset, modifier):
        self.tile = self.tiles[0]
        self.color = self.colors[0]
            
    def get_tile(self, small=False):
        if small:
            return self.tile[1]
        else:
            return self.tile[0]
            
    def get_color(self):
        return self.color
        
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
            return self.sheet_small.crop((x*12, y*12, (x+1)*12, (y+1)*12))
        else:
            return self.sheet.crop((x*24, y*24, (x+1)*24, (y+1)*24))
        
    def add_neighbor(self, pos, index):
        self.neighbors.add(pos)
        
    def remove_neighbor(self, pos, index):
        self.neighbors.remove(pos)
        
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
        super().__init__(offset, modifier)
        if offset == 2:
            self.tile = self.tiles[0]
        else:
            self.tile = self.tiles[1]
    
class BlockLove(Block):
    # pink (love)
    tiles = (tileAt(0, 1), tileAt(1, 1), tileAt(2, 1), tileAt(3, 1))
    colors = ((255, 85, 205),)
    index = 7
    
    def __init__(self, offset, modifier):
        self.tile = random.choice(self.tiles)
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
        
    def add_neighbor(self, pos, index):
        if index == BlockRock.index:
            self.neighbors.add(pos)
        
    def remove_neighbor(self, pos, index):
        if index == BlockRock.index:
            self.neighbors.remove(pos)
    
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
        self.sheet, self.sheet_small = random.choice(self.sheets)
    
    
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
        self.tile = random.choice(self.tiles)

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
            
## SPBoard Class

class SPBoard():
    def __init__(self, size, scale=1, border=False, auto_offset=False, offset=(0, 0), visible=-1):
        self.view_size = size * (2 if border else 1)
        self.size = size
        self.scale = scale
        self.border = border
        self.auto_offset = auto_offset
        self.offset = offset
        self.visible = visible
        self.rendered = False
        self.map = dict()
        self.hidden = dict()
        self.gateways = set()
        self.structs = set()
        self.user = set()
        
    def place(self, x, y, block):
        x = x % self.view_size
        y = y % self.view_size
        self.map[(x, y)] = block
        self.set_neighbors(x, y)
        self.add_to_sort(x, y, block.index)
            
    def set_neighbors(self, x, y):
        block = self.map[(x, y)]
        for neighbor, dir in neighbors((x, y), self.size):
            if neighbor in self.map:
                block_near = self.map[neighbor]
                block.add_neighbor(dir, block_near.index)
                block_near.add_neighbor(dir.opposite(), block.index)
                             
    def remove_neighbors(self, x, y):
        block = self.map[(x, y)]
        for neighbor, dir in neighbors((x, y), self.size):
            if neighbor in self.map:
                block_near = self.map[neighbor]
                block.remove_neighbor(dir, block_near.index)
                block_near.remove_neighbor(dir.opposite(), block.index)   
    
    def show(self, x, y):
        if (x, y) in self.hidden:
            block = self.hidden[(x, y)]
            self.map[(x, y)] = self.hidden[(x, y)]
            self.set_neighbors(x, y)
            self.hidden.pop((x, y))
            self.add_to_sort(x, y, block.index)
            
    def add_to_sort(self, x, y, index):
        if index == BlockPortal.index:
            self.gateways.add((x, y))
        elif index == BlockRock.index:
            self.structs.add((x, y))
        elif index != BlockDirt.index:
            self.user.add((x, y))
        
    def hide(self, x, y):
        if (x, y) in self.map:
            block = self.map[(x, y)]
            self.hidden[(x, y)] = block
            self.remove_neighbors(x, y)
            self.map.pop((x, y))
            self.remove_from_sort(x, y, block.index)
            
    def remove_from_sort(self, x, y, index):
        if index == BlockPortal.index:
            self.gateways.remove((x, y))
        elif index == BlockRock.index:
            self.structs.remove((x, y))
        elif index != BlockDirt.index:
            self.user.remove((x, y))
            
    def set_all_visible(self):
        for coord in self.hidden:
            self.show(*coord)
            
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
        if self.visible > 0:
            self.mark_unseen(self.visible)
        self.image = Image.new("RGBA", (self.view_size, self.view_size), ImageColor.colormap["white"])
        self.tile_image = Image.new("RGBA", (self.view_size*12, self.view_size*12), ImageColor.colormap["white"])
        self.original = Image.new("RGBA", (self.view_size*24, self.view_size*24), ImageColor.colormap["white"])
        self.px = self.image.load()
        if self.auto_offset:
            offset = self.find_offset()
        else:
            offset = self.offset
        for x, y in self.map:
            block = self.map[x, y]
            if self.border:
                coords = [((x - self.size // 2) % self.view_size, (y - self.size // 2) % self.view_size),
                          ((x - self.size // 2) % self.view_size, (y + self.size // 2) % self.view_size),
                          ((x + self.size // 2) % self.view_size, (y - self.size // 2) % self.view_size),
                          ((x + self.size // 2) % self.view_size, (y + self.size // 2) % self.view_size)]
            else:
                coords = [(x, y)]
            for cx, cy in coords:
                self.px[cx, cy] = block.get_color()
                self.tile_image.paste(block.get_tile(small=True), (cx*12, cy*12))
                self.original.paste(block.get_tile(small=False), (cx*24, cy*24))
        self.rendered = True
        self.shift(*offset)
    
    def check_render(self):
        if not self.rendered:
            self.render()
        
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
        
    def can_see(self, tiles, range):
        for given_tile in tiles:
            for tile in perimeter(given_tile, range, self.size):
                if tile in self.user:
                    return True
        return False
        
    def find_island(self, x, y):
        if (x, y) not in self.map:
            return None, None, None
        first = ((x, y), (0, 0))
        gateway = None
        bounds = [0, 0, 0, 0]
        next = queue()
        search = set()
        islands = set()
        next.put(first)
        while not next.empty():
            for cell in surround(*next.get(), self.size):
                if cell not in search:
                    search.add(cell)
                    coord, rel = cell
                    # TODO: FIX (edit: thanks, me)
                    if coord in self.structs:
                        islands.add(coord)
                        next.put(cell)
                        if (rel[0] < bounds[0]):
                            bounds[0] = rel[0]
                        if (rel[1] < bounds[1]):
                            bounds[1] = rel[1]
                        if (rel[0] > bounds[2]):
                            bounds[2] = rel[0]
                        if (rel[1] > bounds[3]):
                            bounds[3] = rel[1]
                    if coord in self.gateways:
                        gateway = coord
        island_size = (bounds[2] - bounds[0], bounds[3] - bounds[1])
        return islands, gateway, island_size

    def mark_unseen(self, range):
        # TODO: Split into find_islands and is_hidden
        self.set_all_visible()
        unsearched = self.structs.copy()
        found = set()

        while len(unsearched) > 0:
            next = unsearched.pop()
            uncheck, gateway, island_size = self.find_island(*next)
            for struct in uncheck:
                if struct in unsearched:
                    unsearched.remove(struct)
            found.add((next, gateway, island_size))
            if not self.can_see(uncheck, range):
                for tile in uncheck:
                    self.hide(*tile)
                if gateway:
                    self.hide(*gateway)
            
    def find_offset(self):          
        row_written = [0 for i in range(board.size)]            
        col_written = [0 for i in range(board.size)]
        
        for row in range(board.size):
            for col in range(board.size):
                if (col, row) in self.map:
                    row_written[row] = 1
                    break
        
        for col in range(board.size):
            for row in range(board.size):
                if (col, row) in self.map:
                    col_written[col] = 1
                    break
                    
        xoffset = 0
        yoffset = 0
        if len(self.map) > 0:
            index = 0
            run_max = 0
            while index < self.size:
                if col_written[index]:
                    index += 1
                else:
                    start = index
                    run = 0
                    while not col_written[index]:
                        run += 1
                        index = (index + 1) % self.size
                    if run > run_max:
                        run_max = run
                        xoffset = self.size - ((start + run // 2) % self.size)
            index = 0
            run_max = 0
            while index < self.size:
                if row_written[index]:
                    index += 1
                else:
                    start = index
                    run = 0
                    while not row_written[index]:
                        run += 1
                        index = (index + 1) % self.size
                    if run > run_max:
                        run_max = run
                        yoffset = self.size - ((start + run // 2) % self.size)
    
        return xoffset, yoffset

## Main Entrypoint

def main():    
    global board # Debugging global
    args = parser.parse_args()
    
    size = 160
    file = args.file
    scale = args.scale
    if args.auto:
        auto_offset = True
        offset = (0, 0)
    else:
        auto_offset = False
        offset = args.offset
    border = args.border
    if args.visible:
        visible = -1
    else:
        visible = args.radius
    use_tile = args.tile
    use_pixel = args.pixel

    with open(file, "rb") as save:
        data = save.readline()
    
    board = SPBoard(size, scale=scale, border=border, auto_offset=auto_offset, offset=offset, visible=visible) 

    data_entries = data.split(b"\x06")
    
    data_extract = [d[1:].split(b",")[:5] for d in data_entries]
    data_tiles = [[*d[:4], *d[4].split(b'|')] for d in data_extract if len(d) == 5]
    data_mem = [d for d in data_entries if chr(d[1]).isupper() and str(d[1:4], "utf-8") != "SUB"]
    
    for tile in data_tiles:
        block = Block.from_data(tile)
        x = int(tile[1])
        y = int(tile[2])
        board.place(x, y, block) 
        
    if use_pixel:
        board.view_px()
    elif use_tile:
        board.view_small()
    else:
        board.view_original()

if __name__ == "__main__":
    board = None
    main()




