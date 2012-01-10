'''
Created on 10 Oca 2012

@author: Kerem
'''
from imap.agent import Agent
import random
from copy import copy
import pp
from tools import miditools
import logging

class Simulation(object):
    agents = None
    midi = None
    defaultTempo = 19000 * 0.8
    resetDone = False
    __jobServer = None
    __logger = None
    
    
    def __init__(self):
        self.midi = miditools.prepare_initial_midi(self.defaultTempo)
        self.__jobServer = pp.Server()
#        self.__logger = logging.getLogger(__name__)
#        self.__logger.
    
    def reset(self, numberOfAgents=10):
        """
        Initializes the simulation with the set number of agents and sets Simulation.resetDone = True. Should be called 
        before starting any simulation run. 
        """
        self.agents = [Agent(i) for i in range(numberOfAgents)]
        self.resetDone = True
        print "Reset."
    
    def run(self, numberOfCycles=100):
        """
        Starts and runs the simulation by executing cycles for the given number of times.
        """
        # if reset is not called, call it
        if self.resetDone == False:
            self.reset()
        self.resetDone = False
        
        for i in range(numberOfCycles):
            print "Cycle %d" % i
            self.cycle()
    
    def cycle(self):
        """
        A single cycle that allows all agents to perform.
        """
        agents = copy(self.agents)
        random.shuffle(agents)
        for agent in agents:
            # make the agent perform
            output = agent.perform()
            for a in self.agents:
                if a is not agent:
                    a.listen(output)
            

if __name__ == '__main__':
    s = Simulation()
    s.run()
    print "Done."