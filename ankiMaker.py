# anki 批量制卡
import genanki
import os
from pathlib import Path
from tqdm import tqdm

if __name__ == "__main__":
    from dbStorage import DBStorage

# anki 批量制卡
import genanki
import os
from pathlib import Path
from tqdm import tqdm

CUSTOM_CSS = """body{font-weight:400;font-family:sans-serif}.gray{color:#a0a0a0}.bold{font-weight:bolder;color:#fd79a8}"""


if __name__ == "__main__":
    # 创建一个模型
    model_id = 1607392320
    model = genanki.Model(
        model_id,
        "Picture Card",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
        css=CUSTOM_CSS,
    )

    # 创建一个牌组
    deck_id = 2059400130
    deck = genanki.Deck(deck_id, "JA语法")

    ROOT = Path(__file__).resolve().parent

    with DBStorage() as db:
        page_index = db.get_indices(where="`type`=0")

        # 遍历文件夹中的图片
        loop = tqdm(page_index)
        for id, type, tag, index, grammary, url in loop:
            p_id, _, page_ctx = db.get_pages(where=f'`url`="{url}"')[0]
            a_ctx = """<h1>%s</h1>""" % grammary
            b_ctx = a_ctx + """<br>%s""" % page_ctx
            note = genanki.Note(
                model=model,
                fields=[
                    a_ctx,
                    b_ctx,
                ],
                tags=[tag],
            )
            deck.add_note(note)

    # 生成APKG文件
    my_package = genanki.Package(deck)
    my_package.write_to_file(ROOT / "mn_cards.apkg")
