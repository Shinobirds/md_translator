#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : card.py
# @Author   : kang.chen
# @Time     : 2023/3/1
# @Note     :


class Card:
    md_name: str = ""
    md_name_bytes: bytes = b''
    md_desc: str = ""
    md_desc_bytes: bytes = b''
    name_idx: [int, int] = []
    desc_idx: [int, int] = []
    pidx: bytes = b''
    part: list[[int, int]] = []
    translate_name: str = ""
    translate_desc: str = ""
    translate_pdesc: str = ""

    def __str__(self):
        def display_str_process(s: str) -> str:
            return s.replace(r'"', r'\"').replace("\r\n", r"\r\n").replace("\n", r"\n")

        return f'''[
    "md_name": "{display_str_process(self.md_name)}",
    "md_desc": "{display_str_process(self.md_desc)}",
    "name_idx": {self.name_idx},
    "desc_idx": {self.desc_idx},
    "pidx": b"{self.pidx.hex()}",
    "part": {self.part},
    "translate_name": "{display_str_process(self.translate_name)}",
    "translate_desc": "{display_str_process(self.translate_desc)}",
    "translate_pdesc": "{display_str_process(self.translate_pdesc)}",
],
'''
