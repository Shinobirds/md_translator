#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : ygocdb.py
# @Author   : kang.chen
# @Time     : 2023/5/15
# @Note     :
import os
import shutil

import requests
import zipfile
import re

YGOCDB_FILE_PATH = "resources/cards.json"
YGOCDB_DOWNLOAD_URL = "https://ygocdb.com/api/v0/cards.zip"
YGOCDB_DOWNLOAD_PATH = "temp/ygocdb/cards.zip"
YGOCDB_FILE_NAME = "cards.json"
YGOCDB_UNZIP_FILE_PATH = "temp/ygocdb/"


class Card:
    md_name: str = ""
    cn_name: str = ""
    jp_name: str = ""
    en_name: str = ""
    desc: str = ""
    p_desc: str = ""


YGOCDB_CARD_PATTERN = r""""[0-9]+": {
[\s\S]+?
  }"""

YGOCDB_JP_NAME_PATTERN = r'"(?:jp_name|md_jp_n)"\s*?:\s*?"(.*?)",'
YGOCDB_EN_NAME_PATTERN = r'"(?:en_name|wiki_en)"\s*?:\s*?"(.*?)",'
YGOCDB_CN_NAME_PATTERN = r'"cn_name"\s*?:\s*?"(.*?)",'
YGOCDB_MD_NAME_PATTERN = r'"md_name"\s*?:\s*?"(.*?)",'
YGOCDB_DESC_PATTERN = r'"desc"\s*?:\s*?"(.*?)"'
YGOCDB_PDESC_PATTERN = r'"pdesc"\s*?:\s*?"(.*?)"'


def load_cards_from_ygocdb_file() -> list[Card]:
    cards = []
    with open(YGOCDB_FILE_PATH, "r", encoding='utf-8') as f:
        cards_str = f.read()

        match_iters = re.finditer(YGOCDB_CARD_PATTERN, cards_str, re.MULTILINE)
        for card_match in match_iters:
            card_str = card_match.group(0)
            cn_match = re.search(YGOCDB_CN_NAME_PATTERN, card_str)
            if cn_match is None:
                continue
            jp_match = re.search(YGOCDB_JP_NAME_PATTERN, card_str)
            if jp_match is None:
                continue
            en_match = re.search(YGOCDB_EN_NAME_PATTERN, card_str)
            if en_match is None:
                continue
            md_match = re.search(YGOCDB_MD_NAME_PATTERN, card_str)
            if md_match is None:
                continue
            desc_match = re.search(YGOCDB_DESC_PATTERN, card_str)
            if desc_match is None:
                continue
            pdesc_match = re.search(YGOCDB_PDESC_PATTERN, card_str)
            if pdesc_match is None:
                continue

            cn_name = cn_match.group(1).replace(r'\"', r'"')
            en_name = en_match.group(1).replace(r'\"', r'"')
            jp_name = jp_match.group(1).replace(r'\"', r'"')
            md_name = md_match.group(1).replace(r'\"', r'"')

            desc = desc_match.group(1).replace(r"\r\n", "\n").replace(r"\n", "\n")
            pdesc = pdesc_match.group(1).replace(r"\r\n", "\n").replace(r"\n", "\n")

            card = Card()
            card.md_name = md_name
            card.cn_name = cn_name
            card.en_name = en_name
            card.jp_name = jp_name
            card.desc = desc
            card.p_desc = pdesc
            cards.append(card)

    return cards


def __download_ygocdb_file():
    r = requests.get(YGOCDB_DOWNLOAD_URL)
    r.raise_for_status()
    os.makedirs(os.path.dirname(YGOCDB_DOWNLOAD_PATH), exist_ok=True)
    with open(YGOCDB_DOWNLOAD_PATH, "wb") as f:
        f.write(r.content)
    r.close()


def __unzip_ygocdb_file():
    zip_file = zipfile.ZipFile(YGOCDB_DOWNLOAD_PATH, "r")
    zip_file.extract(member=YGOCDB_FILE_NAME, path=YGOCDB_UNZIP_FILE_PATH)
    zip_file.close()


def __overwrite_ygoddb_file():
    shutil.copy(os.path.join(YGOCDB_UNZIP_FILE_PATH, YGOCDB_FILE_NAME), YGOCDB_FILE_PATH)


def update_ygocdb_file() -> None:
    __download_ygocdb_file()
    __unzip_ygocdb_file()
    __overwrite_ygoddb_file()


def test():
    print("test start")
    update_ygocdb_file()
    print("test end")
    pass


if __name__ == "__main__":
    test()
