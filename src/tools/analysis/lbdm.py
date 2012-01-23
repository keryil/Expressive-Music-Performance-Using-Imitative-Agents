'''
Created on Jan 11, 2012

@author: kerem

This module implements the LBDM by Combouropoulos 2001
'''
import math
from tools import log
from tools.analysis.key_change import midi_to_note
from copy import deepcopy
logger = None

__strength = lambda f, s, m: (min(m, (math.fabs(f - s)))) / float(f + s) 

def lbdm(midi):
    """
    Receives a monophonic melody of N notes in MIDI format, and returns a list of size N-1 representing the 
    boundary strengths of note intervals.
    """
    pitch = __lbdm_pitch(midi)
    ioi = __lbdm_ioi(midi)
    rest = __lbdm_rest(midi)
    boundaryStrengths = []
    for p, i, r in zip(pitch, ioi, rest):
        boundaryStrengths.append(0.25 * p + 0.50 * i + 0.25 * r)
    
    # make sure we have boundaries at the two ends
#    boundaryStrengths[0] = boundaryStrengths[-1] = max(boundaryStrengths)
    return boundaryStrengths

def transferred_lbdm(original_lbdm, note_groups):
    note_index = 0
    new_lbdm = deepcopy(original_lbdm)
    for group in note_groups:
        first_part, turning_point, second_part = tuple(group)
        lowest_lbdm = 100.
        turning_point_index = 0
        for n in first_part:
            lowest_lbdm = min(original_lbdm[note_index], lowest_lbdm)
            note_index += 1
        turning_point_index = note_index
        note_index += 1
        for n in second_part:
            if note_index == len(original_lbdm):
                break
            lowest_lbdm = min(original_lbdm[note_index], lowest_lbdm)
            note_index += 1
        new_lbdm[turning_point_index] = lowest_lbdm / 2
    return new_lbdm

def getNoteGroups(midi):
    """
    Receives a monophonic melody of N notes, and returns a grouping of them in format 
    [[[first_part],turning_point,[second_part]],[[first_part], turning_point, [second_part]]]
    based on their LBDM scores
    """
    boundaryStrengths = lbdm(midi)
    track = midi.tracks[0]
    avg_strength = sum(boundaryStrengths) / len(boundaryStrengths)
    groups = []
    current_group = []
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
#    print len(boundaryStrengths), len(noteList)
    for i in range(len(noteList)):
        note = noteList[i]
        if current_group == []:
            current_group.append(note)
        elif len(current_group) < 4:
            current_group.append(note)
        elif i == len(boundaryStrengths):
            current_group.append(note)
        elif boundaryStrengths[i] > avg_strength:
#            current_group.append(note)
            groups.append(deepcopy(current_group))
            current_group = [note]
        else:
            current_group.append(note)
    if current_group != []:
        groups.append(current_group)
#    print "Preliminary groups: %s" % groups
    
    detailedGroups = []
    firstNoteOfGroup = 0
    for group in groups:
        first = []
        last = []
        firstStrength = 0.
        third_max_lbdm = max(boundaryStrengths[firstNoteOfGroup+1:firstNoteOfGroup + len(group) - 1])
        turningPointIndex = boundaryStrengths.index(third_max_lbdm, firstNoteOfGroup + 1, firstNoteOfGroup + len(group) - 1)
#        print "DEBUG:: turningPointIndex=%d" % turningPointIndex
        turningPoint = noteList[turningPointIndex]
#        foundTurningPoint = False
        for i in range(len(group)):
            if firstNoteOfGroup + i < turningPointIndex:
                first.append(noteList[firstNoteOfGroup + i])
            elif firstNoteOfGroup + i > turningPointIndex:
                last.append(noteList[firstNoteOfGroup + i])
                
        firstNoteOfGroup += len(group)
        detailedGroups.append([first, turningPoint, last])
                
                
            
            
        
    return detailedGroups

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
        interval = first_note.pitch - second_note.pitch + 12
        intervals.append(interval)
        logger.debug("first: p:%d t:%d d:%d v:%d" % (first_note.pitch, first_note.time, first_note.duration, first_note.volume))
        logger.debug("second: p:%d t:%d d:%d v:%d" % (second_note.pitch, second_note.time, second_note.duration, second_note.volume))
        logger.debug("Interval: %f" % interval)
    
    # first strength is calculated separately since it has no preceding interval
    s = __strength(intervals[0], intervals[1], 12) * intervals[0]
    boundaryStrengths.append(s)
    for i in range(len(intervals) - 2):
        firstInterval = intervals[i]
        secondInterval = intervals[i+1]
        thirdInterval = intervals[i+2]
        boundaryStrength = secondInterval * \
            (__strength(firstInterval, secondInterval, 12) + \
             __strength(secondInterval, thirdInterval, 12))
        boundaryStrengths.append(boundaryStrength)
        logger.debug("Interval: %f, Prev: %f, Next: %f, Strength: %f" % (secondInterval, firstInterval, secondInterval, boundaryStrength))
    # last strength also calculated separately
    s = __strength(intervals[-2], intervals[-1], 12) * intervals[-1]
    boundaryStrengths.append(s)
    # scale to 0-1
    boundaryStrengths = map(lambda x: x / max(boundaryStrengths),boundaryStrengths)    
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
    
    # scale to 0-1
    boundaryStrengths = map(lambda x: x / max_ioi,boundaryStrengths)
        
    return boundaryStrengths

