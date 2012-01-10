'''
Created on 10 Oca 2012

@author: Kerem
'''
from midiutil.MidiFile import MIDIFile

class Agent(object):
    '''
    classdocs
    '''
    performance = None
    id = None
    def __init__(self, id):
        '''
        Constructor
        '''
        self.id = id
    
    def perform(self):
        print "perform()"
        pass
    
    def listen(self, performance):
        print "listen()"
        pass
    
    def evaluate(self, performance):
        print "evaluate()"
        pass
        