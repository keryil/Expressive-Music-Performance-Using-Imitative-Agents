'''
Created on 10 Oca 2012

@author: Kerem
'''
from midiutil.MidiFile import MIDIFile
from tools import logtools

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
        self.__logger = logtools.get_agent_logger(__name__, id)
#        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
        
    def perform(self):
        self.__logger.debug("Performing")
    
    def listen(self, performance):
        self.__logger.debug("Listening")
    
    def evaluate(self, performance):
        self.__logger.debug("Evaluating")
    
#    def __debug(self, message):
#        self.__logger.debug("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
#    
#    def __info(self, message):
#        self.__logger.info("Agent %s |::| %s::%s" % (self.id, inspect.stack()[1][3], message))
        