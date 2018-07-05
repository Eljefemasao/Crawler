

from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
from urllib.parse import quote

from get_category_url import fetch
import os

import boto3
import time

S3_BUCKET_NAME = "AllGoodsPages"


"""

クローリング作業全体の概要

1 amazonホームページのカテゴリーページのハイパーリンクをスクレイピング　　get_category_url.py　　　　　　　　　

2 ドラッグストア・ビューティーからおむつ・おしりふきのハイパーリンクをスクレイピング  get_diaper_url.py     

3 ベビーケア・おむつからおむつのハイパーリンクをスクレイピング  get_diaper_url2.py    

4 おむつからメリーズのハイパーリンクをスクレイピング  get_merise_url.py   

5 メリーズ全69件の商品ページをクローリング   crawl_all_merise_goods.py    

6 全69件に対応するすべてのカスタマーレビューをクローリング      crawl_all_review.py   ◀◀◀◀◀　今ここ

7 S3にcrawlingした全ページを保存      crawl_all_review.py                ◀◀◀◀◀　今ここ


"""


def main():

    base_url = 'https://www.amazon.co.jp/'
    # 全てのメリーズ商品ページurlを取得する
    urls = open("./text/all_merise_goods_url.txt", "r").readlines()

    for url in urls:
        # 全ての商品ページ(html)を取得
        html = fetch(url)
        # メリーズパンツ全ての商品ページをhtml形式で保存
        with open("./goods_html/sr=1-{}".format(url[-3] + url[-2])+".html", "w") as file:
            file.write(html)

        # 各商品ごとに""全てのレビューページを取得する""buttonのハイパーリンクを取得 (およそ40/70件分; 週ごとに増えてる)
        url = scrape(html, base_url)
        print(url)

        # 各商品ごとにページレビューを保存するディレクトリを作成(レビューがある商品のみ)
        if url is not None:
            splitted_path = url.split("/")
            for i in range(len(splitted_path)):
                # レピューがある商品urlより商品IDを取得
                if splitted_path[i] == "product-reviews":
                    os.makedirs("./review/{}".format(splitted_path[i+1]), exist_ok=True)

                    # ""全てのレビューページ""のホーム(1ページ目)をhtml形式で取得
                    html = fetch(url)
                    # 各商品レビューディレクトリにレビューページをhtml形式で保存
                    with open("./review/{}/{}".format(splitted_path[i+1], "1")+".html", "w") as file:
                        file.write(html)
                    if html is not None:
                        get_all_goods_review_pages_url(html, base_url, splitted_path[i+1])


def scrape(html, base_url):
    """
    引数htmlで与えられたhtml(おむつpage)からメリーズ全68件の商品のページ(html形式)およびURLを取得
    :param html:　メリーズ商品ページ形式で保持
    :param base_url: amazonのホームページURL
    :return: str型でメリーズ全68件の商品のページ(html形式)およびURL
    """

    doc = soup(html, "html.parser")
    try:
        if doc is not None:
            a_tab = doc.find("a", id="dp-summary-see-all-reviews")
            abs_path = urljoin(base_url, quote(a_tab.attrs['href'].encode("utf-8")))
            return abs_path

    except "There is no url":
        return None


def scrape_next_button(html, base_url):

    """
    各商品レビューページ下部にある"次へ"buttonのurl(２ページ目url)を取得する
    :param html: 各商品のレビューページホーム(１ページ目)
    :param base_url: amazonホームページurl
    :return: str型で次のページurl
    """

    doc = soup(html, "html.parser")
    div = doc.find("div", id="cm_cr-pagination_bar")

    if div is not None:
        # "次へ"ボタンのa_tabを取得
        next_a_tab = 0
        for a in div.find_all("a"):
            next_a_tab = a
        abs_path = urljoin(base_url, quote(next_a_tab.attrs['href'].encode("utf-8")))
        return abs_path, div

    else:
        return None


def get_all_goods_review_pages_url(html, base_rul, products_directory):
    """
    商品レビューページを全て取得し各商品ディレクトリごとに保存する
    :param html:  各商品のレビューページホーム(１ページ目)
    :param base_rul: amazonホームページurl
    :param products_directory:　商品ディレクトリ名(str型)
    :return: None
    """

    count = 2
    while True:
        time.sleep(1)
        abs_path, div = scrape_next_button(html, base_rul)
        if abs_path is not None and div is not None:
            html = fetch(abs_path)
            with open("./review/{}/{}".format(products_directory, count) + ".html", "w") as file:
                file.write(html)
                count += 1
                if div.find_all("li", class_="a-disabled a-last"):
                    break
        else:
            break
    print("next")


def stock_S3():

    # S3Bucketオブジェクトを取得する
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(S3_BUCKET_NAME)

    for i in range():

        time.sleep(2)
        # 商品ごとのURL及びhtml,reviewをS3に保存する
        bucket.put_object(Key=filename, Body=res)


if __name__ == '__main__':

    main()

