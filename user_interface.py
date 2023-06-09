#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName : user_interface.py
# @Author   : kang.chen
# @Time     : 2023/3/23
# @Note     :

import flet as ft
import os
import sys
import traceback
from flet import Page, Row

from main import main as translate_start

DEBUG = len(sys.argv) > 1


def init(page: Page):
    page.title = "md translator"
    page.vertical_alignment = "center"
    page.window_width = 480
    page.window_min_width = 480
    page.window_height = 400
    page.window_min_height = 400
    page.padding = 0
    page.theme = ft.Theme(font_family="Microsoft YaHei")

    update_ygocdb_checkbox = ft.Checkbox(label="更新翻译数据库(百鸽)")
    update_ygocdb_checkbox.value = True

    md_path: str | None = None
    log_text = ft.Text(expand=True, text_align=ft.TextAlign.START)

    def on_file_pick(e: ft.FilePickerResultEvent):
        nonlocal md_path
        if e.files:
            if e.files[0].name == "masterduel.exe":
                md_path = e.files[0].path
            else:
                md_path = None
        else:
            md_path = None
        log_text.value = md_path
        log_text.update()
        translate_button.disabled = md_path is None
        translate_button.update()

    file_picker = ft.FilePicker(on_result=on_file_pick)
    page.overlay.append(file_picker)

    select_path_button = ft.ElevatedButton(
        "选择目录",
        icon=ft.icons.ADD,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["exe"],
            dialog_title="请选择游戏目录下的masterduel.exe文件"
        ),
    )

    def impl_print(s: str):
        log_text.value = s
        log_text.update()

    def translate(_):
        select_path_button.disabled = True
        select_path_button.update()
        translate_button.disabled = True
        translate_button.update()

        try:
            translate_start(md_path=md_path, update_ygocdb_file=update_ygocdb_checkbox.value, log=impl_print)
        except Exception as e:
            print(e)
            impl_print(traceback.format_exc())

        select_path_button.disabled = False
        select_path_button.update()
        translate_button.disabled = False
        translate_button.update()

    translate_button = ft.ElevatedButton(
        "开始翻译",
        icon=ft.icons.CHEVRON_RIGHT,
        on_click=translate,
    )
    translate_button.disabled = not DEBUG

    page.add(
        Row(
            [
                select_path_button,
                translate_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        Row(
            [
                update_ygocdb_checkbox
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        Row(
            [
                log_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )


if __name__ == "__main__":
    ft.app(target=init)
