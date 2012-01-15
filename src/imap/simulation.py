'''
Created on 10 Oca 2012

@author: Kerem
'''
from imap.agent import Agent
import random
from copy import copy
import pp
from tools import midi as mid
from tools import log
import logging
import time
from tools.analysis.rules import rule1_tempo, rule1_loudness, rule2, rule3,\
    rule4_tempo, rule4_loudness, rule5
from tools.analysis.lbdm import getNoteGroups
from tools.analysis.accentuation_curve import accentuation_curve
from tools.analysis.melodic_accent import analyze_melodic_accent
from tools.analysis.metric_structure import getMetricStructure
from tools.analysis import key_change

class Simulation(object):
    agents = None
    midi = None
    defaultTempo = 3947
    defaultVolume = 100
    resetDone = False
    __jobServer = None
    __logger = None
    weight_tempo, weight_loudness, weight_tempo_rules, weight_loudness_rules = \
        1,0,{"rule1":1.0,"rule2":0.,"rule4":0.,"rule5":0.},{"rule1":0.0,"rule3":0.,"rule4":0.}
    
    def __init__(self):
        self.midi = mid.prepare_initial_midi("../../res/midi_text.txt", "../../res/sample.midi", self.defaultTempo)
        self.__jobServer = pp.Server()
        self.__logger = log.get_logger(__name__)
    
    def reset(self, numberOfAgents=15):
        """
        Initializes the simulation with the set number of agents and sets Simulation.resetDone = True. Should be called 
        before starting any simulation run. 
        """
        self.agents = [Agent(i, self.weight_tempo, self.weight_loudness, self.weight_tempo_rules, self.weight_loudness_rules, self.midi) for i in range(numberOfAgents)]
        self.resetDone = True
        self.__logger.info("Reset.")
    
    def run(self, numberOfCycles=100):
        """
        Starts and runs the simulation by executing cycles for the given number of times.
        """
        # if reset is not called, call it
        if self.resetDone == False:
            self.reset()
        self.resetDone = False
        
        for i in range(numberOfCycles):
            self.__logger.info("Cycle %d" % i)
            self.cycle()
        print "Done"
    
    def cycle(self):
        """
        A single cycle that allows all agents to perform.
        """
        agents = self.agents
        random.shuffle(agents)
        for agent in agents:
            # make the agent perform
            output = agent.perform()
            group_structure = getNoteGroups(output)
            nominal_tempo = self.defaultTempo
            nominal_volume = self.defaultVolume
            tempo_events = [(event.time, event.tempo) for event in output.tracks[0].eventList if event.type == "tempo"]
            notes = [event for event in output.tracks[0].eventList if event.type == "note"]
            metrical_hierarchy,metrical_scores = getMetricStructure(output)
            keys = key_change.analyze_key_change(output)
            accentuation = accentuation_curve(analyze_melodic_accent(output), metrical_scores, keys, notes)
            r1_tempo, r1_loudness, r2, r3, r4_tempo, r4_loudness, r5 = \
                rule1_tempo(group_structure, nominal_tempo, tempo_events), \
                rule1_loudness(group_structure, nominal_volume), \
                rule2(group_structure, nominal_tempo, tempo_events), \
                rule3(notes, nominal_volume, accentuation), \
                rule4_tempo(notes, accentuation, nominal_tempo, tempo_events), \
                rule4_loudness(notes, accentuation, nominal_volume), \
                rule5(group_structure, nominal_tempo, tempo_events)
            # let all other agents evaluate the performance
            for a in agents:
                if a is not agent:
                    a.listen(output, r1_tempo, r1_loudness, r2, r3, r4_tempo, r4_loudness, r5)
            

if __name__ == '__main__':
    s = Simulation()
    s.run()
    print "Done"
