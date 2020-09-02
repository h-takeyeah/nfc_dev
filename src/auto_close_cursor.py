class AutoCloseCursor:
    """カーソルのラッパー
        withが使えるのでclose()し忘れなくなる。
        でも(入退室管理で使う場合は)connectionの方は繋ぎっぱなしだから
        そんなに省エネでもないのかも
        参考サイト
            https://a-zumi.net/mysql-connector-python-wrapper/
            https://qrunch.net/@opqrstuvcut/entries/oLWzzM3dwG5R4Z0p
    Attributes
    ----------
        connector : mysql.connector.connection.MySQLConnection
        cur : mysql.connector.cursor.MySQLCursor

    """
    def __init__(self, connector):
        self.connector = connector
        self.cur = None

    def __enter__(self):
        self.cur = self.connector.cursor()
        return self.cur

    def __exit__(self, exception_type, exception_value, traceback):
        self.cur.close()

