

from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
from urllib.parse import quote

import os
import time
import re

from fake_useragent import UserAgent
import requests

BASEURL = 'https://www.amazon.co.jp/' # アマゾンホームページ
GOODSNAME = "body_care" # クローリングする商品名(ローカルに保存するディレクトリ名)


"""
6 ファイルに保存された全商品に対応するすべてのカスタマーレビューをクローリング      crawl_all_review.py  
"""


def fetch(url):
    """
    引数urlで与えられたURLのwebページをhtml形式で取得する
    WebページのエンコーディングはContent-Typeヘッダーより取得する
    :param url:　amazonのホームページurl
    :return: str型のamazonのホームページのカテゴリーページURL
    """
    # urlがbyte文字列の場合utf-8にdecodeしておく
    if type(url) == bytes:
        url = url.decode("utf-8")

    # 複数回のクローリングを実行するとアマゾンのサーバーから拒絶されたためUser-Agentヘッダーの値を偽造
    UA = UserAgent()
    ua = UA.safari

    # スマホページからのアクセスをカット
    if "(iPad;" in ua:
        # uaをアップデート
        ua = UA.safari
    else:
        pass

    headers = {'User-Agent': ua}

    r = requests.get(url, headers=headers)

    # ステータスコードを確認しresponseが成功しているか確認する
    if not r.status_code == 200:
        print("response.status_code is not 200")
        return None

    r.encoding = r.apparent_encoding

    """
    request = urllib.request.Request(url=base_url, headers=headers)
    response = urllib.request.urlopen(request)

    # Httpヘッダーよりエンコーディングを取得する(明示されていない場合はutf-8をしていする)
    encoding = response.info().get_content_charset(failobj='utf-8')

    # デコードしてhtml形式のamazonホームページコードを取得
    html = response.read().decode(encoding)
    """

    return r.text


def scrape(html, base_url):
    """
    ""全てのレビューページを取得する""　ボタンのハイパーリンクを取得する
    :param html: 特定の商品ページ(html形式ファイル)
    :param base_url: amazonのホームページ(urlをstr型)
    :return: 特定商品の全レビューを表示するページ(urlをstr型)
    """

    doc = soup(html, "lxml")
    if doc is not None:
        a_tab = doc.find("a", id="dp-summary-see-all-reviews")
        try:
            if hasattr(a_tab, "attrs"):
                # pathは相対パスで保存されているので絶対パスに変換する
                abs_path = urljoin(base_url, quote(a_tab.attrs['href'].encode("utf-8")))
                return abs_path
            else:
                print("id=dp-summary-see-all-reviewsが無いようです_lxml")
        except"It' gonna be passed because this page has not a a_tab(dp-summary-see-all-reviews)":
            return None
    else:
        print("docがNoneです")


def scrape_high_and_low(html, base_url):
    """
    アマゾンにより特定商品につき高評価・低評価にリストアップされたレビューページへのハイパーリンクをリストで返す
    :param html: "全てのレビューページを取得する(1ページ目)"のページをhtml形式
    :param base_url: アマゾンのホームページ(urlをstr型)
    :return:　高評価・低評価へのハイパーリンク(list型)
    """

    high_and_low = []
    doc = soup(html, "lxml")
    if doc is not None:
        a_tabs = doc.find_all("a", class_="a-size-base a-link-normal see-all")
        for a_tab in a_tabs:

            if hasattr(a_tab, "attrs"):
                if "高評価のレビュー" in a_tab.text:
                    # pathは相対パスで保存されているので絶対パスに変換する
                    high_abs_path = urljoin(base_url, quote(a_tab.attrs['href'].encode("utf-8")))
                    high_and_low.append(high_abs_path)
                elif "低評価のレビュー" in a_tab.text:
                    # pathは相対パスで保存されているので絶対パスに変換する
                    low_abs_path = urljoin(base_url, quote(a_tab.attrs['href'].encode("utf-8")))
                    high_and_low.append(low_abs_path)

            else:
                return None

        return high_and_low

    else:
        print("docがNoneです")


def scrape_next_button(html, base_url):
    """
    商品レビューページ下部にある"次へ"ボタンのリンク(２ページ目url)を取得する
    :param html: 各商品のレビューページホーム(１ページ目)
    :param base_url: amazonホームページurl
    :return: 次のページurl(str型)
    """

    doc = soup(html, "lxml")
    div = doc.find("div", id="cm_cr-pagination_bar")

    if div is not None:
        # "次へ"ボタンのa_tabを取得
        next_a_tab = 0
        for a in div.find_all("a"):
            next_a_tab = a
        abs_path = urljoin(base_url, quote(next_a_tab.attrs['href'].encode("utf-8")))
        print(abs_path)
        return abs_path, div

    else:
        return None, None


def get_all_goods_review_pages_url(html, base_rul, products_directory):
    """
    商品レビューページを全て取得し各商品ディレクトリごとに保存する
    :param html:  各商品のレビューページホーム(１ページ目)
    :param base_rul: amazonホームページurl(str型)
    :param products_directory:　商品ディレクトリ名(str型)
    :return: None
    """

    count = 2

    # 商品レビューディレクトリにレビューページをhtml形式で保存
    with open("./reviews/review_{}/{}/{}".format(GOODSNAME, products_directory,
                                         str(0) + "1".zfill(3)) + ".html", "w") as file:
        file.write(html)

    while True:
        time.sleep(1)
        abs_path, div = scrape_next_button(html, base_rul)
        if abs_path is not None and div is not None:
            html = fetch(abs_path)
            with open("./reviews/review_{}/{}/{}".format(GOODSNAME, products_directory,
                                                 str(0)+str(count).zfill(3)) + ".html", "w") as file:
                file.write(html)
                count += 1
                if div.find_all("li", class_="a-disabled a-last"):
                    break
        else:
            break
    print("next")


def get_all_high_and_low_review(html, base_rul, products_directory, HIGH_OR_LOW_DIRECTORY):
    """
    商品レビューページを高評価および低評価ごとに全て取得し各商品ディレクトリごとに保存する
    :param html:  各商品のレビューページホーム(１ページ目)
    :param base_rul: amazonホームページurl(str型)
    :param products_directory:　商品ディレクトリ名(str型)
    :return: None
    """

    count = 2

    # 商品レビューディレクトリにレビューページをhtml形式で保存
    with open("./reviews/review_{}/{}/{}/{}".format(GOODSNAME, products_directory, HIGH_OR_LOW_DIRECTORY, str(0) + "1".zfill(3))
              + ".html", "w") as file:
        file.write(html)

    while True:
        time.sleep(1)
        abs_path, div = scrape_next_button(html, base_rul)
        if abs_path is not None and div is not None:
            html = fetch(abs_path)
            with open("./reviews/review_{}/{}/{}/{}".format(GOODSNAME, products_directory, HIGH_OR_LOW_DIRECTORY, str(0)+str(count).zfill(3))
                      + ".html", "w") as file:
                file.write(html)
                count += 1
                if div.find_all("li", class_="a-disabled a-last"):
                    break
        else:
            break
    print("=====")


def main():

    # 全てのメリーズ商品ページurlを取得する
    urls = open("./text/all_goods_url.txt", "r").readlines()
    count = 0
    for url in urls:

        # 商品ページ(html)を取得
        html = fetch(url)
        if html is None:
            html = "None"
        # 商品ページをhtml形式で保存
        goods_label = url.split("&")
        with open("./goods_html/{}".format(goods_label[-1])+".html", "w") as file:
            file.write(html)

        # ""全てのレビューページを取得する""　ボタンのハイパーリンクを取得 (レビュー１ページ目)
        url = scrape(html, BASEURL)
        if url is not None:
            # クローリング対象商品のurlを確認
            print(str(count)+" "+"url:"+url)

        # urlがbyte文字列の場合utf-8にdecodeしておく
        if type(url) == bytes:
            url = url.decode("utf-8")

        # ページレビューを保存するディレクトリを作成(レビューがある商品のみ)
        if url is not None:
            # 商品IDをurlから正規表現を利用し抜き出す
            GOODSID = re.findall('B0[A-Z0-9]{8}', url)
            os.makedirs("./reviews/review_{}/{}".format(GOODSNAME, GOODSID[0]), exist_ok=True)

            # ""全てのレビューページ""のホーム(1ページ目)をhtml形式で取得
            html_origin = fetch(url)

            if html_origin is not None:

                # アマゾンにより"高評価"および"低評価"にそれぞれリストアップされたページのハイパーリンクを取得(それぞれ1ページ目)
                high_and_low_list = scrape_high_and_low(html_origin, BASEURL)

                COUNT = 0
                for url_high_and_low in high_and_low_list:
                    DIRECTORY = 'HIGH--SCORED'
                    if COUNT == 1:
                        DIRECTORY = 'LOW--SCORED'
                    print(DIRECTORY)
                    if url_high_and_low is not None:

                        # 商品IDをurlから正規表現を利用し抜き出す
                        GOODSID = re.findall('B0[A-Z0-9]{8}', url_high_and_low)
                        os.makedirs("./reviews/review_{}/{}/{}".format(GOODSNAME, GOODSID[0], DIRECTORY), exist_ok=True)

                        # ""全てのレビューページ""のホーム(1ページ目)をhtml形式で取得
                        html = fetch(url_high_and_low)

                        if html is not None:

                            # 商品に対応する全てのレビューを高評価および低評価ごとにクローリングする
                            get_all_high_and_low_review(html, BASEURL, GOODSID[0], DIRECTORY)
                            COUNT += 1

                        else:
                            print("この商品にはアマゾンによりリスト化された高評価・低評価のレビューページがありません")
                    else:
                        print("変数のurl_high_and_lowがNoneです")
                print("ALL REVIEW")
                # 高評価・低評価にかかわらず、商品に対応する全てのレビューをクローリングする
                get_all_goods_review_pages_url(html_origin, BASEURL, GOODSID[0])
                count += 1
            else:
                print("この商品にはレビューページがありません")
        else:
            print("変数のurlがNoneです")


if __name__ == '__main__':

    main()

