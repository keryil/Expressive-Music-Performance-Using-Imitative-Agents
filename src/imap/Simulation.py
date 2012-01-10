'''
Created on 10 Oca 2012

@author: Kerem
'''
from imap import Agent
import random
from midiutil.MidiFile import MIDIFile
import re

class Simulation(object):
    agents = []
    midi = None
    defaultTempo = 19000 * 0.8
    
    LINE_REGEX = re.compile("^(?P<time>\d+) (?P<on_off>(On|Off)).*n=(?P<pitch>\d+).*v=(?P<volume>\d+)")
    
    def __init__(self):
        midi = MIDIFile(1)
        midi.addTempo(track=0, time=0, tempo=self.defaultTempo)
        midiText = open("midi_text.txt")
        duration = -1
        pitch = volume = time = -1
        for line in midiText:
            line = line.rstrip()
            m = self.LINE_REGEX.search(line)
            if m.group("on_off") == "On":
                pitch = int(m.group("pitch"))
                volume = int(m.group("volume"))
                time = int(m.group("time"))
                duration = time
            else:
                time2 = int(m.group("time"))
                duration = (float(time2)-float(time))
                midi.addNote(0, 0, pitch, time, duration, volume)
                print "Added p: %d t: %d d: %f v: %d" % (pitch,time,duration,volume)
                duration = -1
        midi.writeFile(open("sample.midi","w"))
        pass
    
    
    def reset(self, numberOfAgents, numberOfCycles):
        """
        Initializes the simulation with the set number of agents
        """
        agents = []
        for i in range(numberOfAgents):
            agents.append(Agent())
        
        for i in range(numberOfCycles):
            self.cycle()
    
    def cycle(self):
        """
        A single cycle that allows all agents to perform
        """
        usedAgents = []
        # select an agent
        agent = random.choice(self.agents)
        while agent not in usedAgents:
            agent = random.choice(self.agents)
        
        usedAgents.append(agent)
        
        # make the agent perform
        output = agent.perform()
        for a in agents:
            if a is not agent:
                a.listen(output)
        
        
def func(n):
    if n == 0:
        return 0
    elif n== 1:
        return 1
    else:
        return func(n-1) + func(n-2)

def callback(result):
    print result

if __name__ == '__main__':
    s = Simulation()