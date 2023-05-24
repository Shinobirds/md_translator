#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : translator.py
# @Author   : kang.chen
# @Time     : 2023/3/17
# @Note     :

import os
from enum import Enum
from typing import Callable, Optional

import archived_card
import main
import md_card
import ygocdb
from util import str_to_bytes, bytes_to_str

TRANSLATED_LIST_PATH = "temp/translator/translated_card_list.txt"
MISMATCHED_LIST_PATH = "temp/translator/mismatched_card_list.txt"
DUPLICATE_MATCHED_LIST_PATH = "temp/translator/duplicate_matched_card_list.txt"


class TranslateResult(Enum):
    SUCCESS = 0,
    MISMATCHED = 1,
    DUPLICATED = 2


def translate_by_archived_cards(card: md_card.Card, archived_card_list: list[archived_card.Card]) -> TranslateResult:
    for c in archived_card_list:
        if c.md_name == card.md_name and c.md_desc == card.md_desc:
            if c.translate_name != "":
                card.translate_name = c.translate_name
                card.translate_desc = c.translate_desc
                card.translate_pdesc = c.translate_pdesc
                return TranslateResult.SUCCESS

    return TranslateResult.MISMATCHED


def translate_by_ygocdb_with_md_name(card: md_card.Card, translate_info_list: list[ygocdb.Card]) -> TranslateResult:
    found_info = None
    for info in translate_info_list:
        if info.md_name != card.md_name:
            continue
        if found_info is not None:
            return TranslateResult.DUPLICATED
        found_info = info
    if found_info is None:
        return TranslateResult.MISMATCHED

    card.translate_name = found_info.cn_name
    card.translate_desc = found_info.desc
    card.translate_pdesc = found_info.p_desc
    return TranslateResult.SUCCESS


def translate_by_ygocdb_with_en_name(card: md_card.Card, translate_info_list: list[ygocdb.Card]) -> TranslateResult:
    found_info = None
    for info in translate_info_list:
        if info.en_name != card.md_name:
            continue
        if found_info is not None:
            return TranslateResult.DUPLICATED
        found_info = info
    if found_info is None:
        return TranslateResult.MISMATCHED

    card.translate_name = found_info.cn_name
    card.translate_desc = found_info.desc
    card.translate_pdesc = found_info.p_desc
    return TranslateResult.SUCCESS


def __name_process_for_md_name(s: str) -> str:
    s_bytes = str_to_bytes(s)
    s_bytes = s_bytes.replace(b"\xC2\xA0", b"\x20")
    return bytes_to_str(s_bytes)


def translate(cards: list[md_card.Card], ui: Optional[Callable]) -> None:
    archived_card_list = archived_card.load_from_file()
    print("len(archived_card_list) :", len(archived_card_list))
    translate_info_list: list[ygocdb.Card] = ygocdb.load_cards_from_ygocdb_file()

    # card list 中文预处理
    for card in cards:
        card.md_name = __name_process_for_md_name(card.md_name)

    mismatched_cards = []
    duplicate_matched_cards = []
    # skip card 0
    for card in cards[1:]:
        if callable(ui):
            ui(f"翻译中 - [{cards.index(card) + 1}/{len(cards)}] [{card.md_name}]")

        translate_result = translate_by_archived_cards(card, archived_card_list)
        if TranslateResult.SUCCESS == translate_result:
            continue

        translate_result = translate_by_ygocdb_with_md_name(card, translate_info_list)
        if TranslateResult.DUPLICATED == translate_result:
            duplicate_matched_cards.append(card)
        elif TranslateResult.MISMATCHED == translate_result:
            # 衍生物
            if card.md_name.endswith("衍生物"):
                continue

            # 有些卡还是全英文的, 按英文去匹配
            if card.md_name.isascii():
                translate_result = translate_by_ygocdb_with_en_name(card, translate_info_list)
                if TranslateResult.DUPLICATED == translate_result:
                    duplicate_matched_cards.append(card)
                elif TranslateResult.MISMATCHED == translate_result:
                    # 衍生物
                    if card.md_name.endswith(" Token"):
                        continue
                    mismatched_cards.append(card)
            else:
                mismatched_cards.append(card)

    if TRANSLATED_LIST_PATH is not None:
        os.makedirs(os.path.dirname(TRANSLATED_LIST_PATH), exist_ok=True)
        with open(TRANSLATED_LIST_PATH, "w", encoding="utf-8") as f:
            for card in cards:
                f.write(str(card))
    if MISMATCHED_LIST_PATH is not None:
        os.makedirs(os.path.dirname(MISMATCHED_LIST_PATH), exist_ok=True)
        with open(MISMATCHED_LIST_PATH, "w", encoding="utf-8") as f:
            f.write(archived_card.save_md_cards_as_archived_format(mismatched_cards))

    if DUPLICATE_MATCHED_LIST_PATH is not None:
        os.makedirs(os.path.dirname(DUPLICATE_MATCHED_LIST_PATH), exist_ok=True)
        with open(DUPLICATE_MATCHED_LIST_PATH, "w", encoding="utf-8") as f:
            f.write(archived_card.save_md_cards_as_archived_format(duplicate_matched_cards))

    """ 没有匹配成功的卡，需要手动归档 """
    if 0 != len(mismatched_cards) or 0 != len(duplicate_matched_cards):
        raise RuntimeError(
            f"mismatched_cards:{len(mismatched_cards)}  duplicate_matched_cards:{len(duplicate_matched_cards)}")
    pass
