import numpy as np
import pandas as pd

def getSingleChordArray(df, root, chordType, random=True):
    if random == True:
        # From df, get all rows with root and chordType
        print (root, chordType)
        df = df[(df['Root'] == root) & (df['ChordType'] == chordType)]
        print (len(df))
        # Pick a random row
        index = np.random.randint(0, len(df))
        array = df.values[index][3:9]
        
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