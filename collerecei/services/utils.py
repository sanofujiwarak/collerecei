# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger
from os import environ, popen, sep

from helium import kill_browser

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

    o = pselenium.ChromeOptions()
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
    o.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0')
    o.add_argument('--lang=ja')
    o.add_argument('--accept-encoding=gzip,deflate,br,zstd')
    o.add_experimental_option(
        'prefs',
        {
            'intl.accept_languages': 'ja,en-US;q=0.9,en;q=0.8',
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
    try:
        pselenium.exec(d, manipulate, module_name, params)
    except Exception as e:
        d.save_screenshot(f'{module_name}_error.png')
        if DEBUG:
            logger.error('%s: %s', type(e).__name__, e)
            with open(f'{module_name}_error.html', 'w', encoding='utf-8') as f:
                f.write(d.page_source)
        raise e
    finally:
        kill_browser()
        popen('taskkill /F /IM chrome.exe')
