# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger
from os import path
import re

import pymupdf

logger = getLogger(__name__)


def divide_pdf(filepath: str, outdir: str='./'):
    logger.info(f'解析対象: {filepath}')
    part = pymupdf.open()
    il = []
    from_page = None
    doc = pymupdf.open(filepath) # open a document
    p = r'￥([0-9,]+)'
    cnt = 0
    for page in doc: # iterate the document pages
        text = page.get_text()
        # 請求書発行日
        issue_date = re.search(r'請求書発行日\n([0-9\\-]+)\n', text, re.M)
        if issue_date:
            logger.info(f'請求書発行日: {issue_date.groups()[0]}')
            il.append(issue_date.groups()[0].replace('-', ''))
        # 税抜 税額 税込
        expenses = re.search(fr'合計\n{p}\n{p}\n{p}\n合計', text, re.M)
        if expenses:
            logger.info(f'価格: {expenses.groups()}')
            il.append(expenses.groups())
        # 発行者
        issuer = re.search(r'発行者 \n(.+)\n', text, re.M)
        if issuer:
            logger.info(f'発行者: {issuer.groups()[0]}')
            il.append(issuer.groups()[0])
        # ページ判定
        invoice_page = re.search(r'([0-9]+) of ([0-9]+) ページ\n', text, re.M)
        if invoice_page:
            r = invoice_page.groups()
            logger.info(f'ページ: {r}')
            if from_page is None:
                from_page = cnt
            if r[0] == r[1] and len(il) == 3:
                filename = f'{il[0]}_{il[1][2].replace(",", "")}_{il[2]}.pdf'
                part.insert_pdf(doc, from_page, cnt)
                part.save(path.join(outdir, filename))
                part.close()
                logger.info(f'{filename} を作成しました.')
                part = pymupdf.open()
                il = []
                from_page = None
        cnt += 1
