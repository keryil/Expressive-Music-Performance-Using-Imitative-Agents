'''
Created on 13 Oca 2012

@author: Kerem
'''
from math import floor, ceil


def getMetricStructure(midi, signature="2/4", quarterNoteDuration=480.):
    """
    Returns the metric structure as a dictionary of structure for different upper_levels e.g. half notes, quarter notes, eighth notes, sixteenth notes etc.
    """
    metric_structure = {}
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
    scoreList = []
    totalDuration = noteList[-1].time + noteList[-1].duration
    for note in noteList:
        d = note.duration / quarterNoteDuration
        if not metric_structure.has_key(d):
#            print d, totalDuration / note.duration
#            print [0] * int(totalDuration / note.duration)
            # quarter notes are straightforward
#            if d == 1:
#                metric_structure[d] = [0] * int(totalDuration/note.duration/2)
#            else:
                metric_structure[d] = [0] * int(totalDuration / note.duration)
    
    # MWFR 1 (revised) Every attack point must be associated with a beat at the smallest metrical level present at that point in the piece.
    # MWFR 2 (revised) Every beat at a given level must also be a beat at all smaller upper_levels present at that point in the piece.
    # MWFR 4 (revised) The tactus and immediately larger metrical upper_levels must consist of beats equally spaced throughout the piece. 
    #                  At subtactus metrical upper_levels, weak beats must be equally spaced between the surrounding strong beats.
    # MWFR 3 At each metrical level, strong beats are spaced either two or three beats apart.
    for note in noteList:        
        total_score = 0
        d = note.duration / quarterNoteDuration
        relevant_structure = metric_structure[d]
        position = int(floor(note.time / note.duration))
        
        # first level should alternate
        if note.duration - quarterNoteDuration < 0.1:
            if (int(floor(position)) % 2 == 1):
                total_score += 1
                metric_structure[d][position] = 1
            else:
                metric_structure[d][position] = 0
                scoreList.append(total_score)
                continue
            
        if relevant_structure[position - 1] != 1:
            total_score += 1
            relevant_structure[position] = 1
            
        
            upper_levels = [level for level in sorted(metric_structure.keys()) if level > d]
            for level in upper_levels:
                if metric_structure[level][int(floor(position * d / level)) - 1] != 1:
                    total_score += 1
                    metric_structure[level][int(floor(position * d / level))] = 1
        scoreList.append(total_score)
#    print scoreList
    return metric_structure, scoreList
    
if __name__ == '__main__':
    from tools import midi as mid
    midi = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    track = midi.tracks[0]
    metric_structure, scores = getMetricStructure(midi)
    print scores
    # maximum beats i.e. number of beats at minimal level
    max_beats = len(metric_structure[min(metric_structure.keys())])
    min_level = min(metric_structure.keys())
    keys = [float(key) for key in metric_structure.keys()]
    for level in sorted(keys):
        structure = metric_structure[level]
#        structureString = " %" + str(int(max_beats / len(structure))) + "d "
        structureString = "%-s" + " " * int(floor(level/min_level) - 1) * 2 + "|"
#        structureString = structureString
        formatString = "%f: " % level + structureString * len(structure)
#        formatString.format(*structure)
#        print formatString
#        print structure
        print formatString % tuple(structure)
        
        