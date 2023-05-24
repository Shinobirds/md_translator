#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : encrypter.py
# @Author   : kang.chen
# @Time     : 2023/3/16
# @Note     :
import os
import zlib

DEFAULT_KEY = 95


def get_crack_key(encrypted_data: bytes) -> int:
    def try_decompress(_b: bytes, _key):
        data = bytearray(_b)
        for i in range(len(data)):
            v = i + _key + 0x23D
            v *= _key
            v ^= i % 7
            data[i] ^= v & 0xFF
        zlib.decompress(data)

    for key in range(0xFF):
        try:
            try_decompress(encrypted_data, key)
            return key
        except zlib.error:
            pass
    raise RuntimeError("get crack key failed")


def decrypt_data(encrypted_data: bytes, key: int = DEFAULT_KEY) -> bytes:
    data = bytearray(encrypted_data)
    for i in range(len(data)):
        v = i + key + 0x23D
        v *= key
        v ^= i % 7
        data[i] ^= (v & 0xFF)
    return zlib.decompress(data)


def encrypt_data(decrypted_data: bytes, key: int = DEFAULT_KEY) -> bytes:
    data = bytearray(zlib.compress(decrypted_data))
    for i in range(len(data)):
        v = i + key + 0x23D
        v *= key
        v ^= i % 7
        data[i] ^= v & 0xFF
    return bytes(data)


def decrypt_asset_map(asset_map: dict, key: int = DEFAULT_KEY) -> None:
    for lang in asset_map.values():
        for asset_name in lang.values():
            data = asset_name['data']
            asset_name['data'] = decrypt_data(data, key)
    pass


def encrypt_asset_map(asset_map: dict, key: int = DEFAULT_KEY) -> None:
    for lang in asset_map.values():
        for asset_name in lang.values():
            data = asset_name['data']
            asset_name['data'] = encrypt_data(data, key)
    pass
