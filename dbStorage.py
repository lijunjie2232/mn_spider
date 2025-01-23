import sqlite3

# (id:auto_increase, url:str)
PAGE_TABLE = """
CREATE TABLE IF NOT EXISTS page (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    page_ctx TEXT DEFAULT NULL
)
"""


# (type:int, tag:str, index:str, setence:str, url:str)
INDEX_TABLE = """
CREATE TABLE IF NOT EXISTS index_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type INTEGER NOT NULL,
    tag TEXT NOT NULL,
    idx TEXT NOT NULL,
    grammar TEXT NOT NULL,
    url TEXT NOT NULL
)
"""


class DBStorage:
    def __init__(self, db_name="ja_gramma.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def _create_tables(self):
        PAGE_TABLE = """
        CREATE TABLE IF NOT EXISTS page (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            page_ctx TEXT DEFAULT NULL
        )
        """

        INDEX_TABLE = """
        CREATE TABLE IF NOT EXISTS index_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type INTEGER NOT NULL,
            tag TEXT NOT NULL,
            idx TEXT NOT NULL,
            grammar TEXT NOT NULL,
            url TEXT NOT NULL
        )
        """

        self.cursor.execute(PAGE_TABLE)
        self.cursor.execute(INDEX_TABLE)

    def _create_indexes(self):
        # 为 page 表的 url 字段创建索引
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_url ON page (url)")

        # 为 index_table 表的 url 字段创建索引
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_index_table_url ON index_table (url)"
        )

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._create_indexes()
        self.conn.commit()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

    def insert_page(self, url, page_ctx=None):
        if page_ctx:
            self.cursor.execute(
                "INSERT INTO page (url, page_ctx) VALUES (?, ?)",
                (
                    url,
                    page_ctx,
                ),
            )
        else:
            self.cursor.execute(
                "INSERT INTO page (url) VALUES (?)",
                (url,),
            )
        self.conn.commit()

    def get_pages(self, cols="*", where=""):
        self.cursor.execute(
            f"SELECT {cols} FROM page" + (f" WHERE {where}" if where else "")
        )
        return self.cursor.fetchall()

    def update_page(self, page_id, url, page_ctx):
        self.cursor.execute(
            "UPDATE page SET page_ctx=?, url=? WHERE id = ?", (page_ctx, url, page_id)
        )
        self.conn.commit()

    def delete_page(self, page_id):
        self.cursor.execute("DELETE FROM page WHERE id = ?", (page_id))
        self.conn.commit()

    def insert_index(self, type, tag, index, sentence, url):
        self.cursor.execute(
            "INSERT INTO index_table (type, tag, idx, grammar, url) VALUES (?, ?, ?, ?, ?)",
            (type, tag, index, sentence, url),
        )
        self.conn.commit()

    def get_indices(self, cols="*", where=""):

        self.cursor.execute(
            f"SELECT {cols} FROM index_table" + (f" WHERE {where}" if where else "")
        )
        return self.cursor.fetchall()

    def update_index(self, index_id, type, tag, index, sentence, url):
        self.cursor.execute(
            "UPDATE index_table SET type = ?, tag = ?, idx = ?, grammar = ?, url = ? WHERE id = ?",
            (type, tag, index, sentence, url, index_id),
        )
        self.conn.commit()

    def delete_index(self, index_id):
        self.cursor.execute("DELETE FROM index_table WHERE id = ?", (index_id,))
        self.conn.commit()


if __name__ == "__main__":
    # 连接到 SQLite 数据库（如果数据库不存在，则会自动创建）
    conn = sqlite3.connect("ja_gramma.db")
    cursor = conn.cursor()

    # 创建表
    cursor.execute(PAGE_TABLE)
    cursor.execute(INDEX_TABLE)

    # 提交事务
    conn.commit()

    # 关闭连接
    conn.close()

    print("数据库和表已成功创建")
