# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger

from helium import *
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from ..services.utils import save_screenshot

logger = getLogger(__name__)


def input_password(d, p):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    '''
    try:
        d.clickable('passwd')

        # パスワードの入力
        url = d.current_url
        logger.info(f'{d.title} {url}')
        write(p['password'], into='パスワード')
        logger.info('パスワードを入力しました')
        save_screenshot(d, p)
        click('ログイン')
    except TimeoutException:
        logger.info('パスワード入力不要')
    finally:
        click('確認コード')


def login(d, p):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    '''
    url = d.current_url
    logger.info(f'{d.title} {url}')
    write(p['email'], into='ID/携帯電話番号/メールアドレス')
    logger.info('ID/携帯電話番号/メールアドレス を入力しました')
    save_screenshot(d, p)
    click('次へ')
    input_password(d, p)

    url = d.current_url
    logger.info(f'{d.title} {url}')
    code = input('確認コードを入力してください -> ')
    logger.debug(code)
    write(code, into='確認コード')
    logger.info('確認コードを入力しました')
    save_screenshot(d, p)
    click('ログイン')
    d.url_changes(url)


def confirmation_email(d, p):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    '''
    try:
        d.title_is('メールアドレスを最新に！ - Yahoo! JAPAN')
    except TimeoutException:
        return
    url = d.current_url
    logger.info(f'{d.title} {url}')
    save_screenshot(d, p)
    click('確認')
    d.url_changes(url)


def yahoo_card(d, p):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    '''
    try:
        d.title_is('Yahoo! JAPANカード（年会費永年無料） - Yahoo! JAPAN')
    except TimeoutException:
        return
    url = d.current_url
    logger.info(f'{d.title} {url}')
    save_screenshot(d, p)
    click('ご利用中のサービスに戻る')
    d.url_changes(url)


def lyp_premium(d, p):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    '''
    try:
        d.title_is('LYPプレミアム - LINE・ヤフー・PayPayがもっと楽しく、もっとおトクに')
    except TimeoutException:
        return
    url = d.current_url
    logger.info(f'{d.title} {url}')
    save_screenshot(d, p)
    click('あとで')
    d.url_changes(url)


def payment_detail_list(d, p, l):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :param list l: 明細URLの格納先
    '''
    d.title_is('支払い一覧 - Yahoo!かんたん決済')

    url = d.current_url
    logger.info(f'{d.title} {url}')
    save_screenshot(d, p)
    if not p.get('target_year'):
        # 対象年・対象年月 未指定
        logger.info("今月分の明細URL収集を開始します")
        collect_detail_url(d, p, l)

    elif p['licensed'] and p.get('target_year') and p.get('target_month'):
        # 対象年・対象年月の指定あり
        select('支払い一覧', f"{p['target_year']}年{p['target_month']}月")
        logger.info(f"{p['target_year']}年{p['target_month']}月 を選択")
        save_screenshot(d, p)
        click('表示')
        d.url_changes(url)

        save_screenshot(d, p)
        logger.info(f"{p['target_year']}年{p['target_month']}月分の明細URL収集を開始します")
        collect_detail_url(d, p, l)

    elif p['licensed'] and p.get('target_year') and not p.get('target_month'):
        # 対象年のみ指定
        logger.info(f'{p["target_year"]}年分の明細URL収集を開始します')
        for i in range(12, 0, -1):
            month = f'{i:02}'
            try:
                select('支払い一覧', f"{p['target_year']}年{month}月")
                logger.info(f"{p['target_year']}年{month}月 を選択")
                click('表示')
                d.url_changes(url)

                url = d.current_url
                save_screenshot(d, p)
                collect_detail_url(d, p, l)
            except NoSuchElementException:
                continue


def collect_detail_url(d, p, l):
    '''
    :param pselenium.ChromePlus d:
    :param dict p: 設定
    :param list l: 明細URLの格納先
    :return:
    '''
    url = d.current_url
    logger.info(f'{d.title} {url}')
    for i in range(2, 12):
        try:
            elm = d.find_element_by_xpath(f'/html/body/div[2]/div/div/div[2]/div/div[1]/table/tbody/tr[{i}]/td[4]/a')
            url = elm.get_property('href')
            logger.debug(f'取得対象URL={url}')
            l.append(url)
        except NoSuchElementException:
            # ページ途中で「明細」ボタンが無くなった場合
            pass

    # TODO: 次ページの処理はあるのか？


def get_pdf(d, p, l):
    '''
    対象ページをpdf化
    :param pselenium.ChromePlus d:
    :param dict p:
    :param list l:
    :return:
    '''
    for i in l:
        d.get(i)
        url = d.current_url
        logger.info(f'{d.title} {url}')
        d.save_pdf(f"Yahoo!かんたん決済_支払明細_{d.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div[3]/ul/li[3]/dl/dd').text}.pdf")


def main(d, p):
    '''
    :param pselenium.ChromePlus d:
    :param dict p:
    :return:
    '''
    set_driver(d)
    d.set_window_size(1080, 1080)

    # 支払い一覧
    go_to('https://aucpay.yahoo.co.jp/detail-front/PaymentDetailList')
    login(d, p)

    # TODO: 未確認
    # 広告等への対処
    try:
        d.title_is('支払い一覧 - Yahoo!かんたん決済')
    except TimeoutException:
        go_to('https://aucpay.yahoo.co.jp/detail-front/PaymentDetailList')
        # confirmation_email(d, p)
        # yahoo_card(d, p)
        # lyp_premium(d, p)

    # 明細のURL収集
    l = []
    payment_detail_list(d, p, l)

    # 領収書ページをpdf化
    logger.info('明細ページを保存します')
    get_pdf(d, p, l)

    # FIXME: 受け取り一覧が必要な人は少ないと思われる
    # 受け取り一覧
    # go_to('https://aucpay.yahoo.co.jp/detail-front/ReceiveDetailList')
    # https://aucpay.yahoo.co.jp/detail-front/ReceiveDetailList?_indication=202010&_menu=3
    # javascript:document.csvdownload.submit()
    # https://aucpay.yahoo.co.jp/detail-front/ReceiveDetailItem?_settle_id=20101171614180&_menu=3&_indication=202010&_page=1
