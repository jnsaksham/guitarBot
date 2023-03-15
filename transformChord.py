"""
Tranform chords to Markus/ Jack's version and save to multiple files. 1: All chords, 2: Markus, 3: Jack
"""

import numpy as np
from generateChords import getCombinations
from fretboard_mapgen import mapgen, fretToNote
import pandas as pd
import os
from dict_maps import tuning, note_midi_dict, chord_interval_dict


def checkInversion(fretArray, stringArray, root, tuning):
    """
    Check if the chord is an inversion.
    return 0 if root = lowest note, return 1 if inversion
    """
    # Find the lowest note played on min of (numNotes, 3) strings and check if it is the root
    least_note = 127
    for i, f in enumerate(fretArray[:3]):
        currentNote = fretToNote(f, stringArray[i], tuning)
        least_note = min(least_note, currentNote)
    
    if least_note in note_midi_dict[root]:
        return 0
    else:
        return 1

def encodeFretArray(fretArray, stringArray, root, tuning):
    """
    Encode fret array based on string array
    """
    encodedFretArray = ['X'] * 6
    for i, s in enumerate(stringArray):
        encodedFretArray[int(s)-1] = fretArray[i]
    inversion_tmp = checkInversion(fretArray, stringArray, root, tuning)
    return encodedFretArray, inversion_tmp

# Write a function decodeFretArray to decode encodedFretArray back to fretArray and stringArray
def decodeFretArray(encodedFretArray):
    """
    Decode encoded fret array
    """
    fretArray = []
    stringArray = []
    for i, f in enumerate(encodedFretArray):
        if f == 'X':
            continue
        else:
            fretArray.append(f)
            stringArray.append(i+1)
    return fretArray, stringArray


def addMetaDataConfig(root, chordType, encodedFretArray, index, inversion):
    """
    Add metadata to encoded fret array
    """
    array = [root]
    array.append(chordType)
    array.append(index)
    array.extend(encodedFretArray)
    numStrings = 6 - encodedFretArray.count('X')
    array.append(numStrings)
    array.append(inversion)
    return array

# def addMetaDataChord(root, chordType, fmap, smap, tuning):
#     """
#     Add metadata to encoded fret array
#     """
#     md_chord = []
#     fpos_all, spos_all, _ = getCombinations(root, chordType, fmap, smap)
#     index = 0
#     for i, f in enumerate(fpos_all):
#         s = spos_all[i]
#         encodedFretArray, inversion_bool = encodeFretArray(f, s, root, tuning)
#         array = addMetaDataConfig(root, chordType, encodedFretArray, index, inversion_bool)
#         index += 1
#         md_chord.append(array)
#     print (len(md_chord))

def genAllChords(roots, chordTypes, fmap, smap, tuning):
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
                encodedFretArray, inversion_bool = encodeFretArray(f, s, root, tuning)
                array = addMetaDataConfig(root, chordType, encodedFretArray, index, inversion_bool)
                all_chords.append(array)
                index += 1
    
    return all_chords

def createDF(all_chords_metadata):
    df = pd.DataFrame(all_chords_metadata, columns=['Root', 'ChordType', 'Index', 'String1', 'String2', 'String3', 'String4', 'String5', 'String6', 'NumStrings', 'Inversion'])
    return df

def savedf(df, filename):
    df.to_csv(filename, index=False)

def filterDFbyNumstrings(df, numStrings):
    if numStrings == '*':
        return df
    else:
        df = df[df['NumStrings'] == numStrings]
        return df

def filterDFbyInversion(df, inversion):
    if inversion == '*':
        return df
    else:
        df = df[df['Inversion'] == inversion]
        return df


def transformDFtoIndexable(folderName, filename, numStrings, inversion=0):
    filename = os.path.join(folderName, filename)
    df = pd.read_csv(f'{filename}.csv', index_col=False)
    df = filterDFbyNumstrings(df, numStrings)
    df = filterDFbyInversion(df, inversion)
    
    cols = df.columns.tolist()
    # cols = cols[:2] + cols[3:] + cols[2:3]
    # df = df[cols]
    return df

if __name__ == '__main__':
    fmap, smap = mapgen()
    roots = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    chordTypes = list(chord_interval_dict.keys())
    groupByNumStrings = 6
    inversion = 0

    # Generate all chords for given roots and chordTypes
    all_chs = genAllChords(roots, chordTypes, fmap, smap, tuning)
    df = createDF(all_chs)
    folderName = 'chord_databases'
    fname = 'all_chords_9frets_v2'
    fpath = os.path.join(folderName, f'{fname}.csv')
    savedf(df, fpath)
    df = transformDFtoIndexable(folderName, fname, groupByNumStrings, inversion)
    fpath = os.path.join(folderName, f'{fname}_{groupByNumStrings}str_inv{inversion}.csv')
    savedf(df, fpath)
