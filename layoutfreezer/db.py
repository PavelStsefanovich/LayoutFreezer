import logging
import sqlite3


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Classes  ##############################

class Database:

    def __init__(self, db_path):
        # connect to database
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.create()

    def create(self):
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

    def delete(self, dl_hash=None, name=None, title=None, rect=None, index=None, orientation=None, logical_operator='AND'):
        bindings = []
        query_operator = 'WHERE'
        query = "DELETE FROM apps"
        if dl_hash:
            query += f'\n{query_operator} display_layout_hash=?'
            query_operator = logical_operator
            bindings.append(dl_hash)
        if name:
            query += f'\n{query_operator} process_name=?'
            query_operator = logical_operator
            bindings.append(name)
        if title:
            query += f'\n{query_operator} window_title=?'
            query_operator = logical_operator
            bindings.append(title)
        if rect:
            query += f'\n{query_operator} window_rectangle=?'
            query_operator = logical_operator
            bindings.append(rect)
        if index:
            query += f'\n{query_operator} display_index=?'
            query_operator = logical_operator
            bindings.append(index)
        if orientation:
            query += f'\n{query_operator} display_orientation=?'
            query_operator = logical_operator
            bindings.append(orientation)
        if query_operator == 'WHERE':
            query += '\nWHERE display_layout_hash=?'
            bindings.append('nothing')
        self.cur.execute(query, bindings)
        self.conn.commit()

    def list_all(self):
        rows = self.search()
        return rows

    def search(self, dl_hash=None, name=None, title=None, rect=None, index=None, orientation=None, order_by=None, logical_operator='AND'):
        bindings = []
        query_operator = 'WHERE'
        query = "SELECT * FROM apps"
        if dl_hash:
            query += f'\n{query_operator} display_layout_hash=?'
            query_operator = logical_operator
            bindings.append(dl_hash)
        if name:
            query += f'\n{query_operator} process_name=?'
            query_operator = logical_operator
            bindings.append(name)
        if title:
            query += f'\n{query_operator} window_title=?'
            query_operator = logical_operator
            bindings.append(title)
        if rect:
            query += f'\n{query_operator} window_rectangle=?'
            query_operator = logical_operator
            bindings.append(rect)
        if index:
            query += f'\n{query_operator} display_index=?'
            query_operator = logical_operator
            bindings.append(index)
        if orientation:
            query += f'\n{query_operator} display_orientation=?'
            query_operator = logical_operator
            bindings.append(orientation)
        if order_by:
            query += f'\n ORDER BY {order_by}'
        self.cur.execute(query, bindings)
        rows = self.cur.fetchall()
        return rows

    def clear(self, table_name='apps'):
        self.cur.execute("DROP TABLE IF EXISTS apps")
        self.conn.commit()
        self.create()

    def __del__(self):
        self.conn.close()


##########  Main  #################################
if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
