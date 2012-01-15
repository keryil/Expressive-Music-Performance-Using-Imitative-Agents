'''
Created on 15 Oca 2012

@author: Kerem
'''

#from math import fabs as abs
from tools import midi as mid
from tools.analysis import lbdm, melodic_accent, metric_structure, key_change,\
    accentuation_curve
from tools.analysis.key_change import note_find_measure



#def rule1(group_structure, nominal_tempo, nominal_loudness, tempo_events):
#    """
#    Receives the LBDM group structure, the nominal tempo and loudness of the piece and 
#    an array of (time, tempo) tuples for each tempo change in the piece, and returns a score
#    """
#    score = 0
#  
#    r1_tempo = rule1_tempo(group_structure, nominal_tempo, tempo_events)
#    r1_loudness = rule1_loudness(group_structure, nominal_loudness)
#    print "Rule 1: t: %d, l: %d"  % (r1_tempo, r1_loudness)
#    return score

def abs(n):
    return -n

    
def rule1_tempo(group_structure, nominal_tempo, tempo_events):
    """
    Receives the LBDM group structure, the nominal tempo of the piece and 
    an array of (time, tempo) tuples for each tempo change in the piece, and returns a score
    """
    score = 0
    for group in group_structure:
        first = group[0]
        turning = group[1]
        last = group[2]
        
        # process the first part
        for i in range(len(first) - 1):
            note = first[i]
            
            # find the tempo during this note
            tempo = None
            for time, temp in tempo_events:
                if time <= note.time:
                    tempo = temp
                if time == note.time:
                    break
            
            # find the next_note note and its tempo    
            next_note = None
            next_tempo = None
            if i == len(first):
                next_note = turning
            else:
                next_note = first[i + 1]
                
            for time, tempo in tempo_events:
                if time <= next_note.time:
                    next_tempo = tempo
                if time == next_note.time:
                    break
            
            # not sure about abs
            if(abs(nominal_tempo - next_tempo) > abs(nominal_tempo - tempo)):
                score += 1
        
        # process the last part
        last = [turning] + last
        for i in range(len(last) - 1):
            note = last[i]
            
            # find the tempo during this note
            tempo = None
            for time, temp in tempo_events:
                if time <= note.time:
                    tempo = temp
                if time == note.time:
                    break
            
            # find the next_note note and its tempo    
            next_note = None
            next_tempo = None
            if i == len(last):
                next_note = turning
            else:
                next_note = last[i + 1]
                
            for time, temp in tempo_events:
                if time <= next_note.time:
                    next_tempo = temp
                if time == next_note.time:
                    break
            
            # not sure about abs
            if(abs(nominal_tempo - next_tempo) <= abs(nominal_tempo - tempo)):
                score += 1
            
    return score
def rule1_loudness(group_structure, nominal_volume):
    score = 0
    for group in group_structure:
        first = group[0]
        turning = group[1]
        last = group[2]
        
        # process the first part
        for i in range(len(first) - 1):
            note = first[i]
           
            
            # find the next_note note   
            next_note = None
            if i == len(first):
                next_note = turning
            else:
                next_note = first[i + 1]
                
            # not sure about abs
            if(abs(nominal_volume - next_note.volume) > abs(nominal_volume - note.volume)):
                score += 1
        
        # process the last part
        last = [turning] + last
        for i in range(len(last) - 1):
            note = last[i]
            next_note = last[i + 1]
            
            # not sure about abs
            if(abs(nominal_volume - next_note.volume) <= abs(nominal_volume - note.volume)):
                score += 1
            
    return score

def rule2(group_structure, nominal_tempo, tempo_events):
    score = 0
    for group in group_structure:
        # go to the last note
        note = group[-1][-1]
        # find the tempo during this note
        tempo = None
        for time, temp in tempo_events:
            if time <= note.time:
                tempo = temp
            if time == note.time:
                break
        if tempo - nominal_tempo > 0:
            score += 1
