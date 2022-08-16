import neat
from datetime import datetime
from neat.reporting import BaseReporter
import time
from trader import Trader
from datamanager import CONFIG_PATH

class ForexTrainer():
    def __init__(self, trader: Trader, gen_count = None, resume = False, multithread = True, thread_count = 4):
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            CONFIG_PATH)
        self.resume = resume
        self.trader = trader
        self.thread_count = thread_count
        self.multithread = multithread
        self.gen_count = gen_count

    def train_network(self):
        population = neat.Population(self.config)
        population.add_reporter(ForexReporter()) #self.trader.strategy.id, self.trader.market.pair, self.trader.market.timeframe
        if self.multithread:
            parralel_evaluator = neat.ParallelEvaluator(self.thread_count,self.evaluate_trader)
            population.run(parralel_evaluator.evaluate,self.gen_count)
        else:
            population.run(self.evaluate_traders,self.gen_count)

    def evaluate_trader(self,genome,config):
        brain = neat.nn.FeedForwardNetwork.create(genome, self.config)
        self.trader.brain = brain
        result = self.trader.trade(training_mode=True)
        return result

    def evaluate_traders(self,genomes,config):
        for genome_id, genome in genomes:
            genome.fitness = self.evaluate_trader(genome,config)

class ForexReporter(BaseReporter):
    def __init__(self):
        self.generation = None
        self.generation_start_time = None
        self.current_best = -999999
        self.generation_times = []

    def start_generation(self, generation):
        self.generation = generation
        self.generation_start_time = time.time()

    def get_timestamp(self):
        return  str(int(datetime.timestamp(datetime.now())))

    def post_evaluate(self, config, population, species, best_genome):
        print('Result: {0:3.5f} in generation {1}'.format(best_genome.fitness, self.generation))