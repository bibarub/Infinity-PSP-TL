#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script generates a file with the format required for further text repackaging with 'repack_scene' utility.
# Also: appends names, changes the encoding to sjis and replaces unsupported characters.

import argparse
import fileinput
import re
import sys
import os
import collections
from typing import List, Tuple

import r11.names as names
import r11

debug = False
should_run_buffer_overflow_validations = False
validate_jp_text = True

STATE_BLANK = 0
STATE_JP = 1
STATE_TRANSLATED_EN = 2
STATE_TRANSLATED_CN = 3
STATE_TRANSLATED_RU = 4

class TlBucket:
  def __init__(self):
    self.jp = None
    self.en = None
    self.cn = None
    self.ru = None

control_tip_pattern = re.compile(r"(?:%TS([0-9]{3}))")

def detectTips(text: str) -> Tuple:
  match = control_tip_pattern.search(text)
  return match.groups() if match else ()

def loadJpMacChapterFile(chapter_name: str, game: str) -> List[str]:
  orig_chapter_path = os.path.dirname(__file__) + f"/../text/tmp-{game}/mac-psp-jp/{chapter_name}.txt"
  r11_jp_lines = []
  with open(orig_chapter_path, "rb") as r11_jp_textfile:
    for raw_line in r11_jp_textfile:
      r11_jp_lines.append(r11.r11_bytes_to_str(raw_line))
  return r11_jp_lines

def filterTrueJpLines(lines: List[str]) -> List[str]:
  # starting from 4th line, every 2nd out of 3
  lines_filtered = [l.rstrip() for i, l in enumerate(lines[3:]) if i%3==1]
  return list(lines_filtered)

# parses lines from a chapters-psp/ file into a list of TlBucket objects
def loadTlBuckets(lines):
  state = STATE_JP
  tl_buckets = []
  current_tl_bucket = None

  for line in lines:
    line = line.rstrip("\n")
    if state == STATE_JP:
      if (line.strip() == ""):
        continue

      if (should_run_buffer_overflow_validations and "%K%P" in line and not line.endswith("%K%P")):
        eprint("Possible typo: found a symbol after '%%K%%P' in '%s'"%(line))

      current_tl_bucket = TlBucket()
      current_tl_bucket.jp = line
      tl_buckets.append(current_tl_bucket)
      state = STATE_TRANSLATED_EN

      # skips textless control sequences
      seqtest, _ = r11.rm_leading_control_sequence(line)
      if not seqtest:
        state = STATE_JP
        if should_run_buffer_overflow_validations and ("%P" in line or "%O" in line): page_buf = 0

    elif state == STATE_TRANSLATED_EN:
      current_tl_bucket.en = line
      # look for CN line next
      state = STATE_TRANSLATED_CN
      if line.strip() == "":
        eprint("EN line was empty! (jp)'{}'".format(current_tl_bucket.jp))

    elif state == STATE_TRANSLATED_CN:
      current_tl_bucket.cn = line
      state = STATE_TRANSLATED_RU
      if line.strip() == "":
        eprint("CN line was empty! (jp)'{}'".format(current_tl_bucket.jp))

    elif state == STATE_TRANSLATED_RU:
      current_tl_bucket.ru = line
      if line.strip() == "":
        eprint("RU line was empty! (jp)'{}'".format(current_tl_bucket.jp))
      # we have all lines, start looking for a JP line again
      state = STATE_JP
  #/for
  return tl_buckets

