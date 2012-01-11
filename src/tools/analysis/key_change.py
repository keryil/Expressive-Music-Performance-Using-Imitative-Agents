'''
Created on Jan 11, 2012

@author: kerem

Implements the key detection algorithm by Krumhansl 2001
'''
import math


CMaj = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
CMin = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
notes = ("C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B")
rotate_array = lambda x,t: x[-t:] + x[:-t]

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
    pass

def correlate(vector1, vector2):
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
    denominator = math.sqrt(denominator1 * denominator2)
    return nominator / denominator
    
if __name__ == "__main__":
#    print CMaj
#    print rotate_array(CMaj,1)
#    print rotate_array(CMaj,2)
    for k in sorted(key_vectors.keys()):
        print "%012s: %s" % (k,key_vectors[k])
    
    