#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re

import r11
from r11 import clean_translation_enc_issues

seg_table_e17 = [0xeb8, 0x7df8]
seg_text_e17 = [0x89b0, 0x1f709]
seg_table_r11 = [0x1140, 0xac98]
seg_text_r11 = [0xba68, 0x2c11a]
seg_table_n7 = [0x1ba8, 0x9904]
seg_text_n7 = [0xaf80, 0x2254f]

seg_table = None
seg_text = None

def main():

  if not 4 <= len(sys.argv) <= 5:
    exit("Usage: %s <translation.txt> <in.init> <out.init> <(optional) translation_lang='en'>"%sys.argv[0])

  global seg_table, seg_text
  game = os.environ["GAME"] if "GAME" in os.environ else "e17"
  if game == "e17":
    seg_table = seg_table_e17
    seg_text = seg_text_e17
  elif game == "r11":
    seg_table = seg_table_r11
    seg_text = seg_text_r11
  elif game == "n7":
    seg_table = seg_table_n7
    seg_text = seg_text_n7

  txt     = sys.argv[1]
  bin_in  = sys.argv[2]
  bin_out = sys.argv[3]

  encoding_table_lang = sys.argv[4] if sys.argv[4] else "en"

  txt_lines = r11.readlines_utf8_crop_crlf(txt)
  with open(bin_in, "rb") as f_bin:
    init_bytes = bytearray(f_bin.read())

  head = init_bytes[:seg_text[0]]
  mv = memoryview(head)
  head_int_view = mv.cast("I")
  body = bytearray()

  jp_pattern = re.compile("^;([\\da-fA-F]*);([\\d]*);(.*)$")
  dupestr = ";dupe:"
  unusedstr = ";unused"
  i = 0
  pos = 0
  while i < len(txt_lines):
    ln = txt_lines[i]
    jp_match = jp_pattern.match(ln)
    if jp_match:
      i += 1
      ln2 = txt_lines[i] if (i < len(txt_lines)) else ""

      addr = jp_match.group(1)
      table_offset = int(addr, 16)
      #jp_len = jp_match.group(2) # not relevant

      if (ln2.startswith(dupestr)):
        dupe_ref_bytes = ln2[len(dupestr):]
        dupe_ref = int(dupe_ref_bytes, 16)
        # Just reference the same string
        head_int_view[table_offset // 4] = head_int_view[dupe_ref // 4]
      else:
        jp_string = jp_match.group(3)
        tl_string = ln2
        if not ln2:
          # fallback to original line
          tl_string = jp_string
        elif ln2.startswith(unusedstr):
          # clearly mark as untranslated to make detection more easy
          tl_string = "<" + addr + ":not_translated>"
        elif ln2.startswith(";lit;"):
          tl_string = tl_string[5:]
          if not tl_string: tl_string = jp_string
        elif ln2.startswith(";"):
          print("Warning, unexpected ';' in the beginning of line [{}]".format(ln2))

        # tl_string = clean_translation_enc_issues(tl_string)
        if (encoding_table_lang == 'en' or encoding_table_lang == 'ru'):
          if game == "r11": tl_string = r11.clean_en_translation_line_r11(tl_string)
          tl_string = r11.clean_en_translation_line(tl_string)
        elif (encoding_table_lang == 'cn'):
          tl_string = r11.clean_cn_translation_line(tl_string)
        else:
          raise Exception("Unrecognized lang")


        if ln2.startswith(";lit;"):
          tl_bytes = r11.str_to_r11_bytes(tl_string, exception_on_unknown=True)
        else:
          tl_bytes = r11.str_to_r11_bytes(tl_string, lang=encoding_table_lang, exception_on_unknown=True)

        head_int_view[table_offset // 4] = pos + seg_text[0]
        body += tl_bytes + b'\x00'
        pos += len(tl_bytes) + 1
    i += 1

  mv.release()

  with open(bin_out, "wb") as f_out:
    f_out.write(head)
    f_out.write(body)


if __name__ == '__main__':
  main();
