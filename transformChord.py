"""
Tranform chords to Markus/ Jack's version and save to multiple files. 1: All chords, 2: Markus, 3: Jack
"""

import numpy as np
from generateChords import getCombinations
from fretboard_mapgen import mapgen
import pandas as pd

def encodeFretArray(fretArray, stringArray):
    """
    Encode fret array based on string array
    """
    encodedFretArray = ['X'] * 6
    for i, s in enumerate(stringArray):
        encodedFretArray[int(s)-1] = fretArray[i]
    return encodedFretArray

def addMetaDataConfig(root, chordType, encodedFretArray, index):
    """
    Add metadata to encoded fret array
    """
    array = [root]
    array.append(chordType)
    array.append(index)
    array.extend(encodedFretArray)
    numStrings = 6 - encodedFretArray.count('X')
    array.append(numStrings)
    return array

def addMetaDataChord(root, chordType, fmap, smap,):
    """
    Add metadata to encoded fret array
    """
    md_chord = []
    fpos_all, spos_all, _ = getCombinations(root, chordType, fmap, smap)
    index = 0
    for i, f in enumerate(fpos_all):
        s = spos_all[i]
        encodedFretArray = encodeFretArray(f, s)
        array = addMetaDataConfig(root, chordType, encodedFretArray, index)
        index += 1
        md_chord.append(array)
    print (len(md_chord))

def genAllChords(roots, chordTypes, fmap, smap):
    """
    Generate all chords from a list of given roots and chordTypes
    """
    all_chords = []
    for root in roots:
        for chordType in chordTypes:
            print (f'{root}{chordType}')
            fpos_all, spos_all, _ = getCombinations(root, chordType, fmap, smap)
            index = 0
            for i, f in enumerate(fpos_all):
                s = spos_all[i]
                encodedFretArray = encodeFretArray(f, s)
                array = addMetaDataConfig(root, chordType, encodedFretArray, index)
                all_chords.append(array)
                index += 1
    
    return all_chords

def createDF(all_chords_metadata):
    df = pd.DataFrame(all_chords_metadata, columns=['Root', 'ChordType', 'Index', 'String1', 'String2', 'String3', 'String4', 'String5', 'String6', 'NumStrings'])
    return df

def savedf(df, filename):
    df.to_csv(filename, index=False)


if __name__ == '__main__':
    fmap, smap = mapgen()
    roots = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    # roots = ['A#']
    chordTypes = ['Major', 'Minor', 'Dom7', 'Major7', 'Minor7']
    
    # Generate all data for one chord
    # addMetaDataChord('A', 'Minor', fmap, smap)


    # Generate all chords for given roots and chordTypes
    all_chs = genAllChords(roots, chordTypes, fmap, smap)
    df = createDF(all_chs)
    savedf(df, 'all_chords.csv')