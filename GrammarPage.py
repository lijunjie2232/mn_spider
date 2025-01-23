import requests
import re
from bs4 import Comment
from pageParser import pageParser
import json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

PROXIES = {"http": "socks5://127.0.0.1:7890", "https": "socks5://127.0.0.1:7890"}


class GrammarPage:
    custom_style = """body{font-weight:400;font-family:sans-serif}.gray{color:#a0a0a0}.bold{font-weight:bolder;color:#fd79a8}"""

    def __init__(self, url, config="template.json", styled=False):
        self.styled = styled
        self.load_config(config)

        self.page = requests.get(
            url,
            headers={
                "User-Agent": UA,
            },
            proxies=PROXIES,
        ).text

        self.purePage = None


    def load_config(self, config="template.json"):
        with open(config, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            return self.config

    def purage(self):
        purePage = pageParser(self.page, self.config)
        if self.custom_style and self.styled:
            # 检查是否存在 <head> 标签
            if not purePage.head:
                # 创建 <head> 标签
                head_tag = purePage.new_tag("head")
                purePage.html.insert(0, head_tag)
                # 检查是否存在 <style> 标签
            style_tag = purePage.new_tag("style")
            style_tag.string = self.custom_style
            purePage.head.append(style_tag)
        for comment in purePage.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        # page = str(purePage)
        page = str(purePage.body.div.div.main)
        # page = re.sub(r"[\n\u3000]", "", page)
        page = re.sub(r"[\n]", "", page)
        page = re.sub(r"[\u3000]", "&nbsp;&nbsp;", page)
        self.purePage = page
        return self.purePage


if __name__ == "__main__":

    url = "https://mainichi-nonbiri.com/grammar/n3-uchiga/"

    gp = GrammarPage(url)
    purePage = gp.purage()

    with open("modified_html0.html", "w", encoding="utf-8") as f:
        f.write(purePage)
