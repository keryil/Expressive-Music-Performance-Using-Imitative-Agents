'''
Created on Jan 11, 2012

@author: kerem
'''
import math
from tools import log
logger = None

__strength = lambda f, s, m: (min(m, (math.fabs(f - s)))) / float(f + s) 

def lbdm(midi):
    pitch = __lbdm_pitch(midi)
    ioi = __lbdm_ioi(midi)
    rest = __lbdm_rest(midi)
    boundaryStrengths = []
    for p, i, r in zip(pitch, ioi, rest):
        boundaryStrengths.append(0.25 * (p + i + r))
    return boundaryStrengths

def __lbdm_pitch(midi):
    global logger
    if not logger:
        logger = log.get_logger(__name__)
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
    boundaryStrengths = []
    intervals = []
    for i in range(len(noteList) - 1):
        first_note = noteList[i]
        second_note = noteList[i + 1]
        
        # add 15 to intervals so that we do not have 0 values 
        # which may cause div by 0 errors
        interval = first_note.pitch - second_note.pitch + 15
        intervals.append(interval)
        logger.debug("first: p:%d t:%d d:%d v:%d" % (first_note.pitch, first_note.time, first_note.duration, first_note.volume))
        logger.debug("second: p:%d t:%d d:%d v:%d" % (second_note.pitch, second_note.time, second_note.duration, second_note.volume))
        logger.debug("Interval: %f" % interval)
    
    # first strength is calculated separately since it has no preceding interval
    s = __strength(intervals[0], intervals[1], 15) * intervals[0]
    boundaryStrengths.append(s)
    for i in range(len(intervals) - 2):
        firstInterval = intervals[i]
        secondInterval = intervals[i+1]
        thirdInterval = intervals[i+2]
        boundaryStrength = secondInterval * \
            (__strength(firstInterval, secondInterval, 15) + \
             __strength(secondInterval, thirdInterval, 15))
        boundaryStrengths.append(boundaryStrength)
        logger.debug("Interval: %f, Prev: %f, Next: %f, Strength: %f" % (secondInterval, firstInterval, secondInterval, boundaryStrength))
    # last strength also calculated separately
    s = __strength(intervals[-2], intervals[-1], 15) * intervals[-1]
    boundaryStrengths.append(s)
        
    return boundaryStrengths

def __lbdm_ioi(midi):
    global logger
    if not logger:
        logger = log.get_logger(__name__)
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
    boundaryStrengths = []
    intervals = []
    max_ioi = noteList[0].duration
    
    for i in range(len(noteList) - 1):
        first_note = noteList[i]
        second_note = noteList[i + 1]
        interval = second_note.time - first_note.time + 1
        intervals.append(interval)
        logger.debug("first: p:%d t:%f d:%f v:%d" % (first_note.pitch, first_note.time, first_note.duration, first_note.volume))
        logger.debug("second: p:%d t:%f d:%f v:%d" % (second_note.pitch, second_note.time, second_note.duration, second_note.volume))
        logger.debug("Interval: %f" % interval)
    # first strength is calculated separately since it has no preceding interval
    s = __strength(intervals[0], intervals[1], max_ioi) * intervals[0]
    boundaryStrengths.append(s)
    for i in range(len(intervals) - 2):
        firstInterval = intervals[i]
        secondInterval = intervals[i+1]
        thirdInterval = intervals[i+2]
        boundaryStrength = secondInterval * \
            (__strength(firstInterval, secondInterval, max_ioi) + \
             __strength(secondInterval, thirdInterval, max_ioi))
        boundaryStrengths.append(boundaryStrength)
        logger.debug("Interval: %f, Prev: %f, Next: %f, Strength: %f" % (secondInterval, firstInterval, secondInterval, boundaryStrength))
    # last strength also calculated separately
    s = __strength(intervals[-2], intervals[-1], max_ioi) * intervals[-1] 
    boundaryStrengths.append(s)
    return boundaryStrengths

def __lbdm_rest(midi):
    global logger
    if not logger:
        logger = log.get_logger(__name__)
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
    boundaryStrengths = []
    intervals = []
    max_ioi = noteList[0].duration
    
    for i in range(len(noteList) - 1):
        first_note = noteList[i]
        second_note = noteList[i + 1]
        interval = second_note.time - first_note.time - first_note.duration + 1
        intervals.append(interval)
        logger.debug("first: p:%d t:%f d:%f v:%d" % (first_note.pitch, first_note.time, first_note.duration, first_note.volume))
        logger.debug("second: p:%d t:%f d:%f v:%d" % (second_note.pitch, second_note.time, second_note.duration, second_note.volume))
        logger.debug("Interval: %f" % interval)
    # first strength is calculated separately since it has no preceding interval
    s = __strength(intervals[0], intervals[1], max_ioi) * intervals[0]
    boundaryStrengths.append(s)
    for i in range(len(intervals) - 2):
        firstInterval = intervals[i]
        secondInterval = intervals[i+1]
        thirdInterval = intervals[i+2]
        boundaryStrength = secondInterval * \
            (__strength(firstInterval, secondInterval, max_ioi) + \
             __strength(secondInterval, thirdInterval, max_ioi))
        boundaryStrengths.append(boundaryStrength)
        logger.debug("Interval: %f, Prev: %f, Next: %f, Strength: %f" % (secondInterval, firstInterval, secondInterval, boundaryStrength))
    # last strength also calculated separately
    s = __strength(intervals[-2], intervals[-1], max_ioi) * intervals[-1] 
    boundaryStrengths.append(s)
    return boundaryStrengths

if __name__ == "__main__":
    from tools import midi as mid
    midi = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    print __lbdm_pitch(midi)
    print __lbdm_ioi(midi)
    print __lbdm_rest(midi)
    print lbdm(midi)
