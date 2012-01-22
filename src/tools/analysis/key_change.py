'''
Created on Jan 11, 2012

@author: kerem

Implements the key detection algorithm by Krumhansl 2001
There are 960 beats per measure in the midi
'''
import math
from tools import log

logger = None
CMaj = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
CMin = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
notes = ("C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B")
rotate_array = lambda x,t: x[-t:] + x[:-t]
midi_to_note = lambda x: notes[x % 12]
notes_in_measure =  lambda n, s, e: [note for note in n if (note.time >= s) and (note.time < e)]
durations_to_array = lambda d: [d[note] for note in notes]
measure_duration = 960

# return true if note n is in measure m
note_in_measure = lambda n, m: (n.time >= measure_duration * m) and (n.time < measure_duration * (m+1))

from math import floor
note_find_measure = lambda n: int(floor(n.time / measure_duration))
                                 
# 24 12-dimensional vectors, one for each major/minor key
key_vectors = {"C Major": CMaj, "C Minor": CMin}
for i in range(len(notes))[1:]:
    note = notes[i]
    distance = i
    #first, majors
    key_vectors[note + " Major"] = rotate_array(CMaj, distance)
    #then, minors
    key_vectors[note + " Minor"] = rotate_array(CMin, distance)

def analyze_key_change(midi):
    
    # we have to do the first bar without comparison and second bar with single comparison 
    # so that we have previous two bars for analysis
    
    global logger
    if not logger:
        logger = log.get_logger(__name__)
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
    keys = []
    keyChange = [0. for i in range(6)]
    
    # process measure by measure
    for i in range(0,6*measure_duration,measure_duration):
        # first measure
        if i == 0:
            continue
#            relevantNotes = notes_in_measure(noteList, i, i+960)
#            keys.append(determine_key(relevantNotes))
        #second measure
        elif i == measure_duration:
            referenceNotes = notes_in_measure(noteList, i-measure_duration,i)
            referenceKey, referenceCorr = determine_key(referenceNotes, i)
            relevantNotes = notes_in_measure(noteList, i, i+measure_duration)
            newCorr = correlate(key_vectors[referenceKey],durations_to_array(get_durations(relevantNotes, i+measure_duration)))
            keyChange[i/measure_duration] = newCorr - referenceCorr
        else:
            referenceNotes = notes_in_measure(noteList, i-2*measure_duration,i)
            referenceKey, referenceCorr = determine_key(referenceNotes, i)
            relevantNotes = notes_in_measure(noteList, i, i+measure_duration)
            newCorr = correlate(key_vectors[referenceKey],durations_to_array(get_durations(relevantNotes, i+measure_duration)))
            keyChange[i/measure_duration] = newCorr - referenceCorr
#    logger.info( "Key change: %s" % (keyChange))
    return keyChange

def notes_in_measure(noteList, start, end):
    in_measure = []
    for note in noteList:
        if (note.time >= start) and (note.time < end):
            in_measure.append(note)                
        # we also need notes that started the previous measure and lingers into this one
        if (note.time < start) and (note.time + note.duration > start):
            in_measure.append(note)
    return in_measure
        
def determine_key(noteList, end):
    #    for note in noteList:
#        # if a note exceeds the measure boundary, just take the relevant part
#        duration = min(note.duration, end - note.time)
#        total_duration += duration
#        durations[midi_to_note(note.pitch)] += duration
#    durations = {note:dur/total_duration for note, dur in durations.items()}
    durations = get_durations(noteList, end)    
    max_correlation = -1.
    best_key = None
    for key, refVector in key_vectors.items():
        corr = correlate(refVector, durations_to_array(durations))
        if corr > max_correlation:
            max_correlation = corr
            best_key = key
    return best_key, max_correlation
        
def get_durations(noteList, end):
    durations = {note: 0. for note in notes}
    for note in noteList:
        # if a note exceeds the measure boundary, just take the relevant part
        duration = min(note.duration, end - note.time)
        durations[midi_to_note(note.pitch)] += duration
    total_duration = sum(durations.values())
    durations = {note:(dur/total_duration) for note, dur in durations.items()}
    return durations

def correlate(vector1, vector2):
#    print vector1, vector2
    vector1_average = sum(vector1)/12.
    vector2_average = sum(vector2)/12.
    nominator = 0.
    denominator1 = denominator2 = 0.
    for v1, v2 in zip(vector1, vector2):
        v1diff = v1-vector1_average
        v2diff = v2-vector2_average
        nominator += v1diff * v2diff
        denominator1 += v1diff ** 2
        denominator2 += v2diff ** 2
#        print v1diff, v2diff
#    print denominator1, denominator2
    denominator = math.sqrt(denominator1 * denominator2)
    return nominator / denominator
    
if __name__ == "__main__":
#    print CMaj
#    print rotate_array(CMaj,1)
#    print rotate_array(CMaj,2)
    from tools import midi as mid
    midi = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    track = midi.tracks[0]
    noteList = [noteEvent for noteEvent in track.eventList if noteEvent.type == "note"]
#    for i in range(0,6*960,960):
#        in_measure = notes_in_measure(noteList, i, i + 960)
#        print [midi_to_note(note.pitch) for note in in_measure]
#        print determine_key(in_measure, i+960)
    print analyze_key_change(midi)
        
#    for k in sorted(key_vectors.keys()):
#        print "%012s: %s" % (k,key_vectors[k])
    
    