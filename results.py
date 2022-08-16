import numpy as np
import pandas as pd

class TradingResultsMngr():
    """Manage collection, storage and output of trading results"""
    def __init__(self, fitness_calc = None, spread = 0):
        self.calculation_function = fitness_calc
        if fitness_calc is None: self.calculation_function = self.default_fitness_func
        self.spread = spread
        self.brain_id = ""
        self.strategy_id = ""
        self.timeframe = ""
        self.security = ""
        self.trades = []
        self.realized = None
        
    def open_trade(self, open_date, open_price, direction):
        self.trade = {}
        self.trade.update(open_date=open_date, open_price=open_price, direction=direction)

    def close_trade(self, close_date, close_price):
        if len(self.trade) == 0:
            print("Cannot close trade")
        else:
            self.trade.update(close_date=close_date, close_price=close_price)
            trade_realized = ((self.trade['close_price'] - self.trade['open_price']) * self.trade['direction']) - self.spread
            self.trade.update(realized=trade_realized)
            self.trades.append(self.trade)

    def get_realized(self)->list:
        """Create and store list of realized values"""
        return [item['realized'] for item in self.trades]

    def get_trading_fitness(self) -> float:
        """Calculate single number to act as fitness for trading"""
        self.get_realized()
        return self.calculation_function(self.get_stats())

    def get_stats(self)->dict:
        realized = self.get_realized()
        realized_y = [x for x in range(1,len(realized)+1)]

        total_realized = sum(realized)
        gains = [value for value in realized if value >= 0]
        losses = [value for value in realized if value < 0]

        if len(gains) == 0: average_win = 0
        else: average_win = sum(gains) / len(gains)

        if len(losses) == 0: average_loss = 0
        else: average_loss = sum(losses) / len(losses)

        if total_realized == 0: stdev, maxdd = [0,0]
        else:
            stdev = np.std(realized)
            cumsum = np.cumsum(realized)
            correlation_matrix  = np.corrcoef(cumsum,realized_y)
            r_squared = correlation_matrix[0,1]**2
            df = pd.DataFrame(cumsum, columns=['Cumsum'])
            dd = df['Cumsum'] - df['Cumsum'].cummax()
            maxdd = dd.min()
        stat_dict = {
            "id":self.brain_id,
            "strategy":self.strategy_id,
            "pair":self.security,
            "timeframe":self.timeframe,
            "wins":len(gains),
            "losses":len(losses),
            "avg_gain":average_win,
            "avg_loss":average_loss,
            "std":stdev,
            "mdd":maxdd,
            "rsq":r_squared,
            "realized":total_realized
        }
        return stat_dict

    def new_resultset(self):
        self.trades = []

    def default_fitness_func(self, stats = None):
        return sum(self.get_realized())

def calculate_mdd_recovery(stats):
    avg_trade_result = stats["realized"] / (stats["wins"]+stats["losses"])
    if avg_trade_result < 0: return -9999
    mdd = stats["mdd"]
    return -(-mdd / avg_trade_result)

def raw_profit(stats):
    return stats["realized"]

def calculate_profit_factor(stats):
    win_rate = stats["wins"] / (stats["wins"]+stats["losses"])
    if stats["avg_gain"] == 0 or stats["mdd"] == 0: return -999
    profit_factor = (win_rate + ((1-win_rate) * (stats["avg_loss"] / stats["avg_gain"])))
    return profit_factor / -stats["mdd"]