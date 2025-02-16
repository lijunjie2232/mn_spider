import requests
import re
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
import os
from GrammarPage import UA, PROXIES

THREAD_NUM = 32
MUSIC_PATTERN = re.compile(
    r"<a class=\"sounds\" data-file=\"(.*?)\" href=\"#\">▶</a>",
)


class soundSpider:
    def __init__(self, db_storage, out_dir):
        self.db_storage = db_storage
        self.out_dir = out_dir

    def process_page(self, ctx):
        ctx = ctx[0]
        sounds = MUSIC_PATTERN.findall(ctx)
        for sound in sounds:
            url = f"{sound}.mp3"
            file_name = os.path.basename(url)
            if (self.out_dir / file_name).is_file():
                continue
            try:
                r = requests.get(
                    url,
                    headers={
                        "User-Agent": UA,
                    },
                    proxies=PROXIES,
                    timeout=100000,
                )
                assert r.status_code == 200
                with open(self.out_dir / file_name, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                print(e)
        return 0

    def iterate_pages(self):
        pages = self.db_storage.get_pages(
            cols="page_ctx",
            where="page_ctx is not null",
        )
        total_pages = len(pages)

        with ThreadPool(THREAD_NUM) as POOL:
            results = POOL.imap(self.process_page, pages)
            for _ in tqdm(results, total=total_pages):
                pass


if __name__ == "__main__":
    from dbStorage import DBStorage
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent
    OUT_DIR = ROOT / "res"
    with DBStorage() as db:

        processor = soundSpider(db, OUT_DIR)
        processor.iterate_pages()
