#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : encoder.py
# @Author   : kang.chen
# @Time     : 2023/3/17
# @Note     :

"""
各个asset文件均为小端（little-endian）

Card_Indx中每8字节指示一张卡的卡名和卡片文本，前4字节指示名字的字符串在CARD_Name中的偏移地址（和前一张卡的卡名的结束地址），
后4字节指示卡片文本在CARD_Desc中的偏移地址（和前一张卡的卡片文本的结束地址）

Card_Part中每4个字节指示一个效果，前2字节指示其基于该卡对应卡片文本的起始偏移地址，后2字节为结束偏移地址

Card_Pidx中每4字节指示一张卡片的效果数量，前2字节指示效果的起始序号（在Card_Part中），第3字节未知，可能为前两字节的扩展位，
第4个字节高4位指示怪兽效果数量，低4位指示灵摆效果数量；若为通常怪兽，则4个字节全0

各个文件指示的第一张卡都是无效的，值基本都为0，不是实际的卡
"""

import os.path
import archived_card
from md_card import Card
from util import read_little_endian_unsigned, write_little_endian_unsigned, str_to_bytes, bytes_to_str

EXTRACT_PATH = "temp/encoder/extract/"
ORIGIN_CARD_LIST_PATH = "temp/encoder/origin_card_list.txt"
TRANSLATION_ACCEPTED_CARD_LIST_PATH = "temp/encoder/translation_accepted_card_list.txt"
TRANSLATION_SKIPPED_CARD_LIST_PATH = "temp/encoder/translation_skipped_card_list.json"


def card_bytes_remove_suffix_zero(b: bytes) -> bytes:
    # 去掉末尾的\x00
    while b.endswith(b"\x00"):
        b = b.rstrip(b"\x00")
    return b


def card_bytes_add_suffix_zero(b: bytes) -> bytes:
    # 结尾加\x00并且保证{b}长度为4字节的整数倍
    byte_array = bytearray(b)
    byte_array.append(0)
    while (len(byte_array) % 4) != 0:
        byte_array.append(0)
    return bytes(byte_array)


def extract_asset_map_files(asset_map: dict, output_path: str = EXTRACT_PATH) -> None:
    for lang in asset_map.keys():
        lang_item: dict = asset_map[lang]
        for asset_name in lang_item.keys():
            asset_item: dict = lang_item[asset_name]
            origin_data: bytes = asset_item['data']
            try:
                origin_text = bytes_to_str(origin_data)
                path = os.path.join(output_path, lang, asset_name + ".txt")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(origin_text)
            except UnicodeDecodeError:
                path = os.path.join(output_path, lang, asset_name + ".bin")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(asset_item['data'])
            print(f"extracting - lang:{lang} asset_name:{asset_name} to {path}")


def __parse_card_name_list(asset_map: dict, lang: str) -> tuple[list[bytes], list[[int, int]]]:
    name_bytes_list: list[bytes] = []
    name_indx_list: list[[int, int]] = []

    lang_item: dict = asset_map[lang]
    name_data_bytes: bytes = lang_item["CARD_Name"]['data']
    index_data_bytes: bytes = lang_item['CARD_Indx']['data']

    assert len(index_data_bytes) % 8 == 0
    for i in range(0, len(index_data_bytes) - 8, 8):
        card_name_idx_start = read_little_endian_unsigned(index_data_bytes[i + 0:i + 4])
        card_name_idx_end = read_little_endian_unsigned(index_data_bytes[i + 8:i + 12])
        name_bytes = name_data_bytes[card_name_idx_start:card_name_idx_end]
        name_bytes_list.append(name_bytes)
        name_indx_list.append([card_name_idx_start, card_name_idx_end])

    return name_bytes_list, name_indx_list


