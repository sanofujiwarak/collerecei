# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from datetime import datetime
from logging import getLogger
import sys

import PySimpleGUI as sg

logger = getLogger(__name__)


def read_params_with_gui(
        licensed, title, icon, prefix, load_params, save_params
):
    '''
    :param bool licensed: ライセンス認証結果
    :param str title: GUIに表示するタイトル
    :param str icon: iconファイルのパス
    :param str prefix: 各種ファイル名のprefix設定
    :param callable load_params: パラメーター設定を読み込む処理
    :param callable save_params: パラメーター設定を書き出す処理
    :return: dict
    '''
    TEXT_SIZE = (18, 1)
    PADDING = (5, (5, 16))
    sg.theme('BlueMono')
    datafile = f'{prefix}.data'
    p = load_params(datafile)
    y = datetime.now().year
    w = sg.Window(
        title,
        [
            [
                sg.Text('pdf 保存先ディレクトリ', size=TEXT_SIZE), sg.Input(p['store_path']),
                sg.FolderBrowse('参照')
            ],
            [sg.Text('メールアドレス', size=TEXT_SIZE), sg.Input(p['email'])],
            [sg.Text('パスワード', size=TEXT_SIZE), sg.Input(p['password'], password_char='*')],
            [
                sg.Text('取得対象 年', size=TEXT_SIZE),
                sg.OptionMenu(
                    [''] + [str(i) for i in range(y, y-8, -1)],
                    '' if p.get('target_year') is None else p['target_year']
                )
            ] if licensed else [],
            [
                sg.Text('取得対象 月', size=TEXT_SIZE, pad=PADDING),
                sg.OptionMenu(
                    [''] + [str(i) for i in range(1, 13)],
                    '' if p.get('target_month') is None else p['target_month'],
                    pad=PADDING
                )
            ] if licensed else [],
            [sg.Button('取得開始'), sg.Exit('終了')]
        ],
        icon=icon,
        text_justification='r'
    )

    event, values = w.read()
    w.close()
    logger.debug(f'{event}, {values}')
    if event == '取得開始':
        p = {
            'licensed': licensed,
            'store_path': values[0],
            'email': values[1],
            'password': values[2],
        }
        if licensed:
            p.update({
                'target_year': values[3],
                'target_month': values[4],
            })
        save_params(datafile, p)
        p['ss_prefix'] = f'{prefix}_'
        p['iter'] = (i for i in range(1, 100))
        return p
    else:
        logger.info('終了します。')
        sys.exit(0)
