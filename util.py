#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : util.py
# @Author   : kang.chen
# @Time     : 2023/5/18
# @Note     :


def read_little_endian_unsigned(b: bytes) -> int:
    return int.from_bytes(b, byteorder='little', signed=False)


def write_little_endian_unsigned(val: int, length: int) -> bytes:
    return val.to_bytes(length, byteorder="little", signed=False)


def str_to_bytes(s: str) -> bytes:
    return s.encode("utf-8")


def bytes_to_str(b: bytes) -> str:
    return b.decode("utf-8")
