import re
import sys
import os
from typing import List, NamedTuple, Tuple, Union

# CharsetElement = Tuple[int, bytes, str]
class CharsetElement(NamedTuple):
  charsetElement: int
  bytesequence: bytes
  character: str

# The original game font supports "JIS X 0208-1990" with some symbols from 2000.
# It is now best to use the charset conversion table (str_to_r11_bytes() function) generated for the game instead of standard python encodings
sjis_enc = "shift_jis_2004"
# sjis_enc = "sjis"

# chinese
# "GB2312"

control_sequences = set([
    "K", "N", "O", "P", "V", "p", "s", "n", "S", "d",
    "TE", "FS", "LL", "LC", "LR", "FE", "XS", "XE", "W"
])

r11_font_table_path: str = os.path.dirname(__file__) + "/../../text/charset-tables" + "/r11-en-font-table.txt"
r11_cn_font_table_path: str = os.path.dirname(__file__) + "/../../text/charset-tables" + "/r11-cn-font-table.txt"
r11_ru_font_table_path: str = os.path.dirname(__file__) + "/../../text/charset-tables" + "/r11-ru-font-table.txt"

en_r11_charset_as_list: Union[List[CharsetElement], None] = None
en_r11_utf8_to_codes: dict = dict()
en_r11_bytes_to_codes: dict = dict()
cn_r11_charset_as_list: Union[List[CharsetElement], None] = None
cn_r11_utf8_to_codes: dict = dict()
cn_r11_bytes_to_codes: dict = dict()
ru_r11_charset_as_list: Union[List[CharsetElement], None] = None
ru_r11_utf8_to_codes: dict = dict()
ru_r11_bytes_to_codes: dict = dict()

def handle_control_sequence(line: str, index: int) -> str:
  seq = line[index+1:index+3]
  if not seq.rstrip('\n'):
    print("edge case! empty control sequence")
    return ""
  if seq[0].isdigit():
    seq = line[index+1:index+4]
    if 'd' in seq:
      seq = seq[:seq.index('d')+1]
  elif seq[:2] in control_sequences:
    seq = seq[:2]
  elif seq[:2] == "TS" or seq[0] == 'C':
    seq = line[index+1:index+6]
  elif seq[0] == 'T' or seq[0] == 'X':
    seq = line[index+1:index+5]
  elif seq[0] in control_sequences:
    seq = seq[0]
  else:
    raise Exception(f"unhandled control sequence " + seq)

  return seq

def rm_trailing_control_sequence(line: str) -> Tuple[str, str]:
  line = line.rstrip('\n')
  tail = ""
  while (not line.endswith("%TE")) and ('%' in line) and (pos := line.rindex('%')):
    seq = handle_control_sequence(line, pos)
    if not line.endswith('%' + seq): break
    line = line[:-len(seq)-1]
    tail = '%' + seq + tail
  return line, tail

def rm_leading_control_sequence(line: str) -> Tuple[str, str]:
  line = line.rstrip('\n')
  head = ""
  while line.startswith('%') and (not line.startswith('%TS')):
    seq = handle_control_sequence(line, 0)
    line = line[len(seq)+1:]
    head += '%' + seq
  return line, head


def clean_translation_enc_issues(line: str) -> str:
  line = line.replace("\uff5e", "\u301c") # two versions of fullwidth tilde '〜' (aka wave dash), but the 2nd one can be converted to sjis
  line = line.replace("\u2014", "\u2015") # likewise for em dash '—'
  line = line.replace("\u2013", "\u2015") # en dash '–' -> em dash '—'
  # fullwidth minus '－' -> em dash '—'
  # In JP and EN translation pulled from tlwiki it was used to blank out time, i.e. "午後－－時－－分：スフィアに戻る" "－:－－PM: returned to SPHIA",
  # but now the main text is cleaned up to use em dash in JP and regular dash in EN.
  # It is still incorrectly used in init.bin JP text and some CN tips
  line = line.replace("\uff0d", "\u2015")

  # russian quotation marks
  line = line.replace("\u00ab", "\u300a")
  line = line.replace("\u00bb", "\u300b")
  #line = line.replace("„", "\"")
  return line

def clean_cn_translation_line(line: str) -> str:
  #line = clean_translation_enc_issues(line)
  line = line.replace("\u00B7", "\u30FB") # middle dot '·' -> katakana middle dot '・' (available in the font)
  return line

def clean_en_translation_line(line: str) -> str:
  return line

def clean_ru_translation_line(line: str) -> str:
  line = line.replace("'аки'", "%CFA4Fаки%CFFFF")
  line = line.replace("'хару'", "%CDE3Fхару%CFFFF")
  #line = line.replace("“", "\"")
  line = line.replace("‘", "'")
  line = line.replace("’", "'")
  return line

