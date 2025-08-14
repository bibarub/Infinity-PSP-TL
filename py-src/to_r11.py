#!/usr/bin/env python3

import sys
import struct
from PIL import Image

atlas_width = 512
atlas_tile_size = 32
drawn_tile_size = 30
tile_bleed_compensation = (atlas_tile_size-drawn_tile_size)//2
tiles_per_atlas_row = atlas_width//atlas_tile_size

def flatten(xss):
    return [x for xs in xss for x in xs]

def make_r11(im, out_path, n7_sprite_mode=False):
    width, height = im.size
    paletted = im.mode == "P"
    if paletted:
        im.apply_transparency()
        palette = im.getpalette("RGBA")
    elif im.mode != "RGBA":
        im = im.convert("RGBA")
    if tile_bleed_compensation:
        tempim = im
        im = Image.new("P" if paletted else "RGBA", (im.width+tile_bleed_compensation*2, im.height+tile_bleed_compensation*2))
        #if paletted:
        #    im.putpalette(tempim.getpalette("RGBA"), "RGBA")
        im.paste(tempim, (tile_bleed_compensation, tile_bleed_compensation))
        tempim.close()
        l = im.crop((tile_bleed_compensation, tile_bleed_compensation, tile_bleed_compensation+1, im.height-tile_bleed_compensation))
        r = im.crop((im.width-tile_bleed_compensation-1, tile_bleed_compensation, im.width-tile_bleed_compensation, im.height-tile_bleed_compensation))
        for i in range(tile_bleed_compensation):
            im.paste(l, (i, tile_bleed_compensation))
            im.paste(r, (im.width-tile_bleed_compensation+i, tile_bleed_compensation))
        u = im.crop((0, tile_bleed_compensation, im.width, tile_bleed_compensation+1))
        d = im.crop((0, im.height-tile_bleed_compensation-1, im.width, im.height-tile_bleed_compensation))
        for i in range(tile_bleed_compensation):
            im.paste(u, (0, i))
            im.paste(d, (0, im.height-i-1))
    rows = (height + drawn_tile_size - 1) // drawn_tile_size
    columns = (width + drawn_tile_size - 1) // drawn_tile_size
    total_tiles = rows*columns
    atlas = Image.new("P" if paletted else "RGBA", (atlas_width, (total_tiles + tiles_per_atlas_row - 1)//tiles_per_atlas_row*atlas_tile_size))
    if paletted:
        atlas.putpalette(palette, "RGBA")
    y = tile_bleed_compensation
    index = 0
    for row in range(rows):
        x = tile_bleed_compensation
        for col in range(columns):
            ut, vt = index%tiles_per_atlas_row, index//tiles_per_atlas_row
            u, v = ut*atlas_tile_size, vt*atlas_tile_size
            atlas.paste(im.crop((x-tile_bleed_compensation, y-tile_bleed_compensation, x+drawn_tile_size+tile_bleed_compensation, y+drawn_tile_size+tile_bleed_compensation)), (u, v))
            x += drawn_tile_size
            index += 1
        y += drawn_tile_size

    entry_ptr = 0x80
    palette_ptr = 0x100
    pixels_ptr = (0x100+5*4*256 if n7_sprite_mode else 0x100+1*4*256) if paletted else palette_ptr
    pixels = list(atlas.getdata()) if paletted else flatten(list(atlas.getdata()))
    file_size = pixels_ptr + len(pixels)

    atlas.close()

    f = open(out_path, "wb")
    if n7_sprite_mode:
        f.write(struct.pack("<8I", 10, entry_ptr, entry_ptr+8+1*12, entry_ptr+8+2*12, entry_ptr+8+3*12, entry_ptr+8+4*12, entry_ptr+8+5*12, entry_ptr+8+6*12))
    else:
        f.write(struct.pack("<3I", 5, entry_ptr, entry_ptr+8+1*12))
    f.write(struct.pack("<3I", palette_ptr, pixels_ptr, file_size))
    f.seek(entry_ptr)
    f.write(struct.pack("<6H", 1, paletted, 0, 0, width, height))
    f.write(struct.pack("<2H4B", 2, 0, 0, 0, columns, rows))
    if n7_sprite_mode:
        for i in range(4):
            f.write(struct.pack("<6H", 0, paletted, 0, 0, width, height))
        f.write(b"\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff")
    if paletted:
        palette_bytes = bytes(palette)
        for i in range(5 if n7_sprite_mode else 1):
            f.seek(palette_ptr+i*4*256)
            f.write(palette_bytes)
    f.seek(pixels_ptr)
    f.write(bytes(pixels))
    f.close()

def main():
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("usage: to_r11.py <INPUT> <OUTPUT.R11> [-n7s]")
        return
    n7_sprite_mode = (len(sys.argv) == 4 and sys.argv[3] == "-n7s")
    make_r11(Image.open(sys.argv[1]), sys.argv[2], n7_sprite_mode)

if __name__ == "__main__":
    main()
