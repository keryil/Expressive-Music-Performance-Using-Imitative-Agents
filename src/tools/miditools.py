'''
Created on 10 Oca 2012

@author: Kerem
'''
from midiutil.MidiFile import MIDIFile
import re

LINE_REGEX = re.compile("^(?P<time>\d+) (?P<on_off>(On|Off)).*n=(?P<pitch>\d+).*v=(?P<volume>\d+)")

def prepare_initial_midi(tempo):
        midi = MIDIFile(1)
        midi.addTempo(track=0, time=0, tempo=tempo)
        midiText = open("midi_text.txt")
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
        midi.writeFile(open("sample.midi","w"))
        return midi