def clean_en_translation_line_r11(line: str) -> str:
  line = line.replace("'''I'''", "%CFFF0I%CFFFF") # ワタシ (katakana-watashi)
  line = line.replace("'''My'''", "%CFFF0My%CFFFF")
  line = line.replace("'''me'''", "%CFFF0me%CFFFF")
  line = line.replace("'''my'''", "%CFFF0my%CFFFF")
  line = line.replace("'''myself'''", "%CFFF0myself%CFFFF")

  line = line.replace("''I''", "%CFFCFI%CFFFF") # ENOMOTO's "私" (kanji-watashi)
  line = line.replace("''My''", "%CFFCFMy%CFFFF")
  line = line.replace("''me''", "%CFFCFme%CFFFF")
  line = line.replace("''my''", "%CFFCFmy%CFFFF")
  line = line.replace("''myself''", "%CFFCFmyself%CFFFF")

  line = line.replace("'I'", "%C88FFI%CFFFF") # YUKIDOH's "俺" (kanji-ore)
  line = line.replace("'My'", "%C88FFMy%CFFFF")
  line = line.replace("'me'", "%C88FFme%CFFFF")
  line = line.replace("'my'", "%C88FFmy%CFFFF")
  line = line.replace("'myself'", "%C88FFmyself%CFFFF")
  return line

def clean_ru_translation_line_r11(line: str) -> str:
  line = line.replace("|||Я|||", "%C8CFFЯ%CFFFF")
  line = line.replace("|||я|||", "%C8CFFя%CFFFF")
  line = line.replace("|||себя|||", "%C8CFFсебя%CFFFF")
  line = line.replace("||Я||", "%CF88FЯ%CFFFF")
  line = line.replace("||я||", "%CF88Fя%CFFFF")
  line = line.replace("||себя||", "%CF88Fсебя%CFFFF")
  line = line.replace("|Я|", "%C9C3FЯ%CFFFF")
  line = line.replace("|я|", "%C9C3Fя%CFFFF")
  line = line.replace("|себя|", "%C9C3Fсебя%CFFFF")
  return line

def clean_translation_line(line: str, lang="en", game=None) -> str:
  line = clean_translation_enc_issues(line)
  line = line.replace("<i>", "%CAAAF")
  line = line.replace("</i>", "%CFFFF")
  if lang == "en":
    if game == "r11":
      line = clean_en_translation_line_r11(line)
    #line = clean_en_translation_line(line)
  elif lang == "cn":
    line = clean_cn_translation_line(line)
  elif lang == "ru":
    if game == "r11":
      line = clean_ru_translation_line_r11(line)
    line = clean_ru_translation_line(line)
  return line

def println_sjis(line: str):
  sys.stdout.buffer.write(line.encode(sjis_enc))
  sys.stdout.buffer.write(b'\n')

def str_to_sjis_bytes(text: str, charset=sjis_enc) -> bytes:
  return text.encode(charset)

def sjis_bytes_to_str(sjisbytes: bytes, charset=sjis_enc) -> str:
  return sjisbytes.decode(charset)

def println_r11(text: str, lang = "en"):
  sys.stdout.buffer.write(str_to_r11_bytes(text, lang))
  sys.stdout.buffer.write(b'\n')

def str_to_r11_bytes(text: str, lang = "en", exception_on_unknown = False) -> bytes:
  (_, r11_utf8_to_codes, _) = _init_r11_charset(lang)
  r11_bytearray = bytearray()
  text_iter = iter(enumerate(text))
  for i, ch in text_iter:
    # regular whitespace
    if ch == ' ':
      r11_bytearray.extend(b'\x20')
    elif ch == '\n':
      r11_bytearray.extend(b'\n')
    elif ch == '\t':
      r11_bytearray.extend(b'\t')
    elif ch == '%':
      r11_bytearray.extend(b'%')
      seq = text[i+1:i+6]
      if not seq:
        print("edge case! empty control sequence")
        continue
      if seq[0] == '%':
        continue
      seq = handle_control_sequence(seq, -1)
      for _ in range(len(seq)): next(text_iter)
      r11_bytearray.extend(seq.encode("ascii"))
    else:
      try:
        r11_char_code = r11_utf8_to_codes[ch][1]
      except KeyError:
        if exception_on_unknown:
          raise Exception("character '{}' could not be mapped, lang {}".format(ch, lang))
        # print("r11 couldn't convert char:", ch, file=sys.stderr)
        r11_char_code = b'\x87\x40' #①
      r11_bytearray.extend(r11_char_code)
  return r11_bytearray