#    print "Rule 2: %d" % score
    return score

def rule3(noteList, nominal_volume, accentuation_curve):
    """
    Rule 3: Loudness Emphasis
    Performance deviations for loudness should emphasise the metrical, 
    melodic, and harmonic structure (Clarke 1988; Sundberg et al. 1983).
    
    So, for each successful expression, we should expect 2 points. 
    Take midi_rule3_sample.txt: 
    
    >>> performance = mid.prepare_initial_midi("../../../res/midi_rule3_text.txt", "../../../res/sample_rule3.midi", 15200)
    >>> group_structure = lbdm.getNoteGroups(performance)
    >>> tempo_events = [(event.time, event.tempo) for event in performance.tracks[0].eventList if event.type == "tempo"]
    >>> notes = [event for event in performance.tracks[0].eventList if event.type == "note"]
    >>> nominal_loudness = 100
    >>> melodic_accent = melodic_accent.analyze_melodic_accent(performance)
    >>> metric_structure, metrical_scores = metric_structure.getMetricStructure(performance)
    >>> key = key_change.analyze_key_change(performance)
    >>> accentuation = accentuation_curve.accentuation_curve(melodic_accent, metrical_scores, key, notes)
    
    There are 2 increases in volume for two
    accentuated notes,so we should expect a score of 4.
    
    >>> rule3(notes, nominal_loudness, accentuation)
    4
    """
    assert len(noteList) == len(accentuation_curve)
    score = 0
    for i in range(len(noteList) - 1):
        lambda_d = accentuation_curve[i+1] - accentuation_curve[i]
        next_loudness_dev = noteList[i+1].volume - nominal_volume
        loudness_dev= noteList[i].volume - nominal_volume
        lambda_dev = next_loudness_dev - loudness_dev
        if lambda_dev * lambda_d > 0:
            score += 1
    return score

#def rule4():
#    pass

def rule4_tempo(notes, accentuation_curve, nominal_tempo, tempo_events):
    """
    Rule 4: Accentuation
    Any note at a significantly accentuated position (as defined later) must either 
    have a lengthened duration value or a local loudness maximum (Clarke 1988; Cambouropoulos 2001).
    """
    score = 0
    accentuated_note_indexes = []
    for i in range(len(accentuation_curve))[1:-1]:
        prev = accentuation_curve[i-1]
        nex = accentuation_curve[i+1]
        this = accentuation_curve[i]
        if this >= prev and this >= nex:
            accentuated_note_indexes.append(i)
    
    for i in accentuated_note_indexes:
        prev_tempo = None
        prev_note = notes[i-1]
        for time, temp in tempo_events:
            if time <= prev_note.time:
                prev_tempo = temp
            if time == prev_note.time:
                break
        prev_dev = prev_tempo - nominal_tempo
        
        
        tempo = None
        note = notes[i]
        for time, temp in tempo_events:
            if time <= note.time:
                tempo = temp
            if time == note.time:
                break
        dev = tempo - nominal_tempo
        
        next_tempo = None
        next_note = notes[i+1]
        for time, temp in tempo_events:
            if time <= next_note.time:
                next_tempo = temp
            if time == next_note.time:
                break
        next_dev = next_tempo - nominal_tempo
        if dev < next_dev and dev < prev_dev:
            score += 1
            
    return score

def rule4_loudness(notes,accentuation_curve, nominal_volume):
    """
    Rule 4: Accentuation
    Any note at a significantly accentuated position (as defined later) must either 
    have a lengthened duration value or a local loudness maximum (Clarke 1988; Cambouropoulos 2001).
    """
    score = 0
    accentuated_note_indexes = []
    for i in range(len(accentuation_curve))[1:-1]:
        prev = accentuation_curve[i-1]
        nex = accentuation_curve[i+1]
        this = accentuation_curve[i]
        if this >= prev and this >= nex:
            accentuated_note_indexes.append(i)
    
    for i in accentuated_note_indexes:
        prev_note = notes[i-1]
        prev_dev = prev_note.volume - nominal_volume
        
        note = notes[i]
        dev = note.volume - nominal_volume
        
        next_note = notes[i+1]
        next_dev = next_note.volume - nominal_volume
        if dev < next_dev and dev < prev_dev:
            score += 1
            
    return score

