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

    def __init__(self):
        '''
        Constructor
        '''
    
    def perform(self):
        print "perform()"
        pass
    
    def listen(self, performance):
        print "listen()"
        pass
    
    def evaluate(self, performance):
        print "evaluate()"
        pass
        