def prepareTlLines(tl_buckets, tl_suffix, game, current_filename, jp_mac_chapter_lines = None) -> bytes:
  out_lines_of_bytes_tl = []

  page_buf = 0

  # used to validate that jp lines have a 100% match with the original.
  jp_true_lines = filterTrueJpLines(jp_mac_chapter_lines) if jp_mac_chapter_lines else None


  for i, tlb in enumerate(tl_buckets):
    jp_line = tlb.jp
    en_line = tlb.en
    cn_line = tlb.cn
    ru_line = tlb.ru

    jp_line = r11.clean_translation_enc_issues(jp_line)
    if jp_true_lines:
      jp_true_line = jp_true_lines[i]
      if jp_true_line != jp_line:
        eprint("JP source mismatch; expected:'{}'; was:'{}' (~{})[{}]".format(jp_true_line, jp_line, i*5, current_filename))
        #jp_line = jp_true_line

    jp_tips = detectTips(jp_line)

    if (tl_suffix == "en" and not en_line) or (tl_suffix == "ru" and not ru_line) or (tl_suffix == "cn" and not cn_line):
      # output original if there's no TL
      out_lines_of_bytes_tl.append(r11.str_to_r11_bytes(jp_line, tl_suffix, exception_on_unknown=True) + b"\n")
      continue

    jp_line, jp_trailing_meta = r11.rm_trailing_control_sequence(jp_line)
    jp_line, jp_leading_meta = r11.rm_leading_control_sequence(jp_line)
    jp_speaker, jp_leading_bracket, jp_trailing_bracket, translated_speaker = names.detectJpSpeakerAndBrackets(jp_line, tl_suffix)

    # SA2_09 "穂鳥（犬伏景子）とオレは、ずっと前からこの施設にいたはずだ。"
    # i can't think of a way to properly handle this.
    # the left parenthesis isn't recongized by the game as a quotation, because the line appears in novel mode.
    if jp_leading_bracket == "（" and not jp_trailing_bracket and jp_speaker == "穂鳥":
        jp_speaker, jp_leading_bracket, translated_speaker = "", "", ""

    # SYEP "%LC少年『ぼくらは時間を超えられるんだ』%T090"
    if jp_leading_bracket == "『" and jp_speaker == "少年" and jp_leading_meta == "%LC":
        jp_speaker, jp_leading_bracket, jp_trailing_bracket, translated_speaker = "", "", "", ""

    export_translated_line = ""
    trailing_control = ""
    leading_control = ""
    leading_bracket = jp_leading_bracket
    trailing_bracket = jp_trailing_bracket

    if tl_suffix in ("en", "ru"):
      if tl_suffix == "en":
        if leading_bracket: leading_bracket = "“" if leading_bracket in "「『" else "(" if leading_bracket == "（" else ""
        if trailing_bracket: trailing_bracket = "”" if trailing_bracket in "」』" else ")" if trailing_bracket == "）" else ""
        tl_line = en_line
      elif tl_suffix == "ru":
        if leading_bracket: leading_bracket = "《" if leading_bracket in "「『" else "(" if leading_bracket == "（" else ""
        if trailing_bracket: trailing_bracket = "》" if trailing_bracket in "」』" else ")" if trailing_bracket == "）" else ""
        tl_line = ru_line
      if tl_line and tl_line[0] ==  ';':
        export_translated_line = r11.clean_translation_enc_issues(tl_line[1:])
      else:
        tl_tips = detectTips(tl_line)
        if (jp_tips != tl_tips):
          eprint("Tips tag missing. TL: {} JP: {}; (tl)'{}' (~{})[{}]".format(tl_tips, jp_tips, tl_line, i*5, current_filename))
        tl_line, tl_trailing_meta = r11.rm_trailing_control_sequence(tl_line)
        tl_line, tl_leading_meta = r11.rm_leading_control_sequence(tl_line)
        tl_line = r11.clean_translation_line(tl_line, tl_suffix, game)

        # nonen = re.findall(r"[^A-Za-z0-9!.,:;/?%\s〜―\"-*-「」♪『』α=！]", tl_line)
        # nonenlen = len(nonen)
        # lineLen = len(tl_line)
        # if nonenlen > 1:
        #   print("Warning! Found too many non-en chars: [{}] in line {}".format(nonen, tl_line))

        if translated_speaker and not tl_leading_meta:
          # append TL'ed speaker + opening bracket
          export_translated_line = "{}{}".format(translated_speaker, leading_bracket)
          # if jp_trailing_bracket and (jp_trailing_bracket != "\u300d"):
            # raise Exception("Unexpected trailing bracket '{}' captured '{}' (~{})[{}]".format(jp_trailing_bracket, jp_line, i*4, current_filename))
        # else:
        #  if (jp_trailing_bracket == "\u300d"):
        #    # Speaker was empty, but trailing bracket exists.
        #    if tl_line.__contains__("\u300c"):
        #      # TL line has its own bracket. Won't append any more
        #      jp_trailing_bracket = ""
        #    else:
        #      # TL line has no bracket.
        #      # Will append opening bracket, trailing bracket will be appended later
        #      #TODO reformat text to get rid of this case
        #      export_translated_line = "\u300c"
        #      eprint("TL Line auto-bracketed 「」 '{}' (~{})[{}]".format(tl_line, i*4, current_filename))
        #  elif (jp_trailing_bracket == "\u300f"):
        #    jp_trailing_bracket = ""

        export_translated_line += tl_line
        if tl_trailing_meta or tl_leading_meta:
          trailing_control = tl_trailing_meta
          leading_control = tl_leading_meta
          trailing_bracket = ""
        else:
          trailing_control = jp_trailing_meta
          leading_control = jp_leading_meta
        export_translated_line += trailing_bracket

    elif tl_suffix == 'cn':
      cn_tips = detectTips(cn_line)
      if (jp_tips != cn_tips):
        eprint("Tips tag missing. CN: {} JP: {}; (cn)'{}' (~{})[{}]".format(cn_tips, jp_tips, cn_line, i*5, current_filename))
      cn_line, cn_trailing_meta = r11.rm_trailing_control_sequence(cn_line)
      cn_line, cn_leading_meta = r11.rm_leading_control_sequence(cn_line)
      cn_line = r11.clean_cn_translation_line(cn_line)

      if not cn_line.startswith(translated_speaker):
        eprint("Speaker mismatch, expected {} at CN line '{}' (~{})[{}]".format(translated_speaker, cn_line, i*5, current_filename))
      export_translated_line = cn_line
      trailing_control = cn_trailing_meta if cn_trailing_meta else jp_trailing_meta
      leading_control = cn_leading_meta if cn_leading_meta else jp_leading_meta

    if should_run_buffer_overflow_validations:
      # check for buffer overflow. the game will probably run out of space on screen
      # before this, but that's harder to check given a variable width font.
      page_buf += len(export_translated_line)

      # Standard psp engine limit is 480
      if page_buf > 480:
        eprint("TEXT BUFFER OVERFLOW DETECTED. Predicted buffer size: %s at line #%s"%(page_buf, i))
      # if ja_speaker and len(export_translated_line) > 120:
      #   eprint("Warn: Single line size: %s at line #%s: %s"%(len(export_translated_line), i, export_translated_line))
      if ("%P" in trailing_control or "%O" in trailing_control):
        page_buf = 0

    export_translated_line = leading_control + export_translated_line + trailing_control

    out_lines_of_bytes_tl.append(r11.str_to_r11_bytes(export_translated_line, lang=tl_suffix, exception_on_unknown=True) + b"\n")
  # end of for i, tlb in enumerate(tl_buckets):

  return out_lines_of_bytes_tl

