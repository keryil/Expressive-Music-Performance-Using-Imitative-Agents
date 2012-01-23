'''
Created on 10 Oca 2012

@author: Kerem
'''
from imap.agent import Agent
import random
from copy import copy, deepcopy
#import pp
from tools import midi as mid
from tools.midi import remove_tempo_events_at, set_volume, translate_tempo
from tools import log
import logging
import time
from tools.analysis.rules import rule1_tempo, rule1_loudness, rule2, rule3,\
    rule4_tempo, rule4_loudness, rule5
from tools.analysis.lbdm import getNoteGroups, transferred_lbdm, lbdm
from tools.analysis.accentuation_curve import accentuation_curve
from tools.analysis.melodic_accent import analyze_melodic_accent
from tools.analysis.metric_structure import getMetricStructure
from tools.analysis import key_change, melodic_accent, metric_structure
from matplotlib import pyplot
from tools.analysis.key_change import correlate

class Simulation(object):
    agents = None
    midi = None
    defaultTempo = 3947
    defaultVolume = 100
    maxVolume = 255
    
    # this is the exact numeric value for default tempo, which is different from what is above
    nominalTempo = int(60000000 / defaultTempo)
    
    resetDone = False
    __jobServer = None
    __logger = None
    weight_tempo = 1.
    weight_loudness = 0. 
    weight_tempo_rules = {"rule1":1.0,"rule2":0.,"rule4":0.,"rule5":0.}
    weight_loudness_rules = {"rule1":0.0,"rule3":1.,"rule4":0.}
    
    def __init__(self):
        self.midi = mid.prepare_initial_midi("../../res/midi_text.txt", "../../res/sample.mid", self.defaultTempo)
#        self.__jobServer = pp.Server()
        self.__logger = log.get_logger(__name__)
    
    def reset(self, numberOfAgents=15):
        """
        Initializes the simulation with the set number of agents and sets Simulation.resetDone = True. Should be called 
        before starting any simulation run. 
        """
        self.agents = []
        initial_performances = []
        for i in range(numberOfAgents):
#            new_midi = mid.prepare_initial_midi("../../res/midi_text.txt", "../../res/sample%d.mid" % i, self.defaultTempo)
#            notes = [event for event in self.midi.tracks[0].eventList if event.type == "note"]
#            tempos = [event for event in self.midi.tracks[0].eventList if event.type == "tempo"]
##            self.nominalTempo = tempos[-1].tempo
#            first_tempo = self.nominalTempo * random.random() * 0.75 + 0.55 * self.nominalTempo
#            remove_tempo_events_at(0, new_midi)
#            new_midi.tracks[0].addTempo(0, first_tempo)
#            for note in notes:
#                volume = min(self.maxVolume, self.defaultVolume * random.random() * 0.5 + 0.75 * self.defaultVolume)
#                tempo = self.nominalTempo * random.random() * 0.75 + 0.55 * self.nominalTempo
##                print "Tempo/volume deviation at %d: %f, %f" % (notes.index(note), tempo, volume)
#                remove_tempo_events_at(note.time, new_midi)
#                new_midi.tracks[0].addTempo(note.time, translate_tempo(tempo))
#                volume = int(volume)
#                self.__logger.info("Setting volume to %s" % volume)
#                self.__logger.info("Agent %d --> Volume #%d: %d" % (i, notes.index(note), volume))
#                set_volume(new_midi, note, volume)
##                new_midi.tracks[0].addTempo(note.time + note.duration, first_tempo)
#            self.__logger.info("Volumes for agent %d: %s" % (i, [note.volume for note in new_midi.tracks[0].eventList if note.type == "note"]))
            agent = Agent(i, self.weight_tempo, self.weight_loudness, self.weight_tempo_rules, self.weight_loudness_rules, self.defaultTempo, self.defaultVolume,
                                     learning_rate=0.1)
            self.agents.append(agent)
            initial_performances.append(agent.performance)
            agent = None
            
            
        for i in range(len(initial_performances)-1):
            p = initial_performances[i]
            others = []
            for i in range(len(initial_performances)-1):
                per = initial_performances[i]
                if per != p:
                    others.append(per)
                
#            if len(others) < len(initial_performances) - 1:
#                print "Dafuq? %d vs %d" % (len(others), len(initial_performances) - 1)
#                exit(-1)
        self.resetDone = True
        
        average_loudness_dev, average_tempo_dev = self.collect_average_deviations(initial_performances)
        outfile = open("first_performance.txt", "w")
        t_lbdm = transferred_lbdm(lbdm(self.midi), getNoteGroups(self.midi)) + [0.]
        
        for i, (t_dev, l_dev) in enumerate(zip(average_tempo_dev, average_loudness_dev)):
            outfile.write("[%d] tdev=%f ldev=%f\n" % (i, t_dev, l_dev))
        tlbdm_correlation = correlate(t_lbdm, average_tempo_dev)
        
        average_performance = mid.prepare_initial_midi("../../res/midi_text.txt", "../../res/sample_average.mid", self.defaultTempo)
        notes = [event for event in average_performance.tracks[0].eventList if event.type == "note"]
