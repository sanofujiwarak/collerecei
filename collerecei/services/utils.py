# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger
from os import environ, sep

from selenium.webdriver import ChromeOptions

import pselenium

DEBUG = False

logger = getLogger(__name__)


def save_screenshot(d, p):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    '''
    if DEBUG:
        return d.save_screenshot(f'{p["ss_prefix"]}{next(p["iter"])}.png')


def __get_webdriver(download_dir):
    '''
    :param str download_dir: スクリーンショット・pdf の保存先ディレクトリパス
    :return:
    '''
    if download_dir == '':
        download_dir = fr'.{sep}'
    environ.setdefault('APP_DOWNLOAD_DIR', download_dir)
    environ.setdefault('APP_SCREENSHOT_DIR', download_dir)

    o = ChromeOptions()
    o.binary_location = fr'tools{sep}GoogleChromePortable{sep}GoogleChromePortable.exe'
    o.headless = True
    o.add_argument('start-maximized')
    o.add_argument('enable-automation')
    o.add_argument('no-sandbox')
    o.add_argument('disable-infobars')
    o.add_argument('disable-extensions')
    o.add_argument('disable-dev-shm-usage')
    o.add_argument('disable-browser-side-navigation')
    o.add_argument('disable-gpu')
    o.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0')
    o.add_experimental_option(
        'prefs',
        {
            "download.default_directory": pselenium.get_download_dir(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    return pselenium.ChromePlus(fr'tools{sep}chromedriver.exe', options=o)


def exec_selenium(manipulate, module_name, params):
    '''
    :param callable manipulate:
    :param str module_name:
    :param dict params:
    :return:
    '''
    global DEBUG
    DEBUG = environ.get('DEBUG', False)
    d = __get_webdriver(params['store_path'])
    pselenium.exec(d, manipulate, module_name, params)
