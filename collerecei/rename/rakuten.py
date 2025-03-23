# encoding: UTF-8
# Copyright (c) sanofujiwarak.
from logging import getLogger
from os import sep, system
from platform import system as psys
import re

import pymupdf

logger = getLogger(__name__)


def copy_command():
    pf = psys()
    if pf == 'Windows':
        return 'copy'
    elif pf == 'Darwin':
        return 'cp'


def rename_pdf(filepath: str, outdir: str):
    logger.info(f'解析対象: {filepath}')
    il = []
    doc = pymupdf.open(filepath)
    for page in doc:
        text = page.get_text()
        logger.debug(text)
        # 初回領収日
        issue_date = re.search(r'初回領収日：([0-9年月日]+)\n', text, re.M)
        if issue_date:
            logger.info(f'初回領収日: {issue_date.groups()[0]}')
            il.append(re.sub('[年月日]+', '', issue_date.groups()[0]))
        # 総合計
        price = re.search(fr'総合計\n([0-9,]+)円', text, re.M)
        if price:
            logger.info(f'総合計: {price.groups()[0]}')
            il.append(price.groups()[0].replace(',', ''))
        # 領収者
        issuer = re.search(r'領収者：(.+)\n', text, re.M)
        if issuer:
            logger.info(f'領収者: {issuer.groups()[0]}')
            il.append(issuer.groups()[0])

    logger.debug(il)
    if len(il) == 3:
        filename = f'{il[0]}_{il[1]}_{il[2]}.pdf'
        cmd = f'{copy_command()} "{filepath.replace("/", sep)}" "{outdir.replace("/", sep)}{sep}{filename}"'
        logger.debug(cmd)
        system(cmd)
