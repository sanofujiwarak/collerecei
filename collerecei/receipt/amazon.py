# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger
from os import rename, path, sep
from time import sleep
import re

from helium import click, go_to, write
from selenium.common.exceptions import NoSuchElementException

from pselenium import By, TimeoutException, set_driver
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
            raise RuntimeError(d.find_element(
                By.XPATH,
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


def solve_puzzle(d, p, field: str = '上記の文字を入力してください'):
    """
    アカウント保護のため、このパズルを解いてください
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :param str field: 入力欄指定
    :return:
    """
    n = next(p["iter"])
    d.save_screenshot(f'{p["ss_prefix"]}{n}.png')
    puzzle = input(
        f'{p["store_path"]}{sep}{p["ss_prefix"]}{n}.png '
        f'を確認し、文字と数字を入力してください -> '
    )
    write(puzzle, into=field)
    logger.info('文字列を入力しました')
    save_screenshot(d, p)
    click('続行')
    sleep(2)


def input_password(d, p) -> None:
    """
    パスワード入力
    :param ChromePlus d:
    :param dict p: 設定
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    try:
        d.send_keys('ap_password', p['password'])
        logger.info('パスワードを入力しました')
    except TimeoutException:
        solve_puzzle(d, p)
        input_password(d, p)


def check_id(d, p):
    """
    IDを確認してください
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :return:
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    if 'IDを確認してください' in d.title:
        solve_puzzle(d, p, '上の文字と数字を入力してください')
        check_id(d, p)


def confirmation_code(d, p) -> bool:
    """
    確認コード入力
    :param ChromePlus d:
    :param dict p: 設定
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    try:
        # 「確認コード」の文言を探す
        click('確認コード')

        # 確認コードを入力
        code = input('Eメールを確認し、確認コードを入力してください -> ')
        d.send_keys('input-box-otp', code)
        logger.info('確認コードを入力しました')
        save_screenshot(d, p)
        click('コードを送信する')
        # d.url_changes(url)
        sleep(2)
    except (NoSuchElementException, LookupError):
        logger.info('確認コード入力不要')
        return True
    return False


def input_code(d, p) -> None:
    """
    確認コード入力
    :param ChromePlus d:
    :param dict p: 設定
    """
    while True:
        if confirmation_code(d, p):
            break


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
    # Eメールまたは携帯電話番号
    d.send_keys('ap_email', p['email'])
    logger.info('メールアドレスを入力しました')
    save_screenshot(d, p)
    click('次に進む')
    sleep(2)
    # パスワード
    input_password(d, p)
    # ログイン
    save_screenshot(d, p)
    d.click('signInSubmit')
    # IDを確認してください
    check_id(d, p)
    # 確認コード
    input_code(d, p)
    # account_fixup(d, p)


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
    else:
        # 過去3か月 表示
        go_to(
            'https://www.amazon.co.jp/gp/legacy/order-history'
            '?opt=ab&unifiedOrders=1&digitalOrders=1&returnTo=&_encoding=UTF8'
        )


def get_invoice_link(d, p, create_link: str, links: str):
    """適格請求書/支払い明細書/返金明細書 のリンクを取得"""
    d.click(create_link, By.XPATH)
    try:
        d.clickable(links, By.XPATH)
    except TimeoutException:
        d.click(create_link, By.XPATH)
        d.clickable(links, By.XPATH)
    save_screenshot(d, p)
    invoice_links = []
    try:
        for i in d.find_element(By.XPATH, links).find_elements(By.TAG_NAME, 'a'):
            href = i.get_property('href')
            if 'invoice.pdf' in href:
                invoice_links.append(href)
    except NoSuchElementException:
        pass
    return invoice_links


def get_order_data(p, d, i):
    """
    1注文の領収書データを取得
    :param dict p: 設定
    :param ChromePlus d:
    :param int i: 注文の位置
    :return: dict
    """
    r = {}
    order_card = f"/html/body/div[1]/div[1]/div[1]/div[5]/div[{i}]/div[1]/div/div/div/"
    r["注文日"] = d.find_element(
        By.XPATH,
        f'{order_card}div[1]/div/div[1]/div[2]/span'
    ).text
    r["注文番号"] = d.find_element(
        By.XPATH,
        f'{order_card}div[2]/div[1]/span[2]/bdi'
    ).text
    r["領収書"] = (
        f'https://www.amazon.co.jp/gp/digital/your-account/order-summary.html/'
        f'ref=oh_aui_ajax_dpi?ie=UTF8&orderID={r["注文番号"]}&print=1'
    ) if r["注文番号"][0] == 'D' else (
        f'https://www.amazon.co.jp/gp/css/summary/print.html/'
        f'ref=oh_aui_ajax_invoice?ie=UTF8&orderID={r["注文番号"]}'
    )
    if p['licensed'] and p.get('target_year'):
        # 対象年の指定有り
        r["invoice"] = get_invoice_link(
            d, p,
            f'{order_card}div[2]/div[2]/ul/span[1]/span/a',
            f'/html/body/div[{i + 1}]/div/div[1]/div/ul'
        )
    else:
        # 過去3か月 表示
        r["invoice"] = get_invoice_link(
            d, p,
            f'{order_card}div[2]/div[2]/ul/span[1]/span/a',
            f'/html/body/div[{i + 2}]/div/div[1]/div/ul'
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
        # 適格請求書/支払い明細書/返金明細書を取得
        ifile = f'{d.screenshot_dir}{sep}invoice.pdf'
        for j in range(len(i['invoice'])):
            d.get(i['invoice'][j])
            while not path.exists(ifile):
                # ダウンロード完了まで待つ
                sleep(1)
            rename(
                ifile,
                f"{d.screenshot_dir}{sep}invoice_Amazon.co.jp_{i['注文番号']}_{j + 1}.pdf"
            )
        sleep(1)
        # 領収書を取得
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
