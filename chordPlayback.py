import numpy as np
import pandas as pd

def getSingleChordArray(df, root, chordType, random=True):
    if random == True:
        # From df, get all rows with root and chordType
        # print (root, chordType)
        df = getAllPossibilities(df, root, chordType)
        # print (len(df))
        array = select_random_chord(df)
        
    fretnum, fretplay = transform_to_fretnum_fretplay(array)
    return fretnum, fretplay


def generate_chord_trajectory(roots, chordTypes, df):
    """
    Generate the whole left hand trajectory for any given chord progression
    
    Inputs
    roots: all roots in the sequence. Includes repetitions too. eg - [CM, Am] x 2 = [C, C, A, A]
    chordTypes: all chordTypes in the sequence. Includes repetitions too. eg - [CM, Am] x 2 = [Major, Major, minor, minor]
    df: dataframe containing all chords (vocabulary)

    Outpus
    ifretnums: length = len(chord_progression)
    iplaynums: length = len(chord_progression)

    """
    ifretnums = []
    ifretplays = []
    
    # Select the first chord at random
    current_fretnum, current_fretplay = getSingleChordArray(df, roots[0], chordTypes[0], random=True)
    prev_fretnum = current_fretnum
    ifretnums.append(current_fretnum)
    ifretplays.append(current_fretplay)

    for i in range(1, len(roots)):
        # Get all possible chords corresponding to the next chord
        df = getAllPossibilities(df, roots[i], chordTypes[i])

        # Convert all possible chords to fretnum arrays
        next_fretnum_all = convert_df_to_chord_array(df)

        # Get the most optimised chord based on distance based cost function
        next_fretnum = shortlist(prev_fretnum, current_fretnum, next_fretnum_all)

        ifretnum, ifretplay = transform_to_fretnum_fretplay(next_fretnum)
        ifretnums.append(ifretnum)
        ifretplays.append(ifretplay)
        prev_fretnum = current_fretnum
        current_fretnum = next_fretnum

    return ifretnums, ifretplays

def convert_df_to_chord_array(df):
    """
    Get all chords from the dataframe
    """
    all_chords = []
    for i in range(len(df)):
        all_chords.append(df.values[i][3:9])
    return all_chords

def getAllPossibilities(df, root, chordType):
    """
    Get a dataframe containing all chords for given root and chordType
    """
    return df[(df['Root'] == root) & (df['ChordType'] == chordType)]

def transform_to_fretnum_fretplay(array):
    fretnum = []
    fretplay = []
    for i in array:
        if i == 'X':
            fretplay.append(3)
            fretnum.append(5)
        
        elif int(float(i)) == 0:
            fretplay.append(1)
            fretnum.append(5)

        else:
            fretplay.append(2)
            fretnum.append(int(float(i)))
    return fretnum, fretplay

def select_random_chord(df):
    index = np.random.randint(0, len(df))
    return df.values[index][3:9]


def shortlist(prev_state, curr_state, potential_state):
    ifretnum = []
    # Loop through all potential states
    for i in range(len(potential_state)):
        # Get the distance between the current state and the potential state
        dist = compute_cost(prev_state, curr_state, potential_state[i])
        ifretnum.append(dist)

    return ifretnum

def compute_cost(prev_state, curr_state, potential_state):
    """
    Compute the distance between the current state and the potential state. Rules for computing distance:
    1. If current state has no 'X' and potential state has 'X' at >=1 positions, then distance = 0 for positions with 'X', otherwise distance = abs(potential_state[i] - curr_state[i])
    2. If current state has 'X' at >=1 positions, then distance = 0 for positions with 'X', otherwise distance = abs(potential_state[i] - prev_state[i])
    """
    
    dist = 0
    for i in range(len(curr_state)):
        if curr_state[i] != 'X':
            if potential_state[i] == 'X':
                dist += 0
            else:
                dist += abs(int(float(curr_state[i])) - int(float(potential_state[i])))
        else:
            if prev_state[i] == 'X' and potential_state[i] == 'X':
                dist += 0
            elif prev_state[i] == 'X' and potential_state[i] != 'X':
                dist += abs(int(float(potential_state[i])))
            else:
                dist += abs(int(float(potential_state[i])) - int(float(prev_state[i])))
    return dist