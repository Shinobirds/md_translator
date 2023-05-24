#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : archived_cards.py
# @Author   : kang.chen
# @Time     : 2023/5/15
# @Note     :

"""
关于归档卡片：
归档卡片指依靠人手动翻译的卡片，包括：
(1)名称重复的卡片，例如“宝贝龙”和“宝贝虎龙”，在MD中卡名都叫“宝贝龙”，自动翻译无法区分它们，只能人为通过卡片效果进行区分
(2)卡片效果数量对应不上的卡，如“卡通恶魔”，YGOCDB的效果文本中缺乏“①、②这种标号”，导致自动翻译无法识别出效果数量
(3)部分YGOCDB翻译后没有效果标号，反而MD原本描述有效果标号的卡，如“异鱼”系列，所以决定保留MD原本的翻译

当自动翻译有问题无法翻译某些卡片时，会抛出runtime error并生成对应的错误卡片表，
开发者将其添加到归档卡片文件“ARCHIVED_FILE_PATH”中并手动翻译，之后就能正常运行。
"""

import md_card
import re
import os

ARCHIVED_FILE_PATH = "resources/archived_cards.json"


class Card:
    md_name: str = ""
    md_desc: str = ""
    translate_name: str = ""
    translate_desc: str = ""
    translate_pdesc: str = ""


CARD_PATTERN = r"""    {
[\s\S]+?
    },?"""

MD_NAME_PATTERN = r'"md_name"\s*?:\s*?"(.*?)",?'
MD_DESC_PATTERN = r'"md_desc"\s*?:\s*?"(.*?)",?'
TRANSLATE_NAME_PATTERN = r'"translate_name"\s*?:\s*?"(.*?)",?'
TRANSLATE_DESC_PATTERN = r'"translate_desc"\s*?:\s*?"(.*?)",?'
TRANSLATE_PDESC_PATTERN = r'"translate_pdesc"\s*?:\s*?"(.*?)",?'


def load_from_file() -> list[Card]:
    if not os.path.exists(ARCHIVED_FILE_PATH):
        return []
    with open(ARCHIVED_FILE_PATH, "r", encoding='utf-8') as f:
        cards_str = f.read()

        match_iters = re.finditer(CARD_PATTERN, cards_str, re.MULTILINE)
        cards = []
        for card_match in match_iters:
            card_str = card_match.group(0)

            md_name_match = re.search(MD_NAME_PATTERN, card_str)
            if md_name_match is None:
                continue
            md_desc_match = re.search(MD_DESC_PATTERN, card_str)
            if md_desc_match is None:
                continue
            translate_name_match = re.search(TRANSLATE_NAME_PATTERN, card_str)
            if translate_name_match is None:
                continue
            translate_desc_match = re.search(TRANSLATE_DESC_PATTERN, card_str)
            if translate_desc_match is None:
                continue
            translate_pdesc_match = re.search(TRANSLATE_PDESC_PATTERN, card_str)
            if translate_pdesc_match is None:
                continue

            md_name = md_name_match.group(1).replace(r'\"', r'"')
            md_desc = md_desc_match.group(1).replace(r"\r\n", "\n").replace(r"\n", "\n")
            translate_name = translate_name_match.group(1).replace(r'\"', r'"')
            translate_desc = translate_desc_match.group(1).replace(r"\r\n", "\n").replace(r"\n", "\n")
            translate_pdesc = translate_pdesc_match.group(1).replace(r"\r\n", "\n").replace(r"\n", "\n")

            card = Card()
            card.md_name = md_name
            card.md_desc = md_desc
            card.translate_name = translate_name
            card.translate_desc = translate_desc
            card.translate_pdesc = translate_pdesc
            cards.append(card)

        return cards


def save_md_cards_as_archived_format(md_cards: list[md_card.Card]) -> str:
    if 0 == len(md_cards):
        return ""

    s = "[\n"
    for i in range(len(md_cards)):
        c = md_cards[i]

        md_name = c.md_name.replace(r'"', r'\"')
        md_desc = c.md_desc.replace("\r\n", r"\r\n").replace("\n", r"\n")
        if 0 == i:
            c_s = "    {\n"
        else:
            c_s = ",\n    {\n"
        c_s += f"        \"md_name\":\"{md_name}\",\n"
        c_s += f"        \"md_desc\":\"{md_desc}\",\n"
        c_s += "        \"translate_name\":\"\",\n"
        c_s += "        \"translate_desc\":\"\",\n"
        c_s += "        \"translate_pdesc\":\"\"\n"
        c_s += "    }"
        s += c_s
    s += "\n]"
    return s
