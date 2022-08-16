from strategy import Strategy
from mkt_data import MarketData
from results import TradingResultsMngr, calculate_profit_factor, calculate_mdd_recovery, raw_profit
import datamanager as dm

CURRENT_STORE_THRESHOLD = 0.01

class Trader():
    def __init__(self, threshold, direction):
        self.curr_brain_name = ""
        self.strategy = None
        self.market = None
        self.brain_id = None
        self.threshold = threshold
        self.direction = direction
        self.enrich_data()
        self.results = TradingResultsMngr(fitness_calc=raw_profit) #calculate_profit_factor

    def set_brain(self, brain_id):
        self.brain, strategy_id = dm.get_brain(brain_id)
        if self.strategy.id != strategy_id:
            self.strategy = dm.get_strategy(strategy_id)

    def set_strategy(self, strategy: Strategy):
        """Set strategy for current trading/training"""
        self.strategy = strategy
        self.results.strategy_id = self.strategy.name
        self.enrich_data()

    def set_market(self, market: MarketData):
        """Set market object for current trading/training"""
        self.market = market
        self.enrich_data()
        self.results.spread = self.market.spread
        self.results.security = self.market.pair
        self.results.timeframe = self.market.timeframe

    def enrich_data(self):
        """Add datapoints used in strategy to market dataframe"""
        if self.strategy is not None and self.market is not None:
            self.enriched_data = self.strategy.add_datapoints(self.market.data)

    def make_decision(self, input):
        """Return output(decisions) from neural network based on input"""
        decisions = self.brain.activate(input)
        return [x > self.threshold for x in decisions]

    def trade(self, export_stats = False, export_trades = False, training_mode = False):
        """Make trading decisions on market dataframe and gather results"""
        self.results.new_resultset()
        self.results.brain_id = self.brain_id                             
        is_trade_open = False
        data_dict = self.enriched_data.to_dict('records')
        for row in data_dict:
            open_trade, close_trade = self.make_decision(row['Input'])
            if (open_trade == True) and (is_trade_open == False):
                is_trade_open = True
                self.results.open_trade(open_date = row['Date'], open_price=row['OpenShift'], direction=self.direction)
                continue
            if (close_trade == True) and (is_trade_open == True):
                is_trade_open = False
                self.results.close_trade(close_date=row['Date'], close_price=row['OpenShift'])

        """Networks with too low activity are punished"""
        if len(self.results.trades) < len(self.enriched_data) / dm.ACTIVITY_FACTOR: return -999

        if export_stats: dm.store_stats_in_db()
        if export_trades: dm.store_trades_in_db()
        score = self.results.get_trading_fitness()
        if score > CURRENT_STORE_THRESHOLD and training_mode:
            stats = self.results.get_stats()
            if stats['rsq'] > 0.85:
                brain_name = dm.store_brain(self.brain,self.strategy.name,self.threshold,self.direction)
                self.results.brain_id = brain_name
                stats['id'] = brain_name
                dm.store_stats_in_db(stats)
                dm.store_trades_in_db(self.results)
                print("Brain saved with score {} and rsq {}".format(score,stats['rsq']))
        return score