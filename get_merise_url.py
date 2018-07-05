
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
import sys
from get_category_url import fetch


"""

クローリング作業全体の概要

1 amazonホームページのカテゴリーページのハイパーリンクをスクレイピング　　get_category_url.py　　　　　　　　　

2 ドラッグストア・ビューティーからおむつ・おしりふきのハイパーリンクをスクレイピング  get_diaper_url.py     

3 ベビーケア・おむつからおむつのハイパーリンクをスクレイピング  get_diaper_url2.py    

4 おむつからメリーズのハイパーリンクをスクレイピング  get_merise_url.py   ◀◀◀◀◀　今ここ  

5 メリーズ全69件の商品のpageをcrawling  crawl_all_merise_goods.py   

6 全69件に対応するすべてのカスタマーレビューを取得     crawl_all_review.py   

7 S3にcrawlingした全ページを保存      crawl_all_review.py                


"""


def main():

    # 標準出力からメリーズのハイパーリンクをtxt形式で取得
    sys.stdout = open("./text/merise.txt", "w")
    base_url = 'https://www.amazon.co.jp/'
    category = open("./text/diaper2.txt", "r").read()
    html = fetch(category)
    all_html = scrape(html, base_url)
    print(all_html)
    sys.stdout.close()
    sys.stdout = sys.__stdout__


def scrape(html, base_url):
    """
    引数htmlで与えられたhtmlからおむつ項目に属す、メリーズ項目のハイパーリンクを取得
    :param html:　べビーケア・おむつ内容をstr形式で保持
    :param base_url: amazonのホームページURL
    :return: str型でメリーズ項目のハイパーリンク
    """
    doc = soup(html, "html.parser")
    tex = doc.findAll("a")
    diaper_url = 0
    for t in tex:
        if t.text == "メリーズ":
            diaper_url = t.attrs['href']
    # 取得した相対URLを絶対URLに変形
    category_page_url = urljoin(base_url, diaper_url)

    return category_page_url


if __name__ == '__main__':

    main()
