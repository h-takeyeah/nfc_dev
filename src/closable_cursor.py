#!/bin/usr/env python3

class ClosableCursor:
    def __init__(self, connector):
        self.connector = connector
        self.cur = None

    def __enter__(self):
        self.cur = self.connector.cursor()
        return self.cur

    def __exit__(self, exception_type, exception_value, traceback):
        self.cur.close()

