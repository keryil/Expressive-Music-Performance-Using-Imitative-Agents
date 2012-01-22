'''
Created on 10 Oca 2012

@author: Kerem
'''
from midiutil.MidiFile import MIDIFile
import re
from copy import deepcopy

LINE_REGEX = re.compile("^(?P<time>\d+) (?P<on_off>(On|Off)).*n=(?P<pitch>\d+).*v=(?P<volume>\d+)")

def prepare_initial_midi(text, out, tempo):
        midi = MIDIFile(1)
        midi.tracks[0].addTempo(time=0, tempo=tempo)
        midiText = open(text)
        duration = -1
        pitch = volume = time = -1
        for line in midiText:
            line = line.rstrip()
            m = LINE_REGEX.search(line)
            if m.group("on_off") == "On":
                pitch = int(m.group("pitch"))
                volume = int(m.group("volume"))
                time = int(m.group("time"))
                duration = time
            else:
                time2 = int(m.group("time"))
                duration = (float(time2)-float(time))
                midi.addNote(0, 0, pitch, time, duration, volume)
#                print "Added p: %d t: %d d: %f v: %d" % (pitch,time,duration,volume)
                duration = -1
        midi_to_write = deepcopy(midi)
        midi_to_write.writeFile(open(out,"w"))
        return midi

def translate_tempo(tempo):
    return 60000000 / tempo
    
#midi = prepare_initial_midi("../../res/midi_text.txt", "../../res/sample.mid", 60000000 / 3947)
#print [(event.time, event.tempo) for event in midi.tracks[0].eventList if event.type == "tempo"]
#midi.tracks[0].addTempo(time=100, tempo=60000000 / 66666)
#print [(event.time, event.tempo) for event in midi.tracks[0].eventList if event.type == "tempo"]