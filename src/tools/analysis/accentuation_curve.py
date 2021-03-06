'''
Created on 15 Oca 2012

@author: Kerem
'''
from tools.analysis.key_change import note_find_measure


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
    
    try:
        assert len(accents) == len(metrics)
    except AssertionError:
        print len(accents), accents
        print len(metrics), metrics
        exit(1)
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

    
    return accentuation_curve

if __name__ == "__main__":
    from tools import midi as mid
    from tools.analysis import lbdm, metric_structure, melodic_accent, key_change
    performance = mid.prepare_initial_midi("../../../res/midi_text.txt", "../../../res/sample.midi", 15200)
    group_structure = lbdm.getNoteGroups(performance)
    tempo_events = [(event.time, event.tempo) for event in performance.tracks[0].eventList if event.type == "tempo"]
    notes = [event for event in performance.tracks[0].eventList if event.type == "note"]
    nominal_tempo = 3947
    nominal_loudness = 100
    melodic_accent = melodic_accent.analyze_melodic_accent(performance)
    metric_structure, metrical_scores = metric_structure.getMetricStructure(performance)
    key = key_change.analyze_key_change(performance)
    accentuation = accentuation_curve(melodic_accent, metrical_scores, key, notes)
    from matplotlib import pyplot as plt
    plt.plot(range(len(accentuation)), accentuation)
    plt.show()