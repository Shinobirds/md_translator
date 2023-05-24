#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : packer.py
# @Author   : kang.chen
# @Time     : 2023/3/14
# @Note     :

import UnityPy
import os

PACKED_FILE_PATH = "temp/packer/"

ASSET_CONTAINER_NAME = {
    "card_name",
    "card_desc",
    "card_indx",
    "card_pidx",
    "card_part",
}


def unpack(asset_bundles: list[str]) -> dict:
    asset_map = {}
    for file_path in asset_bundles:
        env = UnityPy.load(file_path)
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            if obj.container is None:
                continue
            try:
                lang, container_name = obj.container.split("/")[-2:]
                container_name = container_name.removesuffix(".bytes")
            except ValueError:
                continue
            if (lang != "zh-cn") or (container_name not in ASSET_CONTAINER_NAME):
                continue
            data = obj.read()
            name = data.name
            if lang not in asset_map.keys():
                asset_map[lang] = {}
            if name not in asset_map[lang].keys():
                asset_map[lang][name] = {}
            asset_map[lang][name]["path_id"] = obj.path_id
            asset_map[lang][name]["data"] = data.script
            asset_map[lang][name]["file_path"] = file_path
    return asset_map


ASSET_NAME_LIST = {
    "CARD_Name",
    "CARD_Desc",
    "CARD_Indx",
    "Card_Pidx",
    "Card_Part",
}


def pack(asset_map: dict) -> list[str]:
    asset_bundles = []
    for asset_name in ASSET_NAME_LIST:
        asset_item = asset_map["zh-cn"][asset_name]
        origin_file_path = asset_item["file_path"]
        env = UnityPy.load(origin_file_path)
        env.out_path = PACKED_FILE_PATH
        saved = False
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            data = obj.read()
            if data.name != asset_name:
                continue
            data.script = asset_item["data"]
            data.save()
            saved = True
            break
        if saved:
            path = os.path.join(PACKED_FILE_PATH, os.path.basename(origin_file_path))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(env.file.save())
            asset_bundles.append(path)
        else:
            raise RuntimeError(f"pack {asset_name} error")
    return asset_bundles
