#!/usr/bin/env python3

# my very own R11/BIP image unpacker

import os
import struct
import sys
from PIL import Image

ps2 = False
ps2_alt_tile_size = False
android = False

atlas_width = 512
if ps2:
    atlas_tile_size = 16
    if ps2_alt_tile_size: # apparently used in ps2 r11
        drawn_tile_size = 14
    else:
        drawn_tile_size = 16 # definitely used in ps2 e17
else: # infinity psp and android
    atlas_tile_size = 32
    drawn_tile_size = 30
tile_bleed_compensation = (atlas_tile_size-drawn_tile_size)//2
tiles_per_atlas_row = atlas_width // atlas_tile_size

def unpack_r11(r11_file):
    images = []
    data = r11_file.read()

    header_int_count = struct.unpack("<I", data[:4])[0] # apparently the file size is not part of that?
    if header_int_count != 5 and header_int_count != 10: # never encountered any other values
        print("non-standard header_int_count", header_int_count)
    palette_ptr, pixels_ptr, file_size = struct.unpack("<3I", data[header_int_count*4-2*4:header_int_count*4+4])
    # note: sprites have the palette repeated a few times, but it seems like only the first palette is used for everything (incl. lip flaps)
    if len(data) != file_size:
        print("file_size incorrect")

    entries_count = header_int_count - 3 - 2 if header_int_count == 10 else header_int_count - 3 - 1 # guessed
    entry_ptrs = struct.unpack("<"+str(entries_count)+"I", data[4:4+entries_count*4])

    for i, entry_ptr in enumerate(entry_ptrs):
        if entry_ptr == palette_ptr: continue
        draw_count, paletted, unk1, unk2, width, height = struct.unpack("<6H", data[entry_ptr:entry_ptr+6*2])
        if android: # on android, even though "paletted" is set to "1", the atlas is not actually paletted
            paletted = False
        if not draw_count:
            #print("draw_count zero!")
            continue
        if unk1:
            print("non-zero unk1!", unk1)
            continue
        if unk2:
            print("non-zero unk2!", unk2)
            continue

        if i == 0:
            if ps2: # ps2 alpha is 0-128. let's make it 0-255
                data = bytearray(data)
                if paletted:
                    alter_start, alter_end = palette_ptr, palette_ptr + 4*256
                else:
                    alter_start, alter_end = pixels_ptr, len(data)
                for i in range(alter_start, alter_end, 4):
                    a = data[i+3]
                    data[i+3] = a*2 if a != 128 else 255
            atlas_height = (len(data)-pixels_ptr) // atlas_width // (1 if paletted else 4)
            if paletted:
                atlas = Image.new("P", (atlas_width, atlas_height))
                #atlas.putpalette(data[palette_ptr:palette_ptr+4*256], "RGBA")
                atlas.putdata(data[pixels_ptr:])
            else:
                atlas = Image.frombytes("RGBA", (atlas_width, atlas_height), data[pixels_ptr:])

        im = Image.new("P" if paletted else "RGBA", (width, height))
        if paletted:
            im.putpalette(data[palette_ptr:palette_ptr+4*256], "RGBA")
        draw_ptr = entry_ptr + 6*2
        for _ in range(draw_count):
            step, tile_index, x_offset_tiles, y_offset_tiles, columns, rows = struct.unpack("<2H4B", data[draw_ptr:draw_ptr+8])
            step *= 4
            if step != 8:
                raise Exception("step != 8. is "+str(step))
            x, y = x_offset_tiles * drawn_tile_size, y_offset_tiles * drawn_tile_size
            yy = y
            index = tile_index
            for row in range(rows):
                xx = x
                for col in range(columns):
                    ut, vt = index%tiles_per_atlas_row, index//tiles_per_atlas_row
                    u, v = ut*atlas_tile_size+tile_bleed_compensation, vt*atlas_tile_size+tile_bleed_compensation
                    im.paste(atlas.crop((u, v, u+drawn_tile_size, v+drawn_tile_size)), (xx, yy))
                    xx += drawn_tile_size
                    index += 1
                yy += drawn_tile_size
            draw_ptr += step # this is how the psp game uses the "step" value
        images.append(im)
    atlas.close()
    return images

def main():
    if len(sys.argv) != 2:
        print("usage: r11_to_png.py <INPUT.R11>")
        return
    outpathbase = os.path.splitext(sys.argv[1])[0]
    f = open(sys.argv[1], "rb")
    images = unpack_r11(f)
    f.close()
    if not images:
        print("no images unpacked.")
        return
    for i, im in enumerate(images):
        outpath = outpathbase + ("_"+str(i) if i!=0 else "") + ".PNG"
        im.save(outpath)
        im.close()

if __name__ == "__main__":
    main()