#           
        for i in range(len(notes)):
#            prf = initial_performances[i]
#            tempos = [event for event in prf.tracks[0].eventList if event.type == "tempo"]
            for n, deviations in enumerate(zip(average_loudness_dev, average_tempo_dev)):
                v_dev, t_dev = deviations
#                print deviations
                note = notes[n]
                set_volume(average_performance, note, int(note.volume + v_dev))
                remove_tempo_events_at(note.time, average_performance)
                average_performance.tracks[0].addTempo(note.time, self.defaultTempo + t_dev)
        notes = [event for event in average_performance.tracks[0].eventList if event.type == "note"]
        metric_groups, metric_scores = metric_structure.getMetricStructure(average_performance)
        accentuation = accentuation_curve(melodic_accent.analyze_melodic_accent(average_performance), 
                                          metric_scores, key_change.analyze_key_change(average_performance), 
                                          notes)
        accentuation_correlation = correlate(accentuation, average_loudness_dev)
        outfile.write("Tempo/tLBDM tlbdm_correlation: %f" % tlbdm_correlation)
        tlbdm_correlation = correlate(t_lbdm, average_loudness_dev)
        outfile.write("\nLoudness/tLBDM: %f" % tlbdm_correlation)
        outfile.write("\nLoudness/Accentuation: %f" % accentuation_correlation)
        outfile.close()
#        exit()
        self.__logger.info("Reset.")
#        exit()
    
    def run(self, numberOfCycles=40):
        """
        Starts and runs the simulation by executing cycles for the given number of times.
        """
        # if reset is not called, call it
#        if self.resetDone == False:
#            self.reset()
#        self.resetDone = False
        self.reset()
        
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
        tempo = translate_tempo(tempo)
#        print "Tempo: %d" % tempo
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
        nominalTempo = self.defaultTempo
        #t[-1]
        average_performance = deepcopy(self.midi)
        t_lbdm = transferred_lbdm(lbdm(self.midi), getNoteGroups(self.midi)) + [0.]
        notes = [event for event in average_performance.tracks[0].eventList if event.type == "note"]
        average_loudness_dev, average_tempo_dev = self.collect_average_deviations([agent.perform(-1) for agent in self.agents], writeToFile=True)
        for i in range(len(notes)):
            note = notes[i]
            set_volume(average_performance, note, self.defaultVolume + average_loudness_dev[i])
            remove_tempo_events_at(note.time, average_performance)
            average_performance.tracks[0].addTempo(note.time, nominalTempo + average_tempo_dev[i])
        
#        outfile = open("average_performance.mid", "w")
#        average_performance.writeFile(outfile)
#        outfile.close()
        notes = [event for event in average_performance.tracks[0].eventList if event.type == "note"]
        metric_groups, metric_scores = metric_structure.getMetricStructure(average_performance)
        accentuation = accentuation_curve(melodic_accent.analyze_melodic_accent(average_performance), 
                                          metric_scores, key_change.analyze_key_change(average_performance), 
                                          notes)
        outfile = open("average_performance.txt", "w")
        for i, (t_dev, l_dev) in enumerate(zip(average_tempo_dev, average_loudness_dev)):
            outfile.write("[%d] tdev=%f ldev=%f\n" % (i, t_dev, l_dev))
#        print "Correlating tLBDM and average tempo deviations"
        correlation = correlate(t_lbdm, average_tempo_dev)
        outfile.write("Tempo/tLBDM correlation: %f" % correlation)
        correlation = correlate(t_lbdm, average_loudness_dev)
        outfile.write("\nLoudness/tLBDM correlation: %f" % correlation)
        correlation = correlate(accentuation, average_loudness_dev)
        outfile.write("\nLoudness/Accentuation correlation: %f" % correlation)
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
                tempo_dev = translate_tempo(tempo) - nominalTempo
#                print "note %d: volume %f, tempo %f || v_dev %f, t_dev %f" % (n, note.volume, tempo, volume_dev, tempo_dev)
                if writeToFile:
                    f.write("note %d: volume %f, tempo %f || v_dev %f, t_dev %f\n" % (n, note.volume, tempo, volume_dev, tempo_dev))
                average_loudness_dev[n] += float(volume_dev) / len(performances)
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
