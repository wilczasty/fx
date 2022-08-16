from datetime import datetime
import pickle
import sqlite3
import configparser

from results import TradingResultsMngr

DATA_PATH = "data//db//data.db"
CONFIG_PATH = "configs//config"
CHART_PATH = "data//charts//"
EXCEL_PATH = "data//excel_analysis//"
BRAIN_STORE_PATH = "data//brains//"
STRATEGY_STORE_PATH = "data//strategies//"
ACTIVITY_FACTOR = 70

def get_timestamp():
    return str(int(datetime.timestamp(datetime.now())))

def list_all_saved_brains():
    pass

def store_brain(brain, strategy_id, threshold, direction):
    brain_filename = store(obj=brain, path=BRAIN_STORE_PATH,addtimestamp=True)
    sql_execute(DATA_PATH,"INSERT OR REPLACE INTO brains (id,strategy_id, threshold, direction) VALUES (?, ?, ?, ?);", [brain_filename, strategy_id, threshold, direction])
    return brain_filename

def store_strategy(strategy, data, filename = ""):
    sql_execute(DATA_PATH,"INSERT OR IGNORE INTO strategies (id,name,description) VALUES (?, ?, ?);", data)
    timestamp = filename == ""
    return store(obj=strategy, path=STRATEGY_STORE_PATH, filename = filename, addtimestamp=timestamp)

def get_brain(brain_id):
    source = open(BRAIN_STORE_PATH + str(brain_id),'rb')
    brain = pickle.load(source)
    source.close()
    return brain, get_strategy_id(brain_id)

def get_strategy_id(brain_id):
    connection = get_sql_connection(DATA_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT strategy_id FROM brains WHERE id='{}'".format(brain_id))
    return cursor.fetchone()[0]

def get_strategy(strategy_id):
    source = open(STRATEGY_STORE_PATH + str(strategy_id),'rb')
    strategy = pickle.load(source)
    source.close()
    return strategy

def store(obj, path, filename = "", addtimestamp = True):
    if addtimestamp: filename = filename + get_timestamp()
    destination = open(path + filename,"wb")
    pickle.dump(obj,destination)
    destination.close()
    return filename

def sql_execute(path, sql, data):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute(sql, data)
    con.commit()
    con.close()

def sql_executemany(path, sql, data):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executemany(sql, data)
    con.commit()
    con.close()

def get_sql_connection(path):
    connection = sqlite3.connect(path)
    return connection

def store_trades_in_db(results: TradingResultsMngr):
    con = sqlite3.connect(DATA_PATH)
    cur = con.cursor()
    cur.execute
    to_db = [
        (
            results.brain_id, results.security, results.timeframe, trade["direction"],
            trade["open_date"], trade["open_price"], trade["close_date"], trade["close_price"], trade["realized"]
        ) for trade in results.trades]
    cur.execute("DELETE FROM trades WHERE id='{}' AND pair='{}' AND timeframe='{}'".format(results.brain_id,results.security,results.timeframe))
    con.commit()
    cur.executemany("""INSERT OR IGNORE INTO trades (id,pair,timeframe,direction,open_date,open_price,close_date,close_price,result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""", to_db)
    con.commit()
    con.close()

def store_stats_in_db(statistics):
    store_in_db(DATA_PATH,"statistics",statistics)

def store_in_db(path:str, table:str, dictionary:dict):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute
    cur.execute(get_insertreplace_from_dict(table,dictionary), list(dictionary.values()))
    con.commit()
    con.close()

def get_insertreplace_from_dict(table_name:str, dictionary:dict)->str:
    fields = ','.join(list(dictionary.keys()))
    qmarks = ','.join([x for x in len(dictionary) * "?"])
    sql_string = """INSERT OR REPLACE INTO {} ({})
        VALUES ({});""".format(table_name,fields,qmarks)
    return sql_string

def set_inputs(num_of_inputs):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config.set("DefaultGenome","num_inputs",str(num_of_inputs))
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
