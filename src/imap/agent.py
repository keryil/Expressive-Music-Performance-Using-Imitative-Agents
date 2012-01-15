'''
Created on 10 Oca 2012

@author: Kerem
'''
from midiutil.MidiFile import MIDIFile
from tools import log
from tools.analysis import rules

class Agent(object):
    '''
    classdocs
    '''
    performance = None
    __id = None
    __weight_tempo = None
    __weight_loudness = None
    __weight_tempo_rules = None
    __weight_loudness_rules = None
    __logger = None
    
    def __init__(self, id, weight_tempo, weight_loudness, weight_tempo_rules, weight_loudness_rules, performance):
        '''
        Constructor
        '''
        # check if tempo and loudness weights sum up to 1
        assert 1 - (weight_loudness + weight_tempo) < 0.001
        self.performance = performance
        self.__id = id
        self.__logger = log.get_agent_logger(__name__, id)
        self.__weight_loudness = weight_loudness
        self.__weight_loudness_rules = weight_loudness_rules
        self.__weight_tempo = weight_tempo
        self.__weight_tempo_rules = weight_tempo_rules
#        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
        
    def getId(self):
        return self.__id
    
    def perform(self):
        self.__logger.debug("Performing")
        return self.performance
    
    def listen(self, performance, rule1_tempo, rule1_loudness, rule2, rule3, rule4_tempo, rule4_loudness, rule5):
        self.__logger.debug("Listening")
        print self.evaluate(rule1_tempo, rule1_loudness, rule2, rule3, rule4_tempo, rule4_loudness, rule5)
    
    
    def __evaluate_loudness(self,rule1_loudness, rule3, rule4_loudness):
        return self.__weight_loudness_rules["rule1"] * rule1_loudness + \
            self.__weight_loudness_rules["rule3"] * rule3 + \
            self.__weight_loudness_rules["rule4"] * rule4_loudness
        


    def __evaluate_tempo(self,rule1_tempo, rule2, rule4_tempo, rule5):
        return self.__weight_tempo_rules["rule1"] * rule1_tempo + \
                self.__weight_tempo_rules["rule2"] * rule2 + \
                self.__weight_tempo_rules["rule4"] * rule4_tempo + \
                self.__weight_tempo_rules["rule5"] * rule5

    def evaluate(self,rule1_tempo, rule1_loudness, rule2, rule3, rule4_tempo, rule4_loudness, rule5):
        self.__logger.debug("Evaluating")
        return self.__evaluate_tempo(rule1_tempo, rule2, rule4_tempo, rule5) * \
            self.__weight_tempo + self.__evaluate_loudness(rule1_loudness, rule3, rule4_loudness) * (1-self.__weight_loudness)
    
#    def __debug(self, message):
#        self.__logger.debug("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
#    
#    def __info(self, message):
#        self.__logger.info("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
        