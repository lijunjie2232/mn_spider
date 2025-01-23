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

CUSTOM_CSS = """body{font-weight:400;font-family:sans-serif}img{object-fit:contain}.gray{color:#a0a0a0}.bold{font-weight:bolder;color:#e3008c}"""


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parent
    # 创建一个模型
    model_id = 1607391320

    model = genanki.Model(
        model_id,
        "card",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": " Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
        css=CUSTOM_CSS,
    )

    # 创建N个牌组
    deck_id = 2059401130
    decks = {}
    tags = [
        "Ｎ０文法",
        "Ｎ１文法",
        "Ｎ３文法",
        "Ｎ２文法",
        "Ｎ４文法",
        "Ｎ５文法",
    ]
    for idx, tag in enumerate(tags):
        decks[tag] = genanki.Deck(deck_id + idx, "JA语法::%s" % tag)

    with DBStorage() as db:
        page_index = db.get_indices(where="`type`=0")

        # 遍历文件夹中的图片
        loop = tqdm(page_index)
        for id, type, tag, index, grammary, url in loop:
            p_id, _, page_ctx = db.get_pages(where=f'`url`="{url}"')[0]
            a_ctx = """<h1>%s</h1>""" % grammary
            b_ctx = """%s""" % page_ctx
            note = genanki.Note(
                model=model,
                fields=[
                    a_ctx,
                    b_ctx,
                ],
                tags=[tag, index],
            )
            decks[tag].add_note(note)

    # 生成APKG文件
    my_package = genanki.Package([decks[tag] for tag in tags])
    my_package.write_to_file(ROOT / "mn_cards.apkg")
