'''
Created on 10 Oca 2012

@author: Kerem
'''
from imap import Agent
import random

class Simulation(object):
    agents = []
    def __init__(self):
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
    print func(2)
    import pp
    job_server = pp.Server()
    f1 = job_server.submit(func, (3,), callback=callback)
    f2 = job_server.submit(func, (4,), callback=callback)