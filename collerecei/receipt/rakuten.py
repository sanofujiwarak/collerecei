# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from datetime import datetime
from logging import getLogger
from os import path, sep
from time import sleep

from helium import click, go_to
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from pselenium import By, TimeoutException, set_driver
from ..services.utils import save_screenshot

logger = getLogger(__name__)


def login(d, p):
    """
    :param ChromePlus d:
    :param dict p: 設定
    """
    url = d.current_url
    logger.info(f'{d.title} {url}')
    d.send_keys('user_id', p['email'])
    sleep(1)
    save_screenshot(d, p)
    click('次へ')
    d.clickable('password_current')
    d.send_keys('password_current', p['password'])
    sleep(1)
    save_screenshot(d, p)
    click('次へ')
    try:
        d.url_changes(url)
    except TimeoutException as e:
        logger.info('ログイン失敗')
        raise e


def set_period(d, p) -> str:
    """
    :param ChromePlus d:
    :param dict p: 設定
    """
    now = datetime.now()
    param = f'?order_year={now.year}&order_month={now.month}'
    if p['licensed']:
        if p['target_year']:
            param = f'?order_year={p["target_year"]}'
            if p['target_month']:
                param += f'&order_month={p["target_month"]}'
    return param


def get_order(d, p, i):
    """
    1注文の情報を取得
    :param ChromePlus d:
    :param dict p: 設定
    :param int i: 注文の位置
    :return: dict
    """
    r = {}
    ol = f"/html/body/div/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div[4]/div[1]/div[{i}]/div[1]/div/div/"
    r["注文日"] = d.find_element(By.XPATH, f'{ol}div[1]/div/div/div/div[2]/div[2]/div[1]/span[2]').text
    r["注文番号"] = d.find_element(By.XPATH, f'{ol}div[1]/div/div/div/div[2]/div[2]/div[2]/span[2]').text
    r["注文詳細"] = d.find_element(By.XPATH, f'{ol}div[2]/div/div[1]/a').get_attribute('href')
    logger.info(r)
    return r


def collect_order_data(d, p, ol):
    """
    注文情報を収集
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :param list ol:
    :return:
    """
    for i in range(1, 26):
        try:
            order = get_order(d, p, i)
            ol.append(order)
        except NoSuchElementException as e:
            # ページ途中で注文が無くなった場合
            logger.debug(str(e).splitlines()[0])
    # TODO: 複数ページ対応


def get_receipt_pdf(d, p, ol):
    """
    領収書ページをpdf化
    :param ChromePlus d:
    :param dict p: 設定
    :param list ol:
    :return:
    """
    for i in ol:
        go_to(i["注文詳細"])
        url = d.current_url
        logger.info(f'{d.title} {url}')
        button = '/html/body/div/div/div[2]/div/div[1]/div/div[1]/div[5]/div/div[2]/div[2]/button'
        save_screenshot(d, p)
        if len(d.find_elements(By.XPATH, button)) > 0:
            d.clickable(button, By.XPATH)
            # 宛名入力
            editable = True
            try:
                d.send_keys(
                    '/html/body/div/div/div[2]/div/div[1]/div/div[1]/div[5]/div/div[2]/div[1]/div/div[3]/div/div/input',
                    p['name'],
                    By.XPATH
                )
            except ElementNotInteractableException as e:
                logger.info(f'領収書再発行のため、宛名を設定出来ません: {i}')
                editable = False
            # 発行
            save_screenshot(d, p)
            d.click(button, By.XPATH)
            # 宛名の確認
            if editable:
                sleep(1)
                save_screenshot(d, p)
                click('OK')
            # ダウンロード完了まで待つ
            pdf = f'{d.screenshot_dir}{sep}order_receipt_{i["注文番号"]}.pdf'
            while not path.exists(pdf):
                sleep(1)
        else:
            logger.info(f'領収書が発行出来ません: {i}')


def main(d, p):
    """
    :param ChromePlus d:
    :param dict p:
    :return:
    """
    set_driver(d)

    # ログイン
    go_to('https://login.account.rakuten.com/sso/authorize?client_id=rakuten_ichiba_top_web&service_id=s245&response_type=code&scope=openid&redirect_uri=https%3A%2F%2Fwww.rakuten.co.jp%2F#/sign_in')
    login(d, p)

    # 購入履歴をクリック
    url = d.current_url
    logger.info(f'{d.title} {url}')
    save_screenshot(d, p)
    d.click('/html/body/div[1]/div[5]/div/div/div/div[2]/div[5]/a', By.XPATH, 30)
    d.url_changes(url)

    # 期間絞り込み用リクエストパラメータの設定
    param = set_period(d, p)

    # 購入履歴一覧
    d.set_window_size(900, 2880)
    go_to(f'https://order.my.rakuten.co.jp/purchase-history/order-list{param}')
    url = d.current_url
    logger.info(f'{d.title} {url}')
    save_screenshot(d, p)

    # 注文情報取得
    ol = []
    logger.info('注文情報の収集を開始します')
    collect_order_data(d, p, ol)

    # 領収書をダウンロード
    logger.info('領収書を保存します')
    d.set_window_size(900, 1440)
    get_receipt_pdf(d, p, ol)
