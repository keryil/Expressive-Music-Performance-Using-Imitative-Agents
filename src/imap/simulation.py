'''
Created on 10 Oca 2012

@author: Kerem
'''
from imap.agent import Agent
import random
from copy import copy
import pp
from tools import miditools, logtools
import logging
import time

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
        self.__logger = logtools.get_logger(__name__)
    
    def reset(self, numberOfAgents=3):
        """
        Initializes the simulation with the set number of agents and sets Simulation.resetDone = True. Should be called 
        before starting any simulation run. 
        """
        self.agents = [Agent(i) for i in range(numberOfAgents)]
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
    
    def cycle(self):
        """
        A single cycle that allows all agents to perform.
        """
        agents = self.agents
        random.shuffle(agents)
        for agent in agents:
            # make the agent perform
            output = agent.perform()
            time.sleep(1)
            
            # let all other agents evaluate the performance
            for a in agents:
                if a is not agent:
                    a.listen(output)
                    time.sleep(1)
            

if __name__ == '__main__':
    s = Simulation()
    s.run()
    print "Done"