def __parse_card_desc_list(asset_map: dict, lang: str) -> tuple[list[bytes], list[[int, int]]]:
    desc_bytes_list: list[bytes] = []
    desc_indx_list: list[[int, int]] = []

    lang_item: dict = asset_map[lang]
    desc_data_bytes: bytes = lang_item["CARD_Desc"]['data']
    index_data_bytes: bytes = lang_item['CARD_Indx']['data']

    assert len(index_data_bytes) % 8 == 0
    for i in range(0, len(index_data_bytes) - 8, 8):
        card_desc_idx_start = read_little_endian_unsigned(index_data_bytes[i + 4:i + 8])
        card_desc_idx_end = read_little_endian_unsigned(index_data_bytes[i + 12:i + 16])
        desc_bytes = desc_data_bytes[card_desc_idx_start:card_desc_idx_end]
        desc_bytes_list.append(desc_bytes)
        desc_indx_list.append([card_desc_idx_start, card_desc_idx_end])

    return desc_bytes_list, desc_indx_list


def __parse_card_pidx_list(asset_map: dict, lang: str) -> list[bytes]:
    card_pidx_list: list[bytes] = []
    lang_item: dict = asset_map[lang]
    data: bytes = lang_item['Card_Pidx']['data']
    for i in range(0, len(data), 4):
        card_pidx = data[i:i + 4]
        card_pidx_list.append(card_pidx)
    return card_pidx_list


def __parse_card_part_list(asset_map: dict, lang: str) -> list[[int, int]]:
    card_part_list: list[[int, int]] = []
    lang_item: dict = asset_map[lang]
    data: bytes = lang_item['Card_Part']['data']
    for i in range(0, len(data), 4):
        part_bytes = data[i:i + 4]
        part_start = read_little_endian_unsigned(part_bytes[0:2])
        part_end = read_little_endian_unsigned(part_bytes[2:4])
        card_part_list.append([part_start, part_end])
    return card_part_list


def gen_card_list(asset_map: dict) -> list[Card]:
    result: list[Card] = []

    card_name_bytes_list, card_name_indx_list = __parse_card_name_list(asset_map, "zh-cn")
    card_desc_bytes_list, card_desc_indx_list = __parse_card_desc_list(asset_map, "zh-cn")
    card_pidx_list = __parse_card_pidx_list(asset_map, "zh-cn")
    card_part_list = __parse_card_part_list(asset_map, "zh-cn")

    assert len(card_name_bytes_list) == len(card_desc_bytes_list)
    assert len(card_name_bytes_list) == len(card_pidx_list)

    calculated_total_part_num = 0
    for i in range(0, len(card_name_bytes_list)):
        card = Card()
        card.md_desc_bytes = card_bytes_remove_suffix_zero(card_name_bytes_list[i])
        card.md_name = bytes_to_str(card.md_desc_bytes)
        card.md_desc_bytes = card_bytes_remove_suffix_zero(card_desc_bytes_list[i])
        card.md_desc = bytes_to_str(card.md_desc_bytes)
        card.name_idx = card_name_indx_list[i]
        card.desc_idx = card_desc_indx_list[i]
        pidx_bytes: bytes = card_pidx_list[i]
        card.pidx = pidx_bytes

        effect_index = read_little_endian_unsigned(pidx_bytes[0:2])
        assert (pidx_bytes[2] & 0xFF) == 0
        effect_num = (pidx_bytes[3] >> 4) & 0xF
        peffect_num = (pidx_bytes[3] >> 0) & 0xF
        card.part = []
        for j in range(effect_num + peffect_num):
            card.part.append(card_part_list[effect_index + j])
            calculated_total_part_num += 1

        result.append(card)

    # 由于card0的pidx 和 part全为0，在上面的循环中不会计数，会漏掉一个{calculated_total_part_num}计数
    assert calculated_total_part_num + 1 == len(card_part_list)

    if ORIGIN_CARD_LIST_PATH is not None:
        os.makedirs(os.path.dirname(ORIGIN_CARD_LIST_PATH), exist_ok=True)
        with open(ORIGIN_CARD_LIST_PATH, "w", encoding="utf-8") as f:
            for card in result:
                f.write(str(card))

    return result


