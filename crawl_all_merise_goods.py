

from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
import sys
from get_category_url import fetch
import os


"""

クローリング作業全体の概要

1 amazonホームページのカテゴリーページのハイパーリンクをスクレイピング　　get_category_url.py　　　　　　　　　

2 ドラッグストア・ビューティーからおむつ・おしりふきのハイパーリンクをスクレイピング  get_diaper_url.py     

3 ベビーケア・おむつからおむつのハイパーリンクをスクレイピング  get_diaper_url2.py    

4 おむつからメリーズのハイパーリンクをスクレイピング  get_merise_url.py   

5 メリーズ全69件の商品のpageをcrawling  crawl_all_merise_goods.py    ◀◀◀◀◀　今ここ

6 全69件に対応するすべてのカスタマーレビューを取得     crawl_all_review.py   

7 S3にcrawlingした全ページを保存      crawl_all_review.py                


"""


def main():

    sys.stdout = open("./text/all_merise_goods_url.txt", "w")
    base_url = 'https://www.amazon.co.jp/'
    category = open("./text/merise.txt", "r").read()
    html = fetch(category)
    all_url = scrape(html)

    all_goods_url = []
    for i in all_url:
        all_goods_url.append(i)
    a = get_all_goods_pages_link(html, base_url)
    for i in a:
        html = fetch(i)
        all_url = scrape(html)
        for i in all_url:
            all_goods_url.append(i)
    for i in all_goods_url:
        print(i)

    sys.stdout.close()
    sys.stdout = sys.__stdout__


def scrape(html):
    """
    引数htmlで与えられたhtml(おむつpage)からメリーズ全69件の商品のページ(html形式)およびURLを取得
    :param html:　メリーズ商品ページをhtml形式で保持
    :return: str型でメリーズ全68件の商品のページ(html形式)およびURL
    """
    url = []
    doc = soup(html, "html.parser")
    tex = doc.findAll("a", class_="a-link-normal a-text-normal")
    for i in tex:
        # 商品のパスを取得
        goods_path = i.attrs['href']
        # 商品のURLに重複があれば消す
        for u in range(len(url)):
            if goods_path == url[u]:
                del url[u]
        # 商品のパスが絶対パスのもののみ取得(商品ヘルプページを取り除く)
        if os.path.isabs(goods_path):
            pass
        else:
            url.append(goods_path)
    return url


def get_all_goods_pages_link(html, base_url):
    """
    全ての商品ページのリンクをリストとして取得する
    :param html:
    :param base_url:
    :return:
    """
    all_goods_url = []
    doc = soup(html, "html.parser")
    tex = doc.find_all("span", class_="pagnLink")
    for i in tex:
        all_goods_url.append(urljoin(base_url, i.a['href']))
    return all_goods_url


if __name__ == '__main__':

    main()
