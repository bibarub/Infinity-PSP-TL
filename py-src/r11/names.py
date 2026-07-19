#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import collections

TlNames = collections.namedtuple("TlNames", ["en", "cn", "ru"])
# key - original japanese name
# value - list of translated values [en, cn, ru]
names_dict_generic = {
    "？？": TlNames("???", "？？", "???"),
    "みんな": TlNames("Everyone", "所有人", "Все"),
    "男": TlNames("Man", "男", "Мужчина"),
    "女": TlNames("Woman", "女", "Девушка"),
    "少年": TlNames("Boy", "男孩", "Мальчик"),
    "少女": TlNames("Girl", "女孩", "Девочка")
}
game_names_dicts = {
    "r11": {
        "こころ": TlNames("Kokoro", "心", "Кокоро"),
        "悟": TlNames("Satoru", "悟", "Сатору"),
        "黛": TlNames("Mayuzumi", "黛", "Маюдзуми"),
        "黄泉木": TlNames("Yomogi", "黄泉木", "Ёмоги"),
        "内海": TlNames("Utsumi", "内海", "Уцуми"),
        "犬伏": TlNames("Inubushi", "犬伏", "Инубуси"),
        "ゆに": TlNames("Yuni", "悠尼", "Юни"),
        "穂鳥": TlNames("Hotori", "穗鸟", "Хотори"),
        "榎本": TlNames("Enomoto", "鼷本", "Эномото"),
        "機長": TlNames("Pilot", "机长", "Пилот"),
        "ユウキドウ": TlNames("YUKIDOH", "优希堂", "Юкидо"),
        # These occur in init.bin only, but pasting them here, for reference
        "山岳救助隊員": TlNames("Mountain rescue worker", ";unused", ";unused"),
        "沙也香": TlNames("Sayaka", ";unused", ";unused"),
        "ゆに・黄泉木・黛": TlNames("Yuni, Yomogi, Mayuzumi", "悠尼、黄泉木、黛", "Юни, Ёмоги, Маюдзуми"), # unused
        "こころ・ゆに・黛": TlNames("Kokoro, Yuni, Mayuzumi", "心、悠尼、黛", "Кокоро, Юни, Маюдзуми"),
        "ゆに・穂鳥・内海": TlNames("Yuni, Hotori, Utsumi", "悠尼、穗鸟、内海", "Юни, Хотори, Уцуми"), # unused
        "ゆに・悟・穂鳥": TlNames("Yuni, Satoru, Hotori", "悠尼、悟、穗鸟", "Юни, Сатору, Хотори"),
        "黄泉木・黛": TlNames("Yomogi, Mayuzumi", "黄泉木、黛", "Ёмоги, Маюдзуми")
    },
    "e17": {
        "武": TlNames("Takeshi", None, "Такэси"),
        "少年": TlNames("Kid", None, "Малой"),
        "優": TlNames("You", None, "Ю"),
        "優春": TlNames("You'haru'", None, "Ю-хару"),
        "優秋": TlNames("You'aki'", None, "Ю-аки"),
        "つぐみ": TlNames("Tsugumi", None, "Цугуми"),
        "空": TlNames("Sora", None, "Сора"),
        "空Ａ": TlNames("Sora A", None, "Сора А"),
        "空Ｂ": TlNames("Sora B", None, "Сора Б"),
        "空Ｃ": TlNames("Sora C", None, "Сора В"),
        "偽空": TlNames("Fake Sora", None, "Фальшивая Сора"),
        "沙羅": TlNames("Sara", None, "Сара"),
        "ココ": TlNames("Coco", None, "Коко"),
        "ピピ": TlNames("Pipi", None, "Пипи"),
        "タヌキ": TlNames("Tanuki", None, "Тануки"),
        "ホクト": TlNames("Hokuto", None, "Хокуто"),
        "桑古木": TlNames("Kaburaki", None, "Кабураки"),
        "管制官": TlNames("Mission Control", None, "Рация"),
        "救助隊員": TlNames(";unused", ";unused", ";unused"),
        "研究員": TlNames("Researcher", None, "Учёный"),
        "自衛隊員": TlNames(";unused", ";unused", ";unused"),
        "係員": TlNames("Park Staff", None, "Персонал"),
        "部長": TlNames("Club President", None, "Президент Клуба"),
        "客": TlNames("Visitors", None, "Люди"),
        "少女": TlNames("Young Girl", None, "Девочка"),
        "アナウンス": TlNames("Announcement", None, "Автообъявление"),
        "田中先生": TlNames("Doctor Tanaka", None, "Доктор Танака"),
        "ＢＷ": TlNames("Blick Winkel", None, "БВ"),
        "マヨ": TlNames("Mayo", None, "Майо"),
        "女の子": TlNames("Girl", None, "Девушка"),
        "男の人": TlNames("Man", None, "Парень"),
        "女の人": TlNames("Woman", None, "Девушка"),
        "医師": TlNames("Doctor", None, "Врач"),
        "松永": TlNames("Matsunaga", None, "Сара"),
        "優・沙羅": TlNames("You, Sara", None, "Ю, Сара")
    },
    "n7": {
        "誠": TlNames("Makoto", None, None),
        "優夏": TlNames("Yuka", None, None),
        "億彦": TlNames("Okuhiko", None, None),
        "遙": TlNames("Haruka", None, None),
        "いづみ": TlNames("Izumi", None, None),
        "くるみ": TlNames("Kurumi", None, None),
        "沙紀": TlNames("Saki", None, None),
        "医者": TlNames("Doctor", None, None),
        "漁師": TlNames("Fisherman", None, None),
        "声": TlNames("Announcer", None, None),
        "運転手": TlNames("Driver", None, None),
        "守野姉妹": TlNames("Morino sisters", None, None),
        "男の子": TlNames("Boy", None, None),
        "女の子": TlNames("Girl", None, None),
        "先輩": TlNames("Senpai", None, None),
        "警官の声": TlNames("Police officer", None, None),
        "警備員": TlNames("Security guard", None, None),
        "看護師": TlNames("Nurse", None, None),
        "店員": TlNames("Clerk", None, None),
        "老人": TlNames("Old person", None, None),
        "店長": TlNames("Manager", None, None),
        "父": TlNames("Father", None, None),
        "半魚人": TlNames("Merman", None, None),
        "謎の声": TlNames("Mysterious voice", None, None),
        "サメ子": TlNames("Shark", None, None),
        "ラプラス": TlNames("Laplace", None, None),
        "ときみ": TlNames("Tokimi", None, None),
        "北大路": TlNames("Kitaoji", None, None),
        "女の声": TlNames("Female voice", None, None),
        "男の声": TlNames("Male voice", None, None),
        "少年の声": TlNames("Boy's voice", None, None),
        "新入生": TlNames("Freshman", None, None),
        "上級生": TlNames("Senior", None, None),
        "青年": TlNames("Kid", None, None),
        "教授": TlNames("Professor", None, None),
        "ふたり": TlNames("Couple", None, None),
        "漁師の客": TlNames("Fisherman client", None, None),
        "客": TlNames("Customer", None, None),
        "母親": TlNames("Mother", None, None),
        "ゆえ": TlNames("Yue", None, None),
        "不審人物": TlNames("Suspicious person", None, None),
        "島民Ａ": TlNames("Islander A", None, None),
        "いづみ以外": TlNames("All but Izumi", None, None),
        "サメの意識": TlNames("Shark's Mind", None, None),
        "人影": TlNames("Silhouette", None, None),
        "やさ男": TlNames("Kind Man", None, None),
        "キザな男": TlNames("Pretentious Man", None, None),
        "誠＆優夏": TlNames("Makoto & Yuka", None, None),
        "誠＆くるみ": TlNames("Makoto & Kurumi", None, None),
        "優夏＆億彦": TlNames("Yuka & Okuhiko", None, None),
        "誠・優夏": TlNames("Makoto & Yuka", None, None) # present in a user scenario, but not specified in init.bin by default
    }
}

