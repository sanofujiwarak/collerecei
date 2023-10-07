# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger

from ..gui.yahoo_aucpay import read_params_with_gui
from ..receipt.yahoo_aucpay import main
from .utils import exec_selenium

logger = getLogger(__name__)


def start(licensed, title, icon, prefix, load_params, save_params):
    '''
    :param bool licensed: ライセンス認証結果
    :param str title: GUIに表示するタイトル
    :param str icon: iconファイルのパス
    :param str prefix: 各種ファイル名のprefix設定
    :param callable load_params: パラメーター設定を読み込む処理
    :param callable save_params: パラメーター設定を書き出す処理
    :return: dict
    '''
    try:
        params = read_params_with_gui(
            licensed,
            title,
            icon,
            prefix,
            load_params,
            save_params
        )
        logger.debug(params)

        exec_selenium(main, prefix, params)
        logger.info('処理が完了しました。Chromeのウィンドウを閉じてください。')
    except Exception as e:
        logger.error('%s: %s', type(e).__name__, e)
        logger.info('処理が正常に完了出来ませんでした。')