def __get_effect_identifier_pos_in_desc_bytes(desc_bytes: bytes) -> list[int]:
    if desc_bytes == b'':
        return []
    result = []
    if desc_bytes.startswith(str_to_bytes("①")):
        result.append(0)
        effect_identifiers = ["\n②", "\n③", "\n④", "\n⑤", "\n⑥", "\n⑦", "\n⑧", "\n⑨", "\n⑩"]
    else:
        effect_identifiers = ["\n①", "\n②", "\n③", "\n④", "\n⑤", "\n⑥", "\n⑦", "\n⑧", "\n⑨", "\n⑩"]
    for eid in effect_identifiers:
        try:
            pos = desc_bytes.index(str_to_bytes(eid))
            result.append(pos)
        except ValueError:
            pass
    return result


def __accept_translation_name(card: Card):
    if (card.translate_name is None) or (card.translate_name == ""):
        return
    card.md_name = card.translate_name


def __accept_translation_desc(card: Card) -> bool:
    if (card.translate_desc is None) or (card.translate_desc == ""):
        return False
    # effect_index = read_little_endian_unsigned(card.pidx[0:2])
    effect_num = (card.pidx[3] >> 4) & 0xF
    peffect_num = (card.pidx[3] >> 0) & 0xF

    def __desc_process(_effect_num: int, desc: str):
        effect_bytes = str_to_bytes(desc)
        calculated_effect_pos = __get_effect_identifier_pos_in_desc_bytes(effect_bytes)

        calculated_effect_num = len(calculated_effect_pos)
        parts = []
        if _effect_num == 0:
            pass
        elif _effect_num == 1:
            if calculated_effect_num == 0:
                parts.append([0, len(effect_bytes)])
            elif calculated_effect_num == 1:
                parts.append([calculated_effect_pos[0], len(effect_bytes)])
            else:
                raise RuntimeError("calculated_effect_num error for:" + str(card))
        else:
            if _effect_num != calculated_effect_num:
                raise ValueError("")
            calculated_effect_pos.append(len(effect_bytes))
            part = [[calculated_effect_pos[i], calculated_effect_pos[i + 1]] for i in
                    range(len(calculated_effect_pos) - 1)]
            parts.extend(part)
        return parts

    try:
        effect_parts = __desc_process(effect_num, card.translate_desc)
    except ValueError:
        return True
    except RuntimeError as e:
        raise e

    try:
        peffect_parts = __desc_process(peffect_num, card.translate_pdesc)
    except ValueError:
        return True
    except RuntimeError as e:
        raise e

    card.md_desc = card.translate_desc
    card.part = effect_parts
    if card.translate_pdesc != "":
        div_str = "\n【灵摆效果】\n"
        offset = len(str_to_bytes((card.md_desc + div_str)))
        peffect_parts = [[start + offset, end + offset] for [start, end] in peffect_parts]
        card.md_desc = card.md_desc + div_str + card.translate_pdesc
        card.part.extend(peffect_parts)
    return False