def r11_bytes_to_str(r11_bytes: bytes, lang = "en") -> str:
  (_, _, r11_bytes_to_codes) = _init_r11_charset(lang)
  r11_str = []
  r11_bytes_iter = iter(enumerate(r11_bytes)) 
  for i, b in r11_bytes_iter:
    b = b.to_bytes()
    if b == b' ':
      r11_str.extend(' ')
    elif b == b'\n':
      r11_str.extend('\n')
    elif b == b'\t':
      r11_str.extend('\t')
    elif b == b'%':
      r11_str.extend('%')
      try:
        seq = r11_bytes[i+1:i+6].decode(sjis_enc)
      except UnicodeDecodeError:
        seq = r11_bytes[i+1:i+5].decode(sjis_enc)
      if not seq:
        print("edge case! empty control sequence")
        continue
      if seq[0] == '%':
        continue
      seq = handle_control_sequence(seq, -1)
      for _ in range(len(seq)): next(r11_bytes_iter)
      r11_str.extend(seq)
    else:
      try:
        r11_str.extend(r11_bytes_to_codes[b][2])
      except KeyError:
        b = b + next(r11_bytes_iter)[1].to_bytes()
        r11_str.extend(r11_bytes_to_codes[b][2])
  return "".join(r11_str)

def str_to_r11_font_codepoints(text: str, lang = "en") -> List[int]:
  (_, r11_utf8_to_codes, _) = _init_r11_charset(lang)
  fontIndices = []
  for ch in text:
    # regular whitespace - special handling (hardcoded)
    if ch == ' ':
      fontIndices.append(751)
      continue

    try:
      r11_char_code = r11_utf8_to_codes[ch][0]
      fontIndices.append(r11_char_code)
    except KeyError:
      # print("r11 couldn't convert char:", ch, file=sys.stderr)
      fontIndices.append(-1)
  return fontIndices

def _init_r11_charset(lang = "en"):  
  if lang == "en":
    global en_r11_charset_as_list
    global en_r11_utf8_to_codes
    global en_r11_bytes_to_codes
    if en_r11_charset_as_list != None:
      return (en_r11_charset_as_list, en_r11_utf8_to_codes, en_r11_bytes_to_codes)
    (en_r11_charset_as_list, en_r11_utf8_to_codes, en_r11_bytes_to_codes) = _load_r11_font_table(r11_font_table_path)
    return (en_r11_charset_as_list, en_r11_utf8_to_codes, en_r11_bytes_to_codes)
  elif lang == "cn":
    global cn_r11_charset_as_list
    global cn_r11_utf8_to_codes
    global cn_r11_bytes_to_codes
    if cn_r11_charset_as_list != None:
      return (cn_r11_charset_as_list, cn_r11_utf8_to_codes, cn_r11_bytes_to_codes)
    (cn_r11_charset_as_list, cn_r11_utf8_to_codes, cn_r11_bytes_to_codes) = _load_r11_font_table(r11_cn_font_table_path)
    return (cn_r11_charset_as_list, cn_r11_utf8_to_codes, cn_r11_bytes_to_codes)
  elif lang == "ru":
    global ru_r11_charset_as_list
    global ru_r11_utf8_to_codes
    global ru_r11_bytes_to_codes
    if ru_r11_charset_as_list != None:
      return (ru_r11_charset_as_list, ru_r11_utf8_to_codes, ru_r11_bytes_to_codes)
    (ru_r11_charset_as_list, ru_r11_utf8_to_codes, ru_r11_bytes_to_codes) = _load_r11_font_table(r11_ru_font_table_path)
    return (ru_r11_charset_as_list, ru_r11_utf8_to_codes, ru_r11_bytes_to_codes)
  else:
    raise Exception("lang parameter not supported: '{}'".format(lang))

def _load_r11_font_table(r11_font_table_path) -> Tuple[List[CharsetElement], dict, dict]:
  r11_charset_lines = readlines_utf8_crop_crlf(r11_font_table_path)

  split = [x.split("\t", maxsplit=3) for x in r11_charset_lines]
  ## [<font code point>:int, <sjis sequence>:bytes, <utf8 char>:str]
  table_as_list = [CharsetElement(int(x[0][:-1]), bytes.fromhex(x[1][2:]), x[2]) for x in split]
  utf8_to_codes = dict()
  bytes_to_codes = dict()
  #validate and build dicts
  for i, v in enumerate(table_as_list):
    if i != v[0]:
      raise Exception("Charset index was not sequential")

    utf8_ch = v[2]
    r11_b = v[1]
    utf8_to_codes[utf8_ch] = v
    bytes_to_codes[r11_b] = v
  return (table_as_list, utf8_to_codes, bytes_to_codes)

def readlines_utf8_crop_crlf(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return [l.rstrip('\r\n') for l in f.readlines()]
