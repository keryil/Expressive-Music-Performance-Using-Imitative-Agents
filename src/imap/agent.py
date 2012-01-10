'''
Created on 10 Oca 2012

@author: Kerem
'''
from midiutil.MidiFile import MIDIFile
import logging

class Agent(object):
    '''
    classdocs
    '''
    performance = None
    id = None
    __logger = None
    def __init__(self, id):
        '''
        Constructor
        '''
        self.id = id
        self.__logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.setLevel("DEBUG")
        handler.setFormatter(logging.Formatter('%(asctime)s Agent' + str(id) + '%(levelname)s %(module)s %(funcName)s %(message)s'))
        self.__logger.addHandler(handler)
        
#        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
        
    def perform(self):
        self.__logger.info("Performing")
    
    def listen(self, performance):
        self.__logger.info("Listening")
    
    def evaluate(self, performance):
        self.__logger.info("Evaluating")
    
#    def __debug(self, message):
#        self.__logger.debug("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
#    
#    def __info(self, message):
#        self.__logger.info("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
        