def main():

  parser = argparse.ArgumentParser(description="This script extracts translated lines for further text repackaging." +
            " Also appends names, changes the encoding to sjis and replaces unsupported characters.")
  parser.add_argument('--input', '-i', required=True, help='input file')
  parser.add_argument('--output', '-o', required=True, help='output file')
  parser.add_argument('--tl', '-t', required=True, help="what translation to use. Provide 'en', 'cn', or 'ru'", choices=['en', 'cn', 'ru'])
  parser.add_argument('--game', '-g', required=True, help="what game to translate for. Provide 'e17', 'n7', or 'r11'", choices=['e17', 'n7', 'r11'])
  parser.add_argument('--onlytl', action='store_true', help="If specified, will only output translated lines and nothing else.")

  args = parser.parse_args()

  names.init(args.game)

  lines = r11.readlines_utf8_crop_crlf(args.input)
  lines = [line for line in lines if not line.startswith("//")]
  tl_buckets = loadTlBuckets(lines)
  input_filename = os.path.basename(args.input)

  chaptername = input_filename[:-4]
  jp_mac_chapter_lines = loadJpMacChapterFile(chaptername, args.game) if not args.onlytl else None

  lines_tl = prepareTlLines(tl_buckets, args.tl, args.game, input_filename, jp_mac_chapter_lines)

  if (args.output):
    # tmp
    # hack_cn_utf8_dump = os.path.dirname(__file__) + "/../text/tmp/mac-cn-utf8/" + chaptername + ".txt"
    # hack_cn_utf8_full_dump = os.path.dirname(__file__) + "/../text/tmp/cn-text-utf8/fullscript.txt"
    # cn_full = open(hack_cn_utf8_full_dump, mode="a+", encoding="utf-8-sig")
    # cn_full.write(cn_line)

    # eprint("Writing preproc output to " + args.output + ". OnlyTL: " + str(args.onlytl))
    with open(args.output, "wb") as f:
      if (args.onlytl):
        f.writelines(lines_tl)

      else:
        # write first 3 lines as is
        f.writelines([r11.str_to_r11_bytes(l) for l in jp_mac_chapter_lines[:3]])

        # Then replace empty lines (every 3rd) with the translations
        for i, line_tl in enumerate(lines_tl):
          l = i * 3 + 3

          line_addr = r11.str_to_r11_bytes(jp_mac_chapter_lines[l], "en", exception_on_unknown=True)
          line_jp = r11.str_to_r11_bytes(jp_mac_chapter_lines[l+1], "en", exception_on_unknown=True)

          if len(line_jp) > 5 and line_jp[-3] == "%" and line_jp[-5:] != line_tl[-5:]:
            print("Warn: line {} ending mismatch. {} [{}:{}] JP:{} TL:{}".format(i, line_addr, line_jp[-3:], line_tl[-3:], line_jp, line_tl))

          # to_write = [line_addr, line_jp, line_tl]
          f.write(line_addr)
          f.write(line_jp)
          f.write(line_tl)


def eprint(*args, **kwargs):
  print(*args, **kwargs, file=sys.stderr)

if __name__ == '__main__':
  main()
