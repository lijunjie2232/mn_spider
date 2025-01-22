from GrammarPage import GrammarPage
from tqdm import tqdm
from multiprocessing.pool import ThreadPool

THREAD_NUM = 16


class urlSpider:
    def __init__(self, db_storage):
        self.db_storage = db_storage

    def process_page(self, row):
        page_id, url = row
        try:
            gp = GrammarPage(url)
            purePage = gp.purage()
            return page_id, url, purePage
        except Exception as e:
            print(f"Error processing page {url}: {e}")
            return None

    def iterate_pages(self):
        pages = self.db_storage.get_pages(cols="id,url", where="page_ctx is null")
        total_pages = len(pages)

        with ThreadPool(THREAD_NUM) as POOL:
            results = POOL.imap(self.process_page, pages)
            for result in tqdm(results, total=total_pages):
                if result:
                    page_id, url, purePage = result
                    self.db_storage.update_page(page_id, url, purePage)


if __name__ == "__main__":
    from dbStorage import DBStorage

    with DBStorage() as db:

        processor = urlSpider(db)
        processor.iterate_pages()
