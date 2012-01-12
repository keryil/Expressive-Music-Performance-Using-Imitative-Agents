'''
Created on 12 Oca 2012

@author: Kerem
'''
import unittest
from matplotlib import pyplot as plt
from tools import midi
from tools.analysis import *

class Test(unittest.TestCase):
    MIDI = None

    def setUp(self):
        self.MIDI = midi.prepare_initial_midi("/res/midi_text.txt", "/res/midi_text.txt", 19000)
        

    def tearDown(self):
        pass

    def testName(self):
        midi_lbdm = lbdm(self.MIDI)
        plt.plot(range(len(midi_lbdm)), midi_lbdm)
        plt.plot(range(len(midi_lbdm)),[sum(midi_lbdm)/len(midi_lbdm)] * len(midi_lbdm))
        plt.show()


if __name__ == "__main__":                      
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()