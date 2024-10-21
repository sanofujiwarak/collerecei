# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger
from os import sep
import re

from helium import *
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from ..services.utils import save_screenshot

logger = getLogger(__name__)


def reinput_password(d, p, url):
    """
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :param str url:
    """
    try:
        d.url_changes(url)
    except TimeoutException:
        try:
            click('文字列を入力')
        except LookupError as e:
            raise RuntimeError(d.find_element_by_xpath(
                '//*[@id="auth-error-message-box"]/div/div/ul/li/span'
            ).text)
        # パスワードの再入力
        write(p['password'], into='パスワード')
        n = next(p["iter"])
        d.save_screenshot(f'{p["ss_prefix"]}{n}.png')
        code = input(
            f'{p["store_path"]}{sep}{p["ss_prefix"]}{n}.png '
            f'を確認し、文字列を入力してください -> '
        )
        write(code, into='文字列を入力')
        logger.info('文字列を入力しました')
        save_screenshot(d, p)
        d.click('signInSubmit')
        reinput_password(d, p, url)


def solve_puzzle(d, p):
    """
    アカウント保護のため、このパズルを解いてください
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :return:
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')

    if 'IDを確認してください' in d.title:
        n = next(p["iter"])
        d.save_screenshot(f'{p["ss_prefix"]}{n}.png')
        puzzle = input(
            f'{p["store_path"]}{sep}{p["ss_prefix"]}{n}.png '
            f'を確認し、文字と数字を入力してください -> '
        )
        d.send_keys('cvf_captcha_input', puzzle, By.NAME)
        logger.info('文字列を入力しました')
        save_screenshot(d, p)
        click('続行')
        d.url_changes(url)
        solve_puzzle(d, p)


def confirmation_code(d, p):
    """
    確認コード入力
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :return:
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    try:
        # 「確認コード」の文言を探す
        click('確認コード')

        # 確認コードを入力
        url = d.current_url
        logger.info(f'{d.title} {url}')
        code = input('確認コードを入力してください -> ')
        logger.debug(code)
        d.send_keys('input-box-otp', code)
        save_screenshot(d, p)
        click('コードを送信する')
        d.url_changes(url)

    except (NoSuchElementException, LookupError):
        logger.info('確認コード入力不要')


def account_fixup(d, p):
    """
    EメールアドレスをAmazonに追加する
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :return:
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    save_screenshot(d, p)
    if 'EメールアドレスをAmazonに追加する' in d.title:
        click('後で')


def login(d, p):
    """
    ログインする
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    d.send_keys('ap_email', p['email'])
    logger.info('メールアドレスを入力しました')
    save_screenshot(d, p)
    click('次に進む')
    d.url_changes(url)

    d.send_keys('ap_password', p['password'])
    logger.info('パスワードを入力しました')
    save_screenshot(d, p)
    d.click('signInSubmit')
    reinput_password(d, p, url)
    solve_puzzle(d, p)
    confirmation_code(d, p)
    account_fixup(d, p)


def open_order_history(d, p):
    """
    注文履歴画面を開く
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :return:
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    d.title_is('注文履歴')
    save_screenshot(d, p)
    if p['licensed'] and p.get('target_year'):
        # 対象年の指定有り
        go_to(
            f'https://www.amazon.co.jp/gp/your-account/order-history'
            f'?opt=ab&digitalOrders=1&unifiedOrders=1&returnTo='
            f'&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A'
            f'&orderFilter=year-{p["target_year"]}'
        )


def get_order_data(p, d, i):
    """
    1注文の領収書データを取得
    :param dict p: 設定
    :param pselenium.ChromePlus d:
    :param int i: 注文の位置
    :return: dict
    """
    r = {}
    if p['licensed'] and p.get('target_year'):
        # 年 表示
        order_card = f"/html/body/div[1]/div[1]/div[1]/div[5]/div[{i}]/"
    else:
        # 過去3か月 表示
        order_card = f"/html/body/div[1]/section/div[1]/div[{i + 7}]/div/"

    r["注文日"] = d.find_element_by_xpath(
        f'{order_card}div[1]/div/div/div/div[1]/div/div[1]/div[2]/span'
    ).text
    r["注文番号"] = d.find_element_by_xpath(
        f'{order_card}div[1]/div/div/div/div[2]/div[1]/span[2]/bdi'
    ).text
    r["領収書"] = (
        f'https://www.amazon.co.jp/gp/digital/your-account/order-summary.html/'
        f'ref=oh_aui_ajax_dpi?ie=UTF8&orderID={r["注文番号"]}&print=1'
    ) if r["注文番号"][0] == 'D' else (
        f'https://www.amazon.co.jp/gp/css/summary/print.html/'
        f'ref=oh_aui_ajax_invoice?ie=UTF8&orderID={r["注文番号"]}'
    )
    logger.debug(r)
    return r


def validate_order(p, r):
    """
    データ取得対象かを判断
    :param dict p: 設定
    :param dict r: order data
    :return: bool
    """
    if p.get('target_year') is None or p.get('target_month') is None \
            or p['target_year'] == '':
        # 対象年 または 対象月が未指定
        return True

    # 注文日の年月が対象月年月と同じかチェック
    s = re.search(r'(20[0-9]{2})年([1]?[0-9])月', r['注文日'])
    if s and p['target_year'] == s.group(1) and (
            p['target_month'] == '' or p['target_month'] == s.group(2)
    ):
        return True
    logger.info(f'データ取得対象外の注文です {r["注文日"]}, {r["注文番号"]}')
    return False


def collect_receipt_url(d, p, rl):
    """
    領収書のURLを収集
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :param list rl:
    :return:
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    for i in range(2, 12):
        try:
            r = get_order_data(p, d, i)
            if validate_order(p, r):
                logger.debug(f'取得対象のURL={r["領収書"]}')
                rl.append(r)
        except NoSuchElementException as e:
            # ページ途中で注文が無くなった場合
            logger.debug(e)

    if p['licensed']:
        try:
            # 「次へ」をクリック
            save_screenshot(d, p)
            d.click('.a-last > a:nth-child(1)', 'selector')
        except TimeoutException:
            # 「次へ」ボタンが無ければ終了
            return
        d.url_changes(url)

        # 次ページの処理
        collect_receipt_url(d, p, rl)


def get_receipt_pdf(d, rl):
    """
    領収書ページをpdf化
    :param pselenium.ChromePlus d:
    :param list rl:
    :return:
    """
    for i in rl:
        d.get(i['領収書'])
        url = d.current_url
        logger.info(f'{d.title} {url}')
        d.save_pdf(f"Amazon.co.jp_{i['注文番号']}.pdf")


def main(d, p):
    """
    :param pselenium.ChromePlus d:
    :param dict p:
    :return:
    """
    # 注文履歴画面を開く
    set_driver(d)
    go_to('https://www.amazon.co.jp/gp/css/order-history')
    login(d, p)
    open_order_history(d, p)

    # 領収書のURLを収集
    rl = []
    logger.info('領収書のURL収集を開始します')
    collect_receipt_url(d, p, rl)

    # 領収書ページをpdf化
    logger.info('領収書ページを保存します')
    get_receipt_pdf(d, rl)