def __lbdm_rest(midi):
    global logger
    if not logger:
        logger = log.get_logger(__name__)
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
    boundaryStrengths = []
    intervals = []
    max_rest = noteList[0].duration
    
    for i in range(len(noteList) - 1):
        first_note = noteList[i]
        second_note = noteList[i + 1]
        interval = second_note.time - first_note.time - first_note.duration + 1
        intervals.append(interval)
        logger.debug("first: p:%d t:%f d:%f v:%d" % (first_note.pitch, first_note.time, first_note.duration, first_note.volume))
        logger.debug("second: p:%d t:%f d:%f v:%d" % (second_note.pitch, second_note.time, second_note.duration, second_note.volume))
        logger.debug("Interval: %f" % interval)
    # first strength is calculated separately since it has no preceding interval
    s = __strength(intervals[0], intervals[1], max_rest) * intervals[0]
    boundaryStrengths.append(s)
    for i in range(len(intervals) - 2):
        firstInterval = intervals[i]
        secondInterval = intervals[i+1]
        thirdInterval = intervals[i+2]
        boundaryStrength = secondInterval * \
            (__strength(firstInterval, secondInterval, max_rest) + \
             __strength(secondInterval, thirdInterval, max_rest))
        boundaryStrengths.append(boundaryStrength)
        logger.debug("Interval: %f, Prev: %f, Next: %f, Strength: %f" % (secondInterval, firstInterval, thirdInterval, boundaryStrength))
    # last strength also calculated separately
    s = __strength(intervals[-2], intervals[-1], max_rest) * intervals[-1] 
    boundaryStrengths.append(s)
    # scale to 0-1
    boundaryStrengths = map(lambda x: x / max_rest,boundaryStrengths)
    return boundaryStrengths

if __name__ == "__main__":
    from tools import midi as mid
    from matplotlib import pyplot as plt
    midi = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    print __lbdm_pitch(midi)
    print __lbdm_ioi(midi)
    print __lbdm_rest(midi)
    strengths = lbdm(midi)
    groups = getNoteGroups(midi)
    groupMarkers = []
    turningPointMarkers = []
    markerCounter = 0.5
    for group in groups:
        markerCounter += len(group[0]) + len(group[2]) + 1
        turningPointMarkers.append(markerCounter - 0.5 - len(group[2]))
        groupMarkers.append(markerCounter)
    t_ldbm = transferred_lbdm(lbdm(midi),groups)
        
    plt.plot(range(1, len(strengths) + 1),strengths)
    plt.plot(range(1, len(t_ldbm) + 1),t_ldbm)
    
    plt.xticks(range(1,len(strengths)))
    plt.plot(range(len(strengths)),[sum(strengths)/len(strengths)] * len(strengths))
    plt.plot()
    
    axes = plt.axes()
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
#    print [[midi_to_note(note.pitch) for note in group] for group in getNoteGroups(midi)]
    print getNoteGroups(midi)
    for i in range(1,len(noteList) + 1):
        try:
            axes.annotate("%s" % midi_to_note(noteList[i-1].pitch), xy = (i, strengths[i-1]))
        except IndexError, err:
            axes.annotate("%s" % midi_to_note(noteList[i-1].pitch), xy = (i, sum(strengths)/len(strengths)))
    
    for marker in turningPointMarkers:
#        print marker
        plt.axvline(x = marker, color="y")
        
    for marker in groupMarkers:
#        print marker
#        axes.add_line(Line2D(xdata=[marker]*3, ydata=[0,1,2]))
        plt.axvline(x=marker, color="r", linewidth=2)
        
    plt.show()