def accept_translation(card_list: list[Card]) -> None:
    # card0 excluded

    skipped_cards = []
    # card[1:]
    for card in card_list[1:]:
        trans_skipped = __accept_translation_desc(card)
        card.translate_desc = ""
        card.translate_pdesc = ""
        if trans_skipped:
            skipped_cards.append(card)
        else:
            __accept_translation_name(card)
            card.translate_name = ""

    if TRANSLATION_ACCEPTED_CARD_LIST_PATH is not None:
        os.makedirs(os.path.dirname(TRANSLATION_ACCEPTED_CARD_LIST_PATH), exist_ok=True)
        with open(TRANSLATION_ACCEPTED_CARD_LIST_PATH, "w", encoding="utf-8") as f:
            for card in card_list:
                f.write(str(card))

    if TRANSLATION_SKIPPED_CARD_LIST_PATH is not None:
        os.makedirs(os.path.dirname(TRANSLATION_SKIPPED_CARD_LIST_PATH), exist_ok=True)
        with open(TRANSLATION_SKIPPED_CARD_LIST_PATH, "w", encoding="utf-8") as f:
            f.write(archived_card.save_md_cards_as_archived_format(skipped_cards))

    """ 因为效果数量不匹配没有翻译成功的卡，需要手动归档 """
    if 0 != len(skipped_cards):
        raise RuntimeError(f"skipped trans:{len(skipped_cards)}")


def update_asset_map(asset_map: dict, card_list: list[Card]) -> None:
    card_name_byte_array = bytearray()
    card_desc_byte_array = bytearray()
    card_indx_byte_array = bytearray()
    card_pidx_byte_array = bytearray()
    card_part_byte_array = bytearray()

    # card0
    card0 = card_list[0]
    card_name_byte_array.extend(b"\x00\x00\x00\x00\x00\x00\x00\x00")
    card_desc_byte_array.extend(b"\x00\x00\x00\x00\x00\x00\x00\x00")
    [name_idx_start, name_idx_end] = card0.name_idx
    [desc_idx_start, desc_idx_end] = card0.desc_idx
    card_indx_byte_array.extend(write_little_endian_unsigned(name_idx_start, 4))
    card_indx_byte_array.extend(write_little_endian_unsigned(desc_idx_start, 4))
    card_indx_byte_array.extend(write_little_endian_unsigned(name_idx_end, 4))
    card_indx_byte_array.extend(write_little_endian_unsigned(desc_idx_end, 4))
    card_pidx_byte_array.extend(card0.pidx)
    card_part_byte_array.extend(b"\x00\x00\x00\x00")

    name_offset = card0.name_idx[1]
    desc_offset = card0.desc_idx[1]
    for card in card_list[1:]:
        card.md_name_bytes = card_bytes_add_suffix_zero(str_to_bytes(card.md_name))
        [name_idx_start, name_idx_end] = [name_offset, name_offset + len(card.md_name_bytes)]
        card.name_idx = [name_idx_start, name_idx_end]
        name_offset += len(card.md_name_bytes)

        card.md_desc_bytes = card_bytes_add_suffix_zero(str_to_bytes(card.md_desc))
        [desc_idx_start, desc_idx_end] = [desc_offset, desc_offset + len(card.md_desc_bytes)]
        card.desc_idx = [desc_idx_start, desc_idx_end]
        desc_offset += len(card.md_desc_bytes)

        assert (name_idx_start % 4) == 0
        assert (desc_idx_start % 4) == 0

        card_indx_byte_array.extend(write_little_endian_unsigned(name_idx_end, 4))
        card_indx_byte_array.extend(write_little_endian_unsigned(desc_idx_end, 4))

        card_name_byte_array.extend(card.md_name_bytes)
        card_desc_byte_array.extend(card.md_desc_bytes)

        card_pidx_byte_array.extend(card.pidx)

        for [start, end] in card.part:
            card_part_byte_array.extend(write_little_endian_unsigned(start, 2))
            card_part_byte_array.extend(write_little_endian_unsigned(end, 2))

    asset_map["zh-cn"]["CARD_Name"]["data"] = bytes(card_name_byte_array)
    asset_map["zh-cn"]["CARD_Desc"]["data"] = bytes(card_desc_byte_array)
    asset_map["zh-cn"]["CARD_Indx"]["data"] = bytes(card_indx_byte_array)
    asset_map["zh-cn"]["Card_Pidx"]["data"] = bytes(card_pidx_byte_array)
    asset_map["zh-cn"]["Card_Part"]["data"] = bytes(card_part_byte_array)

    pass
