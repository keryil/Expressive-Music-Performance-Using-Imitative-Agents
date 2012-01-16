'''
Created on 10 Oca 2012

@author: Kerem
'''
from midiutil.MidiFile import MIDIFile
from tools import log
from tools.analysis import rules, key_change
#from rules import *
from tools.analysis.lbdm import getNoteGroups
from tools.analysis.metric_structure import getMetricStructure
from tools.analysis.accentuation_curve import accentuation_curve
from tools.analysis.melodic_accent import analyze_melodic_accent
from tools.analysis.rules import rule1_tempo, rule1_loudness, rule2, rule3,\
    rule4_tempo, rule4_loudness, rule5
from copy import deepcopy

class Agent(object):
    '''
    classdocs
    '''
    performance = None
    __self_evaluation = None
    __id = None
    __weight_tempo = None
    __weight_loudness = None
    __weight_tempo_rules = None
    __weight_loudness_rules = None
    __logger = None
    __learningRate = 0.1
    __nominal_tempo = None
    __nominal_volume = None
    
    def __init__(self, id, weight_tempo, weight_loudness, weight_tempo_rules, weight_loudness_rules, performance, nominal_tempo, nominal_volume, learning_rate=0.1):
        '''
        Constructor
        '''
        # check if tempo and loudness weights sum up to 1
        assert 1 - (weight_loudness + weight_tempo) < 0.001
        self.__logger = log.get_agent_logger(__name__, id)
        self.__id = id
        self.__nominal_tempo = nominal_tempo
        self.__nominal_volume = nominal_volume
        self.__weight_loudness = weight_loudness
        self.__weight_loudness_rules = deepcopy(weight_loudness_rules)
        self.__weight_tempo = weight_tempo
        self.__weight_tempo_rules = deepcopy(weight_tempo_rules)
        self.__learningRate = learning_rate
        self.performance = performance
        self.__self_evaluation = self.__listen_own(nominal_tempo, nominal_volume)
        
#        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
        
    def getId(self):
        return self.__id
    
    def perform(self):
        self.__logger.debug("Performing")
        return self.performance
    
    def __listen_own(self, nominal_tempo, nominal_volume):
        self.__logger.debug("Listening to self")
        performance = self.performance
        group_structure = getNoteGroups(performance)
        tempo_events = [(event.time, event.tempo) for event in performance.tracks[0].eventList if event.type == "tempo"]
        notes = [event for event in performance.tracks[0].eventList if event.type == "note"]
        metrical_hierarchy,metrical_scores = getMetricStructure(performance)
        keys = key_change.analyze_key_change(performance)
        accentuation = accentuation_curve(analyze_melodic_accent(performance), metrical_scores, keys, notes)
        r1_tempo, r1_loudness, r2, r3, r4_tempo, r4_loudness, r5 = \
            rule1_tempo(group_structure, nominal_tempo, tempo_events), \
            rule1_loudness(group_structure, nominal_volume), \
            rule2(group_structure, nominal_tempo, tempo_events), \
            rule3(notes, nominal_volume, accentuation), \
            rule4_tempo(notes, accentuation, nominal_tempo, tempo_events), \
            rule4_loudness(notes, accentuation, nominal_volume), \
            rule5(group_structure, nominal_tempo, tempo_events)
        return self.evaluate(r1_tempo, r1_loudness, r2, r3, r4_tempo, r4_loudness, r5)
        
    def listen(self, performance, rule1_tempo, rule1_loudness, rule2, rule3, rule4_tempo, rule4_loudness, rule5):
        self.__logger.debug("Listening")
        score = self.evaluate(rule1_tempo, rule1_loudness, rule2, rule3, rule4_tempo, rule4_loudness, rule5)
        if score > self.__self_evaluation:
            self.__logger.info("Changing performance...")
            my_notes =  [event for event in self.performance.tracks[0].eventList if event.type == "note"]
            my_tempo_events =  [(event.time, event.tempo) for event in self.performance.tracks[0].eventList if event.type == "tempo"]
            his_notes =  [event for event in performance.tracks[0].eventList if event.type == "note"]
            his_tempo_events =  [(event.time, event.tempo) for event in performance.tracks[0].eventList if event.type == "tempo"]
            for i in range(len(my_notes)):
                my_note = my_notes[i]
                his_note = his_notes[i]
                
                my_tempo = None
                for time, temp in my_tempo_events:
                    if time <= my_note.time:
                        my_tempo = temp
                    if time == my_note.time:
                        break 
                my_volume = my_note.volume
                
                his_tempo = None
                for time, temp in his_tempo_events:
                    if time <= his_note.time:
                        his_tempo = temp
                    if time == his_note.time:
                        break 
                his_volume = his_note.volume
                
                nominal_tempo = self.__nominal_tempo
                my_tempo_delta = my_tempo - nominal_tempo
                his_tempo_delta = his_tempo - nominal_tempo
                new_tempo_delta = (1-self.__learningRate) * my_tempo_delta + self.__learningRate * his_tempo_delta
                new_tempo = nominal_tempo + new_tempo_delta
                self.performance.tracks[0].addTempo(my_note.time, new_tempo)
                
                nominal_volume = self.__nominal_volume
                my_volume_delta = my_volume - nominal_volume
                his_volume_delta = his_volume - nominal_volume
                new_volume_delta = (1-self.__learningRate) * my_volume_delta + self.__learningRate * his_volume_delta
                new_volume = nominal_volume + new_volume_delta
                my_note.volume = new_volume
                
            self.__self_evaluation = self.__listen_own(nominal_tempo, nominal_volume)
        else:
            self.__logger.info("NOT changing performance...")
                
    def __evaluate_loudness(self,rule1_loudness, rule3, rule4_loudness):
        return self.__weight_loudness_rules["rule1"] * rule1_loudness + \
            self.__weight_loudness_rules["rule3"] * rule3 + \
            self.__weight_loudness_rules["rule4"] * rule4_loudness
        


    def __evaluate_tempo(self,r1_tempo, r2, r4_tempo, r5):
        return self.__weight_tempo_rules["rule1"] * r1_tempo + \
                self.__weight_tempo_rules["rule2"] * r2 + \
                self.__weight_tempo_rules["rule4"] * r4_tempo + \
                self.__weight_tempo_rules["rule5"] * r5

    def evaluate(self,r1_tempo, r1_loudness, r2, r3, r4_tempo, r4_loudness, r5):
        self.__logger.debug("Evaluating")
        return self.__evaluate_tempo(r1_tempo, r2, r4_tempo, r5) * \
            self.__weight_tempo + self.__evaluate_loudness(r1_loudness, r3, r4_loudness) * \
                (1-self.__weight_loudness)
    
#    def __debug(self, message):
#        self.__logger.debug("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
#    
#    def __info(self, message):
#        self.__logger.info("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
        