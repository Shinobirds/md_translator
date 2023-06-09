#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : asset_bundle.py
# @Author   : kang.chen
# @Time     : 2023/5/17
# @Note     :

import os.path
import shutil
import UnityPy
from typing import Callable, Optional

INPUT_PATH = "input/"
OUTPUT_PATH = "output/"

MD_EXE_FILE_NAME = "masterduel.exe"
MD_LOCAL_DATA_RELATIVE_PATH = "LocalData/"
MD_LOCAL_DATA_ZERO_FOLDER_NAME = "0000/"

INTERESTING_CONTAINER_NAME = {
    "card_name",
    "card_desc",
    "card_indx",
    "card_pidx",
    "card_part",
}


def __get_cn_text_asset_bundle_container_name(file_path) -> Optional[str]:
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
        if (lang != "zh-cn") or (container_name not in INTERESTING_CONTAINER_NAME):
            continue
        return container_name
    return None


def __get_md_traversal_path(md_path: str) -> str:
    if not md_path.endswith(MD_EXE_FILE_NAME):
        raise RuntimeError("invalid md path")
    md_local_data_path = os.path.join(os.path.dirname(md_path), MD_LOCAL_DATA_RELATIVE_PATH)
    if not os.path.exists(md_local_data_path):
        raise RuntimeError("LocalData not exists")
    account_folders = os.listdir(md_local_data_path)
    if len(account_folders) != 1:
        raise RuntimeError("multiple account folder")
    account_folder_name = account_folders[0]
    md_traversal_path = os.path.join(md_local_data_path, account_folder_name, MD_LOCAL_DATA_ZERO_FOLDER_NAME)
    if not os.path.exists(md_traversal_path):
        raise RuntimeError("md_traversal_path not exists")
    return md_traversal_path


def __copy_to_input_path(md_traversal_path: str, ui: Optional[Callable]):
    copied_container_name_list = set()
    for root, dirs, files in os.walk(md_traversal_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if callable(ui):
                ui(f"遍历MD文件中...\n{file_path}")
            container_name = __get_cn_text_asset_bundle_container_name(file_path)
            if container_name is not None:
                copied_container_name_list.add(container_name)
                shutil.copy(file_path, INPUT_PATH)
                if copied_container_name_list == INTERESTING_CONTAINER_NAME:
                    # done
                    return
    raise RuntimeError("file traversal error")


def copy_from_md(md_path: str = None, ui: Optional[Callable] = None) -> list[str]:
    if md_path is not None:
        shutil.rmtree(INPUT_PATH, ignore_errors=True)
        os.makedirs(INPUT_PATH, exist_ok=True)
        md_traversal_path = __get_md_traversal_path(md_path)
        __copy_to_input_path(md_traversal_path, ui)

    asset_bundles = []
    if not os.path.exists(INPUT_PATH):
        return asset_bundles
    for file_name in os.listdir(INPUT_PATH):
        file_path = os.path.join(INPUT_PATH, file_name)
        asset_bundles.append(file_path)
    return asset_bundles


def copy_to_output_path(asset_bundles: list[str], md_path: Optional[str] = None) -> None:
    shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    for file_path in asset_bundles:
        file_name = os.path.basename(file_path)
        if not os.path.isfile(file_path):
            continue
        if len(file_name) != 8:
            raise RuntimeError(f"invalid asset bundle [{file_name}]")
        dir_name = file_name[0:2]
        target_path = os.path.join(OUTPUT_PATH, dir_name, file_name)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy(file_path, target_path)
    if md_path is None:
        return
    md_traversal_path = __get_md_traversal_path(md_path)
    shutil.copytree(OUTPUT_PATH, md_traversal_path, dirs_exist_ok=True)