def rule5(group_structure, nominal_tempo, tempo_events):
    """
    Rule 5: Boundary Notes
    The last note in a note grouping should have an expressive 
    tempo, which is either a local minimum or local maximum (Clarke 1988).
    """
    score = 0
    for i in range(len(group_structure)):
        group = group_structure[i]
        note = group[-1][-1]
        tempo = None
        
        # find the tempo for current note
        for time, temp in tempo_events:
            if time <= note.time:
                tempo = temp
            if time == note.time:
                break
        
        prev_note = None
        prev_tempo = None
        
        try:
            prev_note = group[-1][-2]
        except IndexError:
            prev_note = group[-2]
        # find the tempo for previous note
        for time, temp in tempo_events:
            if time <= prev_note.time:
                prev_tempo = temp
            if time == prev_note.time:
                break
            
        next_note = None
        next_tempo = None
        
        try:
            next_note = group_structure[i + 1][0][0]
            # find the tempo for previous note
            for time, temp in tempo_events:
                if time <= next_note.time:
                    next_tempo = temp
                if time == next_note.time:
                    break
            if ((tempo - nominal_tempo) - (prev_tempo - nominal_tempo)) * ((tempo - nominal_tempo) - (next_tempo - nominal_tempo)):
                score += 1
        # we may hit the end of the score here
        except IndexError, err:
            print "End of score at %d?" % note.time
#            print err
        
    return score
    
if __name__ == '__main__':
#    performance = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    import doctest
    doctest.testmod()
    exit()
    
    performance = mid.prepare_initial_midi("../../../res/midi_rule3_text.txt", "../../../res/sample_rule3.midi", 15200)
    group_structure = lbdm.getNoteGroups(performance)
    tempo_events = [(event.time, event.tempo) for event in performance.tracks[0].eventList if event.type == "tempo"]
    notes = [event for event in performance.tracks[0].eventList if event.type == "note"]
    nominal_tempo = 3947
    nominal_loudness = 100
    melodic_accent = melodic_accent.analyze_melodic_accent(performance)
    metric_structure, metrical_scores = metric_structure.getMetricStructure(performance)
    key = key_change.analyze_key_change(performance)
    accentuation = accentuation_curve.accentuation_curve(melodic_accent, metrical_scores, key, notes)
    print "Rule 1 tempo: %d" % rule1_tempo(group_structure, nominal_tempo, tempo_events)
    print "Rule 1 loudness: %d" % rule1_loudness(group_structure, nominal_loudness)
    print "Rule 2: %d" % rule2(group_structure, nominal_tempo, tempo_events)
    print "Rule 3: %d" % rule3(notes, nominal_loudness, accentuation)
    print "Rule 4 tempo: %d" % rule4_tempo(notes, accentuation, nominal_tempo, tempo_events)
    print "Rule 4 loudness: %d" % rule4_loudness(notes, accentuation, nominal_loudness)
    print "Rule 5: %d" % rule5(group_structure, nominal_tempo, tempo_events)
#    accentuation_curve(melodic_accent.analyze_melodic_accent(performance), metric_scores, key_change.analyze_key_change(performance), [note for note in performance.tracks[0].eventList if note.type == "note"])
    print "Rule 5: %d" % rule5(group_structure, nominal_tempo, tempo_events)
    metric_structure, metric_scores = metric_structure.getMetricStructure(performance)
    accentuation_curve(melodic_accent.analyze_melodic_accent(performance), metric_scores, key_change.analyze_key_change(performance), [note for note in performance.tracks[0].eventList if note.type == "note"])
