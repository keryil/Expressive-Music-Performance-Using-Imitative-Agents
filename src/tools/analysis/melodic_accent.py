'''
Created on Jan 11, 2012

@author: kerem

Implements the melodic accent model of Thomassen 1982
'''

from tools import log
logger = None

def analyze_melodic_accent(midi):
    global logger
    if not logger:
        logger = log.get_logger(__name__)
    track = midi.tracks[0]
    pitchList = [noteEvent.pitch for noteEvent in track.eventList if noteEvent.type == "note"]
    accentProbabilities = [1. for p in pitchList]
    for i in range(len(pitchList)):
        pitch3 = pitchList[i]
        pitch1=pitch2=None
        if i != 0:
            pitch2 = pitchList[i-1]
            if i != 1:
                pitch1 = pitchList[i-2]
        p2,p3 = __analyze_note_triplet(pitch1, pitch2, pitch3)
        
        accentProbabilities[i] *= p3
        if i != 0:
            accentProbabilities[i-1] *= p2
    return accentProbabilities
            

def __analyze_note_triplet(pitch1, pitch2, pitch3):
    """
    Analyzes the three pitches and returns a tuple containing
    the probability of pitch2 and pitch3 being accents, respectively. 
    pitch1 and/or pitch2 may be None if we are at the beginning of the melody.
    """
    p2 = 0.
    p3 = 0.
    
    # handles first two windows which do not have all three pitches
    if pitch1 == None:
        if pitch2 == None:
            return 0.,1.
        else:
            if pitch3 == pitch2:
                return 0.5, 0.5
            else:
                return 0., 1.
    c1 = c2 = 0
    
    try:        
        c1 = pitch2 - pitch1
        c2 = pitch3 - pitch2
    except TypeError, e:
        exit()
    
    # c1 == c2 == 0 and c1 == 0, c2 != 0
    if c1 == 0:
        if c2 == 0:
            p2 = p3 = 0.
        else:
            p2 = 0.
            p3 = 1.
    # c1 != 0, c2 == 0
    elif c2 == 0:
        p2 = 1.
        p3 = 0.
    else:
        if c1 > 0:
            if c2 < 0:
                p2 = 0.83
                p3 = 0.17
            else:
                p2 = 0.33
                p3 = 0.67
        else:
            if c2 < 0:
                p2 = p3 = 0.5
            else:
                p2 = .71
                p3 = .29
        
    try:
        assert 1 - p2 - p3 <= .001
    except AssertionError, e:
        exit()
    return (p2,p3)

if __name__ == '__main__':
    from tools import midi as mid
    midi = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    print analyze_melodic_accent(midi)