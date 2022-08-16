import pandas as pd
import sqlite3

MARKET_DATA_DB_PATH = "data\\db\\marketdata.db"

class MarketData():
    def __init__(self, pair, timeframe, spread = 0.0003, head = None, tail = None):
        self.spread = spread
        self.pair = pair
        self.timeframe = timeframe
        con = sqlite3.connect(MARKET_DATA_DB_PATH)
        self.data = pd.read_sql_query("SELECT * FROM ohlc WHERE pair = '{}' AND timeframe = '{}'".format(self.pair,self.timeframe), con,)
        con.close()
        if tail is not None:
            self.data = self.data.tail(tail)
        if head is not None:
            self.data = self.data.head(head)