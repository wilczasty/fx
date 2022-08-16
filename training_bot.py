from fx_trainer import ForexTrainer
from mkt_data import MarketData
from trader import Trader
import datamanager as dm
PAIR = "EURUSD"
TIMEFRAME = "D1"
DEFAULT_SPREAD = 0.0003
STRATEGY_TO_TRAIN = 1658999477


def main():
    market = MarketData(pair=PAIR, timeframe=TIMEFRAME, spread = DEFAULT_SPREAD)
    strategy = dm.get_strategy(STRATEGY_TO_TRAIN)
    dm.set_inputs(strategy.input_count)
    trader = Trader(threshold=0.6, direction=1)
    trader.set_market(market)
    trader.set_strategy(strategy)
    gym = ForexTrainer(trader=trader, gen_count=10000, multithread=True, thread_count = 4)
    gym.train_network()

if __name__ == "__main__":
    main()
