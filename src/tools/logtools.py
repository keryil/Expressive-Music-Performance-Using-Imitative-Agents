'''
Created on 10 Oca 2012

@author: Kerem
'''
import logging

def get_agent_logger(name, agentId):
        logger = logging.getLogger(name)
        logger.setLevel("INFO")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s Agent' + str(agentId) + ' %(module)s.%(funcName)s(): %(message)s'))
        logger.addHandler(handler)
        return logger

def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel("INFO")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s.%(funcName)s(): %(message)s'))
        logger.addHandler(handler)
        return logger        