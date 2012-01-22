'''
Created on 10 Oca 2012

@author: Kerem
'''
from imap.agent import Agent
import random
from copy import copy, deepcopy
import pp
from tools import midi as mid
from tools.midi import translate_tempo
from tools import log
import logging
import time
from tools.analysis.rules import rule1_tempo, rule1_loudness, rule2, rule3,\
    rule4_tempo, rule4_loudness, rule5
from tools.analysis.lbdm import getNoteGroups, transferred_lbdm, lbdm
from tools.analysis.accentuation_curve import accentuation_curve
from tools.analysis.melodic_accent import analyze_melodic_accent
from tools.analysis.metric_structure import getMetricStructure
from tools.analysis import key_change
from matplotlib import pyplot
from tools.analysis.key_change import correlate

class Simulation(object):
    agents = None
    midi = None
    defaultTempo = 3947
    defaultVolume = 100
    
    # this is the exact numeric value for default tempo, which is different from what is above
    nominalTempo = int(60000000 / defaultTempo)
    
    resetDone = False
    __jobServer = None
    __logger = None
    weight_tempo, weight_loudness, weight_tempo_rules, weight_loudness_rules = \
        1.,0.,{"rule1":1.0,"rule2":0.,"rule4":0.,"rule5":0.},{"rule1":0.0,"rule3":0.,"rule4":0.}
    
    def __init__(self):
        self.midi = mid.prepare_initial_midi("../../res/midi_text.txt", "../../res/sample.mid", self.defaultTempo)
        self.__jobServer = pp.Server()
        self.__logger = log.get_logger(__name__)
    
    def reset(self, numberOfAgents=2):
        """
        Initializes the simulation with the set number of agents and sets Simulation.resetDone = True. Should be called 
        before starting any simulation run. 
        """
        self.agents = []
        initial_performances = []
        for i in range(numberOfAgents):
            new_midi = mid.prepare_initial_midi("../../res/midi_text.txt", "../../res/sample%d.mid" % i, self.defaultTempo)
            notes = [event for event in new_midi.tracks[0].eventList if event.type == "note"]
            tempos = [event for event in self.midi.tracks[0].eventList if event.type == "tempo"]
#            self.nominalTempo = tempos[-1].tempo
            first_tempo = self.nominalTempo * random.random() * 0.75 + 0.55 * self.nominalTempo
            new_midi.tracks[0].addTempo(0, first_tempo)
            for note in notes:
                volume = self.defaultVolume * random.random() * 0.5 + 0.75 * self.defaultVolume
                tempo = self.nominalTempo * random.random() * 0.75 + 0.55 * self.nominalTempo
#                print "Tempo/volume deviation at %d: %f, %f" % (notes.index(note), tempo, volume)
                new_midi.tracks[0].addTempo(note.time, tempo)
                note.volume = volume
                new_midi.tracks[0].addTempo(note.time + note.duration, first_tempo)
            initial_performances.append(new_midi)
            self.agents.append(Agent(i, self.weight_tempo, self.weight_loudness, self.weight_tempo_rules, self.weight_loudness_rules, new_midi, self.nominalTempo, self.defaultVolume))
        self.resetDone = True
        
        average_loudness_dev, average_tempo_dev = self.collect_average_deviations(initial_performances)
        outfile = open("first_performance.txt", "w")
        t_lbdm = transferred_lbdm(lbdm(self.midi), getNoteGroups(self.midi)) + [0.]
        
        for i, (t_dev, l_dev) in enumerate(zip(average_tempo_dev, average_loudness_dev)):
            outfile.write("[%d] tdev=%f ldev=%f\n" % (i, t_dev, l_dev))
        correlation = correlate(t_lbdm, average_tempo_dev)
        
        outfile.write("Tempo/tLBDM correlation: %f" % correlation)
        outfile.close()
        
        self.__logger.info("Reset.")
    
    def run(self, numberOfCycles=20):
        """
        Starts and runs the simulation by executing cycles for the given number of times.
        """
        # if reset is not called, call it
        if self.resetDone == False:
            self.reset()
        self.resetDone = False
        
        for i in range(numberOfCycles):
            self.__logger.info("Cycle %d" % i)
            self.cycle(i)
        print "Done simulating"
        self.collect_data()
    
                
    def __find_tempo_of_note(self, note, midi):
        tempo = None
        tempo_events = [(event.time, event.tempo) for event in midi.tracks[0].eventList if event.type == "tempo"]
        for time, temp in tempo_events:
            if time > note.time:
                break
            else: 
                tempo = temp
        return tempo
    
    def collect_data(self):
        """
        Computes the average loudness and tempo deviations in the population and returns a midi of the average
        performance of the population.
        """
        print "Collecting data..."
        
#        pyplot.plot(range(len(average_loudness_dev)), average_loudness_dev)
#        pyplot.plot(range(len(average_tempo_dev)), average_tempo_dev)
#        pyplot.plot()
        t = [event.tempo for event in self.midi.tracks[0].eventList if event.type == "tempo"]
        nominalTempo = self.nominalTempo
        #t[-1]
        average_performance = deepcopy(self.midi)
        t_lbdm = transferred_lbdm(lbdm(self.midi), getNoteGroups(self.midi)) + [0.]
        notes = [event for event in average_performance.tracks[0].eventList if event.type == "note"]
        average_loudness_dev, average_tempo_dev = self.collect_average_deviations([agent.perform(-1) for agent in self.agents], writeToFile=True)
        for i in range(len(notes)):
            note = notes[i]
            note.volume += average_loudness_dev[i]
            average_performance.tracks[0].addTempo(note.time, nominalTempo + average_tempo_dev[i])
        
        outfile = open("average_performance.mid", "w")
        average_performance.writeFile(outfile)
        outfile.close()
        
        outfile = open("average_performance.txt", "w")
        for i, (t_dev, l_dev) in enumerate(zip(average_tempo_dev, average_loudness_dev)):
            outfile.write("[%d] tdev=%f ldev=%f\n" % (i, t_dev, l_dev))
#        print "Correlating tLBDM and average tempo deviations"
        correlation = correlate(t_lbdm, average_tempo_dev)
        outfile.write("Tempo/tLBDM correlation: %f" % correlation)
        outfile.close()
        
        return average_performance
        
    def collect_average_deviations(self, performances, writeToFile=False):
        average_loudness_dev = []
        average_tempo_dev = []
        t = [event.tempo for event in self.midi.tracks[0].eventList if event.type == "tempo"]
        nominalTempo = self.defaultTempo
        f = None
        if writeToFile:
            f = open("all_deviations.txt", "w")
            
        print "Nominal tempo: %s" % nominalTempo
        for performance in performances:
#            performance = agent.perform()
            notes = [event for event in performance.tracks[0].eventList if event.type == "note"]
            if average_loudness_dev == []:
                average_loudness_dev = [0. for note in notes]
            if average_tempo_dev == []:
                average_tempo_dev = [0. for note in notes]
            
            for n, note in enumerate(notes):
                volume_dev = note.volume - self.defaultVolume
                tempo = self.__find_tempo_of_note(note, performance)
                tempo_dev = tempo - nominalTempo
                print "note %d: volume %f, tempo %f || v_dev %f, t_dev %f" % (n, note.volume, tempo, volume_dev, tempo_dev)
                if writeToFile:
                    f.write("note %d: volume %f, tempo %f || v_dev %f, t_dev %f\n" % (n, note.volume, tempo, volume_dev, tempo_dev))
                average_loudness_dev[n] += volume_dev / len(performances)
                average_tempo_dev[n] += tempo_dev / len(performances)
                
#        average_loudness_dev = map(lambda x: x / len(performances), average_loudness_dev)
#        average_tempo_dev = map(lambda x: x / len(performances), average_tempo_dev)
        if writeToFile:
            f.close()
        return average_loudness_dev, average_tempo_dev
    
    
    def cycle(self, cycle_no):
        """
        A single cycle that allows all agents to perform.
        """
        agents = self.agents
        random.shuffle(agents)
        for agent in agents:
            round_no = agents.index(agent) + cycle_no + 1
            self.__logger.info("Cycle %s Round %s" % (cycle_no, round_no))
            # make the agent perform
            output = agent.perform(round_no)
            group_structure = getNoteGroups(output)
            nominal_tempo = self.nominalTempo
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
                if a.getId() != agent.getId():
                    a.listen(output, r1_tempo, r1_loudness, r2, r3, r4_tempo, r4_loudness, r5)
            

if __name__ == '__main__':
    s = Simulation()
    s.run()
    print "Done"
