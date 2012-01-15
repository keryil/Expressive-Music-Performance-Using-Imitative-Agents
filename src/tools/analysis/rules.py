'''
Created on 15 Oca 2012

@author: Kerem
'''

#from math import fabs as abs
from tools import midi as mid
from tools.analysis import lbdm, melodic_accent, metric_structure, key_change
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

def accentuation_curve(melodic_accent, metrical_scores, key_change, notes, maxVal=10., minVal=0.):
    """
    Normalizes the three curves and produces a weighted sum from them, normalized to between
    minVal and maxVal
    """
    w_melodic = 0.34
    w_metric = 0.33
    w_key_change = 0.33
    # take the abs values of key change values
    from math import fabs
    keys = [fabs(change) for change in key_change]
    
    accents = [float(accent) * maxVal / max(melodic_accent) for accent in melodic_accent]
    metrics = [float(score) * maxVal / float(max(metrical_scores)) for score in metrical_scores]
    keys = [float(change) * maxVal / max(keys) for change in keys]
#    print melodic_accent
#    print accents
#    print len(accents)
#    print metrical_scores
#    print metrics
#    print len(metrics)
#    print key_change
#    print keys
#    print len(keys)
    accentuation_curve = [w_melodic * melodic + w_metric * metric for melodic, metric in zip(accents, metrics)]
    
#    print accentuation_curve
    keys_final = []
    for i in range(len(notes)):
        note = notes[i]
#        print i, note_find_measure(note)
        accentuation_curve[i] += w_key_change * keys[note_find_measure(note)]
        keys_final.append(keys[note_find_measure(note)])
#    print keys_final
#    print accentuation_curve

#    from matplotlib import pyplot as plt
#    plt.plot(range(len(accentuation_curve)), accentuation_curve)
#    plt.show()
    return accentuation_curve
    
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

def rule3():
    pass
def rule4():
    pass
def rule5(group_structure, nominal_tempo, tempo_events):
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
    performance = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    group_structure = lbdm.getNoteGroups(performance)
    tempo_events = [(event.time, event.tempo) for event in performance.tracks[0].eventList if event.type == "tempo"]
    nominal_tempo = 3947
    nominal_loudness = 100
    print "Rule 1 tempo: %d" % rule1_tempo(group_structure, nominal_tempo, tempo_events)
    print "Rule 1 loudness: %d" % rule1_loudness(group_structure, nominal_loudness)
    print "Rule 2: %d" % rule2(group_structure, nominal_tempo, tempo_events)
    print "Rule 5: %d" % rule5(group_structure, nominal_tempo, tempo_events)
    metric_structure, metric_scores = metric_structure.getMetricStructure(performance)
    accentuation_curve(melodic_accent.analyze_melodic_accent(performance), metric_scores, key_change.analyze_key_change(performance), [note for note in performance.tracks[0].eventList if note.type == "note"])
