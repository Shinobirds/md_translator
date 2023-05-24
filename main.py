#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : main.py
# @Author   : kang.chen
# @Time     : 2023/3/23
# @Note     :

import encoder
import encrypter
import packer
import asset_bundle
import translator
from typing import Optional, Callable

import ygocdb

ui_interface_log: Optional[Callable] = None


def ui_print(s: str):
    if callable(ui_interface_log):
        ui_interface_log(s)
    else:
        print(s)


def main(md_path: str = None, update_ygocdb_file=True, log: Optional[Callable] = None):
    global ui_interface_log
    ui_interface_log = log

    if update_ygocdb_file:
        ui_print("更新百鸽数据...")
        ygocdb.update_ygocdb_file()

    ui_print("遍历MD文件...")
    origin_asset_files = asset_bundle.copy_from_md(md_path, ui=ui_print)

    ui_print("生成asset map...")
    asset_map = packer.unpack(origin_asset_files)

    ui_print("解密...")
    crack_key = encrypter.get_crack_key(asset_map['zh-cn']['CARD_Name']['data'])
    print(f"crack key:[{crack_key}]")
    encrypter.decrypt_asset_map(asset_map, crack_key)

    ui_print("提取asset文件...")
    encoder.extract_asset_map_files(asset_map)

    ui_print("生成卡片列表...")
    cards = encoder.gen_card_list(asset_map)

    ui_print("翻译中...")
    translator.translate(cards, ui=ui_print)
    encoder.accept_translation(cards)

    ui_print("更新asset map...")
    encoder.update_asset_map(asset_map, cards)

    ui_print("加密...")
    encrypter.encrypt_asset_map(asset_map, crack_key)

    ui_print("生成翻译文件...")
    translated_asset_files = packer.pack(asset_map)
    asset_bundle.copy_to_output_path(translated_asset_files, md_path=md_path)

    ui_print("成功")
    return


if __name__ == "__main__":
    main()
