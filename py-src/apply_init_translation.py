#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import re
import struct

import r11
import r11.tipsparser

import os
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "text")))
import jukebox

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("translation")
    parser.add_argument("init_input")
    parser.add_argument("init_output")
    parser.add_argument("-g", "--game", default="e17")
    parser.add_argument("-l", "--lang", default="en")
    parser.add_argument("-t", "--tips")
    parser.add_argument("-c", "--chronology")
    args = parser.parse_args(sys.argv[1:])

    if args.game == "r11":
        #tip_amount = 110
        tip_pages_amount = 10
        seg_text = (0xba68, 0x2c11a)
        # seg_table = [0x1140, 0xac98]
        #seg_table_tips = [0x7610, 0x7f7c]
    elif args.game == "n7":
        #tip_amount = 112
        tip_pages_amount = 9
        seg_text = (0xaf80, 0x2254f)
        # seg_table = [0x1ba8, 0x9904]
        #seg_table_tips = [0x7fbc, 0x880c]
    elif args.game == "e17":
        #tip_amount = 119
        tip_pages_amount = 9
        seg_text = (0x89b0, 0x1f709)
        # seg_table = [0xeb8, 0x7df8]
        #seg_table_tips = [0x65c4, 0x6ee8]
    else:
        sys.exit("game not supported.")

    txt_lines = r11.readlines_utf8_crop_crlf(args.translation)
    with open(args.init_input, "rb") as f_bin:
        init_bytes = bytearray(f_bin.read())

    head = init_bytes[:seg_text[0]]
    mv = memoryview(head)
    head_int_view = mv.cast("I")
    body = bytearray()

    i = head_int_view[0x60//4]
    while (head_int_view[i//4] != 0):
        i += 4
    seg_table_lyric_ptrs = (head_int_view[0x60//4], i)
    i = head_int_view[seg_table_lyric_ptrs[1]//4-1]
    while (head_int_view[i//4] != 0):
        i += 8
    seg_table_lyrics = (head_int_view[seg_table_lyric_ptrs[0]//4], i+4)
    song_amount = (seg_table_lyric_ptrs[1]-seg_table_lyric_ptrs[0])//4

    seg_table_tip_ptrs = (head_int_view[0x64//4], head_int_view[0x68//4]-8)
    tip_amount = (seg_table_tip_ptrs[1]-seg_table_tip_ptrs[0])//12
    seg_table_tips = (head_int_view[seg_table_tip_ptrs[0]//4], head_int_view[seg_table_tip_ptrs[1]//4-2]+4)
    
    seg_table_tip_page_ptrs = (head_int_view[0x68//4], head_int_view[0x68//4]+tip_pages_amount*8)
    seg_table_tip_pages = (head_int_view[seg_table_tip_page_ptrs[0]//4+1], seg_table_tips[0])

    seg_table_chrono = (head_int_view[0x88//4], head_int_view[0x8c//4])

    songs = jukebox.jukebox(args.game, args.lang)
    if songs:
        if len(songs) != song_amount:
            raise Exception(song_amount, "songs expected, got", len(songs))
        lyric_amount = sum(len(song) for song in songs)
        lyric_offset = lyric_amount*8+song_amount*4+seg_table_lyrics[0]-seg_table_lyrics[1]
    else:
        lyric_offset = 0

    tips_txt = args.tips
    if tips_txt:
        tips = r11.tipsparser.parse_tip_file(tips_txt)
        new_tip_amount = sum(1 for tip in tips if getattr(tip.title, args.lang) or getattr(tip.title, "jp"))
        page_amount = sum(len(getattr(tip.pages, args.lang) or tip.pages.jp) for tip in tips)
        tip_offset = page_amount*4+new_tip_amount*12+seg_table_tips[0]-seg_table_tips[1]
        tip_ptr_offset = (new_tip_amount-tip_amount)*12
        new_tip_pages_amount = tip_pages_amount+1 if new_tip_amount != tip_amount and tip_pages_amount != 10 else tip_pages_amount
        tip_page_offset = seg_table_tip_pages[0]-seg_table_tip_pages[1]+((new_tip_amount+new_tip_pages_amount)*2+3)&~3
        tip_page_ptrs_offset = (new_tip_pages_amount-tip_pages_amount)*8
    else:
        tip_offset = 0
        tip_ptr_offset = 0
        tip_page_offset = 0
        tip_page_ptrs_offset = 0
        new_tip_pages_amount = tip_pages_amount

    chrono_txt = args.chronology
    if chrono_txt:
        with open(chrono_txt, "r", encoding="utf-8-sig") as f:
            chronology_lines = [l.rstrip("\n") for l in f.readlines() if not l.startswith("#")]
        chrono_count = sum(map(lambda x: len(x) != 2 or x[-1] != ':' or x[0] not in "01234", chronology_lines))
        chrono_offset = chrono_count*8+4-seg_table_chrono[1]+seg_table_chrono[0]
    else:
        chrono_offset = 0

    pos = seg_text[0]

    offset = lyric_offset+tip_ptr_offset+tip_offset+chrono_offset+tip_page_offset+tip_page_ptrs_offset
    if offset:
        pos += offset
        for i in range(head_int_view[0x8c//4]//4, head_int_view[head_int_view[0x8c//4]//4]//4-1, 1):
            head_int_view[i] += offset
        for i in range(head_int_view[0xa0//4]//4, head_int_view[head_int_view[0xa0//4]//4]//4, 1):
            head_int_view[i] += offset
        for i in (0x8c, 0xa0):
            head_int_view[i//4] += offset
        if lyric_offset:
            for i in range(seg_table_tip_ptrs[0]//4, seg_table_tip_ptrs[1]//4, 3):
                head_int_view[i] += lyric_offset
                head_int_view[i+1] += lyric_offset
            for i in (0x64, 0x78):
                head_int_view[i//4] += lyric_offset
        if lyric_offset or tip_ptr_offset:
            for i in range(head_int_view[0x68//4]//4, head_int_view[head_int_view[0x68//4]//4+1]//4-2, 2):
                head_int_view[i+1] += lyric_offset+tip_ptr_offset
            head_int_view[0x68//4] += lyric_offset+tip_ptr_offset
        if lyric_offset or tip_offset or tip_ptr_offset:
            for i in (0x7c, 0x6c, 0x80, 0x84, 0x88):
                head_int_view[i//4] += lyric_offset+tip_ptr_offset+tip_offset+tip_page_offset+tip_page_ptrs_offset
        seg_table_tip_ptrs = tuple(x+lyric_offset for x in seg_table_tip_ptrs)
        seg_table_tips = tuple(x+lyric_offset+tip_ptr_offset for x in seg_table_tips)
        seg_table_tip_page_ptrs = tuple(x+lyric_offset+tip_ptr_offset for x in seg_table_tip_page_ptrs)
        seg_table_tip_pages = tuple(x+lyric_offset+tip_ptr_offset+tip_page_ptrs_offset for x in seg_table_tip_pages)
        seg_table_chrono = tuple(x+lyric_offset+tip_offset+tip_ptr_offset+tip_page_offset+tip_page_ptrs_offset for x in seg_table_chrono)

    if songs:
        lyric_ptrs = bytearray()
        song_ptr_off = seg_table_lyrics[0]
        song_i = seg_table_lyric_ptrs[0]//4
        for song in songs:
            head_int_view[song_i] = song_ptr_off
            for lyric in song:
                lyric_bytes = r11.str_to_r11_bytes(r11.clean_translation_line(lyric[1], args.lang, args.game), lang=args.lang)+b'\0'
                lyric_ptrs += struct.pack("<2I", pos, lyric[0])
                body += lyric_bytes
                pos += len(lyric_bytes)
                song_ptr_off += 8
            lyric_ptrs += struct.pack("<I", 0)
            song_ptr_off += 4
            song_i += 1
        head_int_view.release()
        mv.release()
        head[seg_table_lyrics[0]:seg_table_lyrics[1]] = lyric_ptrs
        mv = memoryview(head)
        head_int_view=mv.cast("I")

    if tips_txt:
        #tip_i = seg_table_tip_ptrs[0]//4
        tip_ptr_off = seg_table_tips[0]+tip_page_ptrs_offset+tip_page_offset
        tip_text_ptrs = bytearray()
        tip_ptrs = bytearray()
        for tip in tips:
            tl_title = getattr(tip.title, args.lang)
            tl_pages = getattr(tip.pages, args.lang)
            title = tl_title or tip.title.jp
            pages = tl_pages or tip.pages.jp
            if not title: continue
            title_bytes = r11.str_to_r11_bytes(r11.clean_translation_line(title, args.lang, args.game), lang=args.lang)+b'\0'
            #head_int_view[tip_i] = tip_ptr_off
            tip_ptrs += struct.pack("<I", tip_ptr_off)
            tip_text_ptrs += struct.pack("<I", pos)
            tip_ptr_off += 4
            body += title_bytes
            pos += len(title_bytes)
            for p in pages:
                p_bytes = r11.str_to_r11_bytes(r11.clean_translation_line(p, args.lang, args.game), lang=args.lang)+b'\0'
                tip_text_ptrs += struct.pack("<I", pos)
                tip_ptr_off += 4
                body += p_bytes
                pos += len(p_bytes)
            #head_int_view[tip_i+1] = tip_ptr_off+4
            tip_ptrs += struct.pack("<II", tip_ptr_off+4, 0)
            tip_text_ptrs += struct.pack("<II", 0, 0x9090ffff)
            tip_ptr_off += 8
            #tip_i += 3
        head_int_view.release()
        mv.release()
        head[seg_table_tip_ptrs[0]:seg_table_tip_ptrs[1]] = tip_ptrs
        head[seg_table_tips[0]:seg_table_tips[1]] = tip_text_ptrs
        mv = memoryview(head)
        head_int_view=mv.cast("I")
        if new_tip_amount != tip_amount:
            head_short_view=mv.cast("H")
            tip_pages = []
            for i in range(tip_pages_amount):
                tip_page_ptr = head_int_view[seg_table_tip_page_ptrs[0]//4+i*2+1]//2
                tip_page = []
                while head_short_view[tip_page_ptr] != 0xffff:
                    tip_page.append(head_short_view[tip_page_ptr])
                    tip_page_ptr += 1
                tip_pages.append(tip_page)
            if new_tip_pages_amount != tip_pages_amount:
                tip_pages.append([])
            for i in range(tip_amount, new_tip_amount):
                tip_pages[-1].append(i)
            tip_page_bytes = bytearray()
            tip_page_ptrs_bytes = bytearray()
            page_symbols = ["ア", "カ", "サ", "タ", "ナ", "ハ", "マ", "ヤ", "ラ", "ワ"] # idk why preserve them, but why not
            for i in range(len(tip_pages)):
                tip_page_ptrs_bytes += struct.pack("<2I", pos, seg_table_tip_pages[0]+len(tip_page_bytes))
                page_symbol = r11.str_to_r11_bytes(page_symbols[i], "en")+b'\0'
                body += page_symbol
                pos += len(page_symbol)
                for j in tip_pages[i]:
                    tip_page_bytes += struct.pack("<H", j)
                tip_page_bytes += b"\xff\xff"
            for i in range(len(tip_pages), 10):
                tip_page_bytes += b"\xff\xff"
            if len(tip_page_bytes)%4:
                tip_page_bytes += b"\x90\x90"
            head_int_view.release()
            head_short_view.release()
            mv.release()
            head[seg_table_tip_page_ptrs[0]:seg_table_tip_page_ptrs[1]] = tip_page_ptrs_bytes
            head[seg_table_tip_pages[0]:seg_table_tip_pages[1]] = tip_page_bytes
            mv = memoryview(head)
            head_int_view=mv.cast("I")

    if chrono_txt:
        chrono = bytearray()
        i = 0
        for l in chronology_lines:
            if len(l) == 2 and l[1] == ':' and l[0] in "01234":
                i = int(l[0])
                continue
            chrono += struct.pack("<2I", pos, i)
            b = r11.str_to_r11_bytes(r11.clean_translation_line(l, args.lang, args.game), lang=args.lang)+b'\0'
            body += b
            pos += len(b)
        chrono += struct.pack("<I", 0)
        head_int_view.release()
        mv.release()
        head[seg_table_chrono[0]:seg_table_chrono[1]] = chrono
        mv = memoryview(head)
        head_int_view=mv.cast("I")

    jp_pattern = re.compile(r"^;([\da-fA-F]*);([\d]*);(.*)$")
    dupestr = ";dupe:"
    unusedstr = ";unused"
    litstr = ";lit;"
    i = -1
    while i < len(txt_lines)-1:
        i += 1
        ln = txt_lines[i]
        jp_match = jp_pattern.match(ln)
        if not jp_match:
            continue
        i += 1
        ln2 = txt_lines[i] if (i < len(txt_lines)) else ""

        addr = jp_match.group(1)
        table_offset = int(addr, 16)
        if table_offset > seg_table_lyrics[0]:
            table_offset += lyric_offset
        if table_offset > seg_table_tip_ptrs[0]:
            table_offset += tip_ptr_offset
        if table_offset > seg_table_tip_page_ptrs[0]:
            table_offset += tip_page_ptrs_offset
        if table_offset > seg_table_tip_pages[0]:
            table_offset += tip_page_offset
        if table_offset > seg_table_tips[0]:
            table_offset += tip_offset
        if table_offset > seg_table_chrono[0]:
            table_offset += chrono_offset
        #jp_len = jp_match.group(2) # not relevant

        if ln2.startswith(dupestr):
            dupe_ref_bytes = ln2[len(dupestr):]
            dupe_ref = int(dupe_ref_bytes, 16)
            if dupe_ref > seg_table_lyrics[0]:
                dupe_ref += lyric_offset
            if dupe_ref > seg_table_tip_ptrs[0]:
                dupe_ref += tip_ptr_offset
            if dupe_ref > seg_table_tip_page_ptrs[0]:
                dupe_ref += tip_page_ptrs_offset
            if dupe_ref > seg_table_tip_pages[0]:
                dupe_ref += tip_page_offset
            if dupe_ref > seg_table_tips[0]:
                dupe_ref += tip_offset
            if dupe_ref > seg_table_chrono[0]:
                dupe_ref += chrono_offset
            # Just reference the same string
            head_int_view[table_offset // 4] = head_int_view[dupe_ref // 4]
            continue
        jp_string = jp_match.group(3)
        tl_string = ln2
        if not ln2 or ln2[0] == "#":
            # fallback to original line
            tl_string = jp_string
        elif ln2.startswith(unusedstr):
            # clearly mark as untranslated to make detection more easy
            tl_string = "<" + addr + ":not_translated>"
        elif ln2.startswith(litstr):
            tl_string = tl_string[len(litstr):]
            if not tl_string: tl_string = jp_string
        elif ln2[0] == ";":
            print("Warning, unexpected ';' in the beginning of line [{}]".format(ln2))

        tl_string = r11.clean_translation_line(tl_string, args.lang, args.game)

        if ln2.startswith(litstr):
            tl_bytes = r11.str_to_r11_bytes(tl_string, exception_on_unknown=True)
        else:
            tl_bytes = r11.str_to_r11_bytes(tl_string, lang=args.lang, exception_on_unknown=True)

        head_int_view[table_offset // 4] = pos
        body += tl_bytes + b'\0'
        pos += len(tl_bytes) + 1

    head_int_view.release()
    mv.release()

    with open(args.init_output, "wb") as f_out:
        f_out.write(head)
        f_out.write(body)

if __name__ == "__main__":
    main()
