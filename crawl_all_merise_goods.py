

from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
import sys
from get_category_url import fetch
import os
from urllib.parse import quote
import time


"""


5 メリーズ全69件の商品のpageをcrawling  crawl_all_merise_goods.py    ◀◀◀◀◀　今ここ

6 全69件に対応するすべてのカスタマーレビューを取得     crawl_all_review.py   


"""


def main():

    sys.stdout = open("./text/all_goods_url.txt", "w")
    base_url = 'https://www.amazon.co.jp/'

    category = open("./text/diaper.txt", "r").read()

    #category = 'https://www.amazon.co.jp/b/?ie=UTF8&node=170040011&ref_=sv_jpallbtn_1'
    category = 'https://www.amazon.co.jp/%E3%83%9C%E3%83%87%E3%82%A3%E3%82%B1%E3%82%A2-%E3%82%AB%E3%83%86%E3%82%B4%E3%83%AA%E3%83%BC%E5%88%A5/b/ref=sv_jpallbtn_3?ie=UTF8&node=170267011'
    html = fetch(category)
    get_all_goods_review_pages_url(html, base_url)

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
    a_tabs = doc.findAll("a", class_="a-link-normal a-text-normal")
    for a_tab in a_tabs:
        if hasattr(a_tab, "attrs"):
            # 商品のパスを取得
            goods_path = a_tab.attrs['href']
            # 商品のURLに重複があれば消す
            for i in range(len(url)):
                if goods_path == url[i]:
                    del url[i]
            # 商品のパスが絶対パスのもののみ取得(商品ヘルプページを取り除く)  絶対パスの場合=False
            if os.path.isabs(goods_path):
                pass
            else:
                url.append(goods_path)
    return url


def scrape_next_button(html, base_url):

    doc = soup(html, "html.parser")
    div = doc.find("div", id="pagn")

    if div is not None:
        # "次へ"ボタンのa_tabを取得
        next_a_tab = 0
        for a in div.find_all("a"):
            next_a_tab = a
        abs_path = urljoin(base_url, quote(next_a_tab.attrs['href'].encode("utf-8")))
        return abs_path, div

    else:
        return None, None


def get_all_goods_review_pages_url(html, base_rul):

    all_url = []
    while True:
        time.sleep(3)
        abs_path, div = scrape_next_button(html, base_rul)
        if abs_path is not None and div is not None:
            html = fetch(abs_path)
            urls = scrape(html)
            all_url.append(urls)
            for url in urls:
                print(url)

            if div.find_all("li", class_="a-disabled a-last"):
                break
        else:
            break
    return all_url


if __name__ == '__main__':

    main()