names_dict = None
speech_brackets = ("「」", "『』", "（）")

def init(game: str) -> dict:
    global names_dict
    if not game in game_names_dicts:
        raise Exception(f"Game {game} is not supported.")
    names_dict = names_dict_generic | game_names_dicts[game]
    return names_dict

# tl_lang should be one of TlNames field names: "en", "cn", or "ru"
def detectJpSpeakerAndBrackets(jp_line: str, tl_lang: str) -> str:
    jp_speaker = ""
    jp_leading_bracket = ""
    jp_trailing_bracket = ""
    tl_speaker = ""
    for jp_name in names_dict:
        if not jp_line.startswith(jp_name):
            continue
        if len(jp_name) == len(jp_line):
            continue
        potential_bracket = jp_line[len(jp_name)]
        for brackets in speech_brackets:
            leading_bracket, trailing_bracket = tuple(brackets)
            if potential_bracket != leading_bracket:
                continue
            jp_leading_bracket = potential_bracket
            jp_speaker = jp_name
            if jp_line[-1] == trailing_bracket:
                jp_trailing_bracket = trailing_bracket
            # else: print("debug: trailing bracket not found", jp_line)
            break
        if jp_speaker:
            # if jp_leading_bracket != "「": print("debug: funny leading bracket", jp_line)
            tl_speaker = getattr(names_dict[jp_speaker], tl_lang)
            break
    return (jp_speaker, jp_leading_bracket, jp_trailing_bracket, tl_speaker)
