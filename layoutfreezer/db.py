import sqlite3

class Database:

    def __init__(self, db_path):

        # connect to database
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

        # create table 'apps' if does not exist
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS apps
            (id INTEGER PRIMARY KEY,
            display_layout_hash TEXT NOT NULL,
            process_name TEXT NOT NULL,
            window_title TEXT NOT NULL,
            window_rectangle TEXT NOT NULL,
            display_index INTEGER NOT NULL,
            display_orientation TEXT NOT NULL,
            is_default BOOLEAN)""")
        self.conn.commit()


    def add(self, dl_hash=None, name=None, title=None, rect=None, index=None, orientation=None, is_default=0):
        self.cur.execute("INSERT OR REPLACE INTO apps VALUES (NULL, ?,?,?,?,?,?,?)",
                         (dl_hash, name, title, rect, index, orientation, is_default))
        self.conn.commit()


    def list_all(self):
        self.cur.execute("SELECT * FROM apps")
        rows = self.cur.fetchall()
        return rows


    def search(self, dl_hash="", name="", title="", rect="", index=-1, orientation="", order_by=""):

        query = """SELECT * FROM apps
                WHERE display_layout_hash=?
                OR process_name=?
                OR window_title=?
                OR window_rectangle=?
                OR display_index=?
                OR display_orientation=?"""

        if len(order_by) > 0:
            query += f"\n ORDER BY {order_by}"

        self.cur.execute(query, (dl_hash, name, title, rect, index, orientation))
        rows = self.cur.fetchall()
        return rows


    def clear(self, table_name='apps'):
        self.cur.execute("DROP TABLE IF EXISTS apps")
        self.conn.commit()
        self.conn.close()
        self.__init__(self.db_path)

    def __del__(self):
        self.conn.close()
