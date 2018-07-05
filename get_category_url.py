

import urllib.request
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
import sys

import requests


"""

クローリング作業全体の概要

1 amazonホームページのカテゴリーページのハイパーリンクをスクレイピング　　get_category_url.py　　　 ◀◀◀◀◀　今ここ 　　　

2 ドラッグストア・ビューティーからおむつ・おしりふきのハイパーリンクをスクレイピング  get_diaper_url.py         

3 ベビーケア・おむつからおむつのハイパーリンクをスクレイピング  get_diaper_url2.py    

4 おむつからメリーズのハイパーリンクをスクレイピング  get_merise_url.py    

5 メリーズ全69件の商品のpageをcrawling  crawl_all_merise_goods.py   

6 全69件に対応するすべてのカスタマーレビューを取得     crawl_all_review.py   

7 S3にcrawlingした全ページを保存      crawl_all_review.py                


"""


def main():

    # 標準出力(amazonホームページのカテゴリーページハイパーリンク)をtxt形式で保存するファイルを用意
    #sys.stdout = open("./text/category.txt", "w")
    base_url = 'https://www.amazon.co.jp/'
    html = fetch(base_url)
    category_page_url = scrape(html, base_url)
    print(category_page_url)
    #sys.stdout.close()
    #sys.stdout = sys.__stdout__


def fetch(base_url):
    """
    引数urlで与えられたURLのwebページをhtml形式で取得する
    WebページのエンコーディングはContent-Typeヘッダーより取得する
    :param base_url:　amazonのホームページurl
    :return: str型のamazonのホームページのカテゴリーページURL
    """

    # User-Agentの問題で(HTTPError: HTTP Error 503: Forbidden)と出力されたためUser-Agentヘッダーの値をFirefoxに偽装
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
    request = urllib.request.Request(url=base_url, headers=headers)
    response = urllib.request.urlopen(request)

    # Httpヘッダーよりエンコーディングを取得する(明示されていない場合はutf-8をしていする)
    encoding = response.info().get_content_charset(failobj='utf-8')

    # デコードしてhtml形式のamazonホームページコードを取得
    html = response.read().decode(encoding)

    return html


def scrape(html, base_url):
    """
    引数htmlで与えられたhtmlから全商品カテゴリー項目のハイパーリンクを取得
    :param html:　amazonのホームページ内容をstr形式で保持
    :param base_url: amazonのホームページURL
    :return: str型でamazonの商品カテゴリーページのハイパーリンク
    """

    doc = soup(html, "html.parser")

    # amazonのホームページにおいて、main-nav-barにあるハイパーリンク"カテゴリ"URLを取得
    category_url = doc.find(id="nav-link-shopall").attrs['href']

    # 取得した相対URLを絶対URLに変形
    category_page_url = urljoin(base_url, category_url)
    return category_page_url


if __name__ == '__main__':

    main()

