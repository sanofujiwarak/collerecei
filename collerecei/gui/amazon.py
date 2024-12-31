# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from datetime import datetime
from logging import getLogger
from sys import exit
from time import sleep

import PySimpleGUI as sg

from ..rename.amazon import divide_pdf

logger = getLogger(__name__)


def read_params_with_gui(
        licensed, title, icon, prefix, load_params, save_params
):
    """
    :param bool licensed: ライセンス認証結果
    :param str title: GUIに表示するタイトル
    :param str icon: iconファイルのパス
    :param str prefix: 各種ファイル名のprefix設定
    :param callable load_params: パラメーター設定を読み込む処理
    :param callable save_params: パラメーター設定を書き出す処理
    :return: dict
    """
    text_size = (18, 1)
    padding = (5, (5, 16))
    sg.theme('BlueMono')
    datafile = f'{prefix}.data'
    p = load_params(datafile)
    y = datetime.now().year
    w = sg.Window(
        title,
        [
            [
                sg.Text('pdf 保存先ディレクトリ', size=text_size), sg.Input(p['store_path']),
                sg.FolderBrowse('参照')
            ],
            [sg.Text('メールアドレス', size=text_size), sg.Input(p['email'])],
            [sg.Text('パスワード', size=text_size), sg.Input(p['password'], password_char='*')],
            [
                sg.Text('取得対象 年', size=text_size),
                sg.OptionMenu(
                    [''] + [str(i) for i in range(y, y-8, -1)],
                    '' if p.get('target_year') is None else p['target_year']
                )
            ] if licensed else [],
            [
                sg.Text('取得対象 月', size=text_size, pad=padding),
                sg.OptionMenu(
                    [''] + [str(i) for i in range(1, 13)],
                    '' if p.get('target_month') is None else p['target_month'],
                    pad=padding
                )
            ] if licensed else [],
            [sg.Button('取得開始'), sg.Button('ファイル名変更へ'), sg.Exit('終了')]
        ],
        icon=icon,
        text_justification='r'
    )

    event, values = w.read()
    w.close()
    logger.debug(f'{event}, {values}')
    if event == '取得開始':
        p.update({
            'licensed': licensed,
            'store_path': values[0],
            'email': values[1],
            'password': values[2],
        })
        if licensed:
            p.update({
                'target_year': values[3],
                'target_month': values[4],
            })
        save_params(datafile, p)
        p['ss_prefix'] = f'{prefix}_'
        p['iter'] = (i for i in range(1, 100))
        return p
    elif event == 'ファイル名変更へ':
        rename_window_gui(licensed, title, icon, prefix, load_params, save_params)
    else:
        logger.info('終了します。')
        exit(0)


def rename_window_gui(
        licensed, title, icon, prefix, load_params, save_params
):
    """
    :param bool licensed: ライセンス認証結果
    :param str title: GUIに表示するタイトル
    :param str icon: iconファイルのパス
    :param str prefix: 各種ファイル名のprefix設定
    :param callable load_params: パラメーター設定を読み込む処理
    :param callable save_params: パラメーター設定を書き出す処理
    :return: dict
    """
    text_size = (28, 1)
    sg.theme('BlueMono')
    datafile = f'{prefix}.data'
    p = load_params(datafile)
    # GUI
    w = sg.Window(
        title,
        [
            [
                sg.Text('ファイル名変更対象ファイル', size=text_size),
                sg.Input(),
                sg.FilesBrowse('参照') if licensed else sg.FileBrowse('参照')
            ],
            [
                sg.Text('変更後ファイル保存先ディレクトリ', size=text_size),
                sg.Input(p['rename_path'] if 'rename_path' in p else ''),
                sg.FolderBrowse('参照')
            ],
            [sg.Button('変更開始'), sg.Exit('終了')]
        ],
        icon=icon,
        text_justification='r'
    )

    # イベント処理
    event, values = w.read()
    w.close()
    logger.debug(f'{event}, {values}')
    if event == '変更開始':
        p.update({
            'licensed': licensed,
            'rename_path': values[1],
        })
        save_params(datafile, p)

        if licensed:
            for i in values[0].split(';'):
                divide_pdf(i, p['rename_path'])
                sleep(1)
        else:
            divide_pdf(values[0], p['rename_path'])
            sleep(3)
        rename_window_gui(licensed, title, icon, prefix, load_params, save_params)
    else:
        logger.info('終了します。')
        exit(0)
