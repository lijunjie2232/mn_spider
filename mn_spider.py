import requests
import re
from pathlib import Path
import os
import shutil
from lxml import html, etree
from tqdm import tqdm

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"


ONN_JUN_TEXT = "五十音順"
LEVEL_JUN_TEXT = "レベル順"
KEIGO_TEXT = "敬語"

PROXIES = {"http": "socks5://127.0.0.1:7890", "https": "socks5://127.0.0.1:7890"}


def p_content_parse(p: html.HtmlElement):
    text = etree.tostring(p, encoding="unicode", method="html")
    text = re.sub(r"[\n\u3000]", "", text)
    text = re.sub(r"^<p>", "", text)
    text = re.sub(r"</p>$", "", text)
    node_list = text.split("<br>")

    extracted_items = []
    for item in tqdm(node_list, desc="parse p tag", leave=False):
        match = re.search(
            r"<span.*?>【(.*?)】</span>(.*?)<a.*?href=\"(.*?)\".*?>(.*?)</a>", item
        )
        if not match:
            print(item)
            continue
        tag = match.group(1)
        index = match.group(2)
        url = match.group(3)
        grammar = match.group(4)
        extracted_items.append((tag, index, grammar, url))

    return extracted_items


def main_page_parse(url):
    response = requests.get(
        url,
        headers={
            "User-Agent": UA,
        },
        proxies=PROXIES,
    ).text
    tree = html.fromstring(response)
    elements = tree.xpath(
        '//*[@id="main_content"]/div/div/*'
    )  # 使用xpath解析子节点列表

    # select target child elements

    g_list = [[], [], []]
    jun_ = -1

    for element in tqdm(elements, desc="parse header"):
        if element.tag == "h2":
            if element.text in [ONN_JUN_TEXT, LEVEL_JUN_TEXT, KEIGO_TEXT]:
                jun_ += 1
        elif element.tag == "p":
            if jun_ != -1:
                content_list = p_content_parse(element)
                g_list[jun_].extend(content_list)

    return g_list  # 返回筛选后的结果


if __name__ == "__main__":
    ROOT = Path(__file__).absolute().parent
    DATA_DIR = ROOT / "data"
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    DATA_DIR.mkdir(exist_ok=True)

    url = "https://mainichi-nonbiri.com/japanese-grammar/"

    result = main_page_parse(url)

    from dbStorage import DBStorage

    # store url of each grammar page
    with DBStorage("ja_gramma.db") as db:

        urlSet = set()

        for idx, g_list_by_jun in enumerate(tqdm(result, desc="insert page index")):
            for (tag, index, sentence, url) in tqdm(g_list_by_jun,leave=False):
                db.insert_index(idx, tag, index, sentence, url)
                urlSet.add(url)
        
        for url in tqdm(urlSet, desc="insert url"):
            db.insert_page(url)
        

    pass
