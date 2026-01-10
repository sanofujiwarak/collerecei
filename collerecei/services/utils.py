# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger
from os import environ, sep
from platform import system

from helium import set_driver, kill_browser

from pselenium import TimeoutException, ChromeOptions, ChromePlus, Service, get_download_dir

DEBUG = False

logger = getLogger(__name__)


def save_screenshot(d, p):
    """
    :param ChromePlus d:
    :param dict p: 設定
    """
    if DEBUG:
        d.save_screenshot(f'{p["ss_prefix"]}{next(p["iter"])}.png')


def wait_for_document_complete(d: ChromePlus, timeout: int = 30):
    """ページの読み込み完了を待つ"""
    try:
        d.document_complete(timeout)
    except TimeoutException as e:
        logger.warning('ページ読み込み中にタイムアウトが発生。ネットワーク速度が不足しています。')
        raise e


def set_slow_network(d: ChromePlus):
    # ネットワーク制限の設定
    kbps = 200
    d.execute_cdp_cmd('Network.emulateNetworkConditions', {
        'offline': False,
        'latency': 1600,  # 遅延 (ms)
        'downloadThroughput': kbps * 1024 / 8, # kbpsをバイト換算
        'uploadThroughput': kbps * 1024 / 8, # kbpsをバイト換算
    })
    # ネットワーク機能を有効化（これが必要な場合があります）
    d.execute_cdp_cmd('Network.enable', {})
    # キャッシュをクリア
    d.execute_cdp_cmd('Network.clearBrowserCache', {})


def __set_binary_location() -> str:
    pf = system()
    if pf == 'Windows':
        return fr'tools{sep}chrome-headless-shell-win64{sep}chrome-headless-shell.exe'
    elif pf == 'Darwin':
        return fr'tools{sep}chrome-headless-shell-mac-arm64{sep}chrome-headless-shell'
    raise RuntimeError('Unsupported platform!')


def __set_driver_location() -> str:
    pf = system()
    if pf == 'Windows':
        return fr'tools{sep}chromedriver.exe'
    elif pf == 'Darwin':
        return fr'tools{sep}chromedriver'
    raise RuntimeError('Unsupported platform!')


def __get_webdriver(download_dir) -> ChromePlus:
    """
    :param str download_dir: スクリーンショット・pdf の保存先ディレクトリパス
    """
    if download_dir == '':
        download_dir = fr'.{sep}'
    environ.setdefault('APP_DOWNLOAD_DIR', download_dir)
    environ.setdefault('APP_SCREENSHOT_DIR', download_dir)

    o = ChromeOptions()
    o.binary_location = __set_binary_location()
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
            "download.default_directory": get_download_dir(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    return ChromePlus(service=Service(__set_driver_location()), options=o)


def exec_selenium(manipulate, module_name, params):
    """
    :param callable manipulate:
    :param str module_name:
    :param dict params:
    :return:
    """
    global DEBUG
    DEBUG = environ.get('DEBUG', False)
    d = __get_webdriver(params['store_path'])
    try:
        set_driver(d)
        if DEBUG:
            set_slow_network(d)
        manipulate(d, params)
    except Exception as e:
        d.save_screenshot(f'{module_name}_error.png')
        if DEBUG:
            logger.error('%s: %s', type(e).__name__, e)
            with open(f'{d.screenshot_dir}{sep}{module_name}_error.html', 'w', encoding='utf-8') as f:
                f.write(d.page_source)
        raise e
    finally:
        kill_browser()
