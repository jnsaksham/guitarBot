import pandas as pd
from chordPlayback import getSingleChordArray, getAllPossibilities, convert_df_to_chord_array, transform_to_fretnum_fretplay, shortlist
from dict_maps import fret_distances


def get_chords_M(directory, chord_letter, chord_type):
    df_chords = pd.read_csv(directory)
    for new_x in range(334):
        if df_chords.iloc[new_x][0] == chord_letter:
            if df_chords.iloc[new_x][1] == chord_type:
                x = new_x
                break
    ftraj = False
    dtraj = []
    utraj = []
    try:
        s1 = int(df_chords.iloc[x][3])
        dtraj = [0, 6]
        utraj = [6, 0]
        ftraj = True
    except:
        s1 = -1
    try:
        s2 = int(df_chords.iloc[x][4])
        if ftraj == False:
            dtraj = [1, 6]
            utraj = [6, 1]
            ftraj = True
    except:
        s2 = -1

    try:
        s3 = int(df_chords.iloc[x][5])
        if ftraj == False:
            dtraj = [2, 6]
            utraj = [6, 2]
            ftraj = True
    except:
        s3 = -1
    try:
        s4 = int(df_chords.iloc[x][6])
        if ftraj == False:
            dtraj = [3, 6]
            utraj = [6, 3]
            ftraj = True
    except:
        s4 = -1
    try:
        s5 = int(df_chords.iloc[x][7])
        if ftraj == False:
            dtraj = [4, 6]
            utraj = [6, 4]
            ftraj = True
    except:
        s5 = -1
    try:
        s6 = int(df_chords.iloc[x][8])
        if ftraj == False:
            dtraj = [5, 6]
            utraj = [6, 5]
            ftraj = True
    except:
        s6 = -1
    fret_numbers = [s1, s2, s3, s4, s5, s6]
    fret_play = []
    if fret_numbers[0] == 0:
        fret_numbers[0] += 1
        fret_play.append(1)
    elif fret_numbers[0] == -1:
        fret_numbers[0] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[1] == 0:
        fret_numbers[1] += 1
        fret_play.append(1)
    elif fret_numbers[1] == -1:
        fret_numbers[1] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[2] == 0:
        fret_numbers[2] += 1
        fret_play.append(1)
    elif fret_numbers[2] == -1:
        fret_numbers[2] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[3] == 0:
        fret_numbers[3] += 1
        fret_play.append(1)
    elif fret_numbers[3] == -1:
        fret_numbers[3] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[4] == 0:
        fret_numbers[4] += 1
        fret_play.append(1)
    elif fret_numbers[4] == -1:
        fret_numbers[4] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[5] == 0:
        fret_numbers[5] += 1
        fret_play.append(1)
    elif fret_numbers[5] == -1:
        fret_numbers[5] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)
    print(fret_numbers, fret_play)
    print(dtraj, utraj)
    return fret_numbers, fret_play, dtraj, utraj


def parseright_M(right_arm, measure_time):
    initialStrum = "D"
    firstbfound = False
    mra = 0
    pmra = 0
    pbra = 0
    deltaT = 0

    for measure in right_arm:
        bra = 0
        for beat in measure:
            if beat == "U" or beat == "D" or beat == "":
                if not firstbfound:
                    if beat == "D":
                        right_arm[mra][bra] = [beat, "N", measure_time / 8, 1]  # Change strum time here
                    if beat == "U":
                        right_arm[mra][bra] = [beat, "N", measure_time / 8, 1]  # Change strum time here
                    firstbfound = True
                    initialStrum = beat
                    pmra = mra
                    pbra = bra

                    bra += 1
                    deltaT += measure_time / 8
                    continue
                if beat == "U":
                    right_arm[mra][bra] = [beat, "N", measure_time / 8, deltaT]  # Change strum time here
                    if right_arm[pmra][pbra][0] == "U":
                        right_arm[pmra][pbra][1] = "C"
                    right_arm[pmra][pbra][3] = deltaT
                    pmra -= pmra
                    pmra += mra
                    pbra -= pbra
                    pbra += bra
                    deltaT = 0
                    # print(pmra, pbra)
                if beat == "D":
                    right_arm[mra][bra] = [beat, "N", measure_time / 8, deltaT]  # Change strum time here
                    if right_arm[pmra][pbra][0] == "D":
                        right_arm[pmra][pbra][1] = "C"
                    right_arm[pmra][pbra][3] = deltaT
                    pmra -= pmra
                    pmra += mra
                    pbra -= pbra
                    pbra += bra
                    deltaT = 0
            else:
                raise Exception("Right Arm input incorrect")
                    # print(pmra, pbra)
            bra += 1
            deltaT += measure_time / 8
        mra += 1
    right_information = right_arm
    # print("ri", right_information, initialStrum)
    return right_information, initialStrum


def parseleft_S(left_arm, df):
    firstc = []
    firstcfound = False
    mcount = 0
    for measure in left_arm:
        bcount = 0
        i = 0
        for chords in measure:
            if len(chords) != 0:
                key = chords.split(' ')[0]
                type = chords.split(' ')[1]

                if i == 0:
                    frets, command = getSingleChordArray(df, key, type, random=True)
                    i += 1

                else:
                    df_shortlisted = getAllPossibilities(df, key, type)
                    # Convert all possible chords to fretnum arrays
                    next_fretnum_all = convert_df_to_chord_array(df_shortlisted)
                    frets, command = shortlist(frets, next_fretnum_all, fret_distances)
                    
                left_arm[mcount][bcount] = [frets, command]
                if firstcfound == False:
                    firstc.append(frets)
                    firstc.append(command)
                    firstcfound = True
            bcount += 1
        mcount += 1
    
    return left_arm, firstc

def parseleft_M(left_arm):
    firstc = []
    firstcfound = False
    mcount = 0
    for measure in left_arm:
        bcount = 0
        for chords in measure:
            if len(chords) != 0:
                type = "MAJOR"
                key = chords[1]
                if chords[2:7] == "MAJOR":
                    type = "MAJOR"
                if chords[2:7] == "MINOR":
                    type = "MINOR"
                    # print("MINOR CHORD")
                if chords[2:8] == "MAJOR7":
                    type = "MAJOR7"
                    # print("MAJOR7 CHORD")
                if chords[2:8] == "MAJOR9":
                    type = "MAJOR9"
                    # print("MAJOR9 CHORD")
                if chords[2:8] == "MINOR9":
                    type = "MINOR9"
                    # print("MINOR9 CHORD")
                if chords[2:6] == "SUS2":
                    type = "SUS2"
                    # print("SUS2 CHORD")
                if chords[2:6] == "SUS4":
                    type = "SUS4"
                    # print("SUS4 CHORD")
                if chords[2:8] == "MAJOR6":
                    type = "MAJOR6"
                    # print("MAJOR6 CHORD")
                if chords[2:7] == "FIFTH":
                    type = "FIFTH"
                    # print("FIFTH CHORD")
                if chords[2:12] == "DIMINISHED":
                    type = "DIMINISHED"
                    # print("DIMINISHED CHORD")
                if chords[2:8] == "MINOR7":
                    type = "MINOR"
                    # print("MINOR CHORD")
                if chords[2:8] == "MINOR6":
                    type = "MINOR6"
                    # print("MINOR6 CHORD")
                if chords[2:10] == "HALF-DIM":
                    type = "HALF-DIM"
                    # print("HALF-DIM CHORD")
                if chords[2:10] == "DOMINANT":
                    type = "DOMINANT"
                    # print("DOMINANT CHORD")
                frets, command, dtraj, utraj = get_chords_M("Chords - Chords.csv", chords[0] + key, type)
                left_arm[mcount][bcount] = [frets, command]
                if not firstcfound:
                    firstc.append(frets)
                    firstc.append(command)
                    firstcfound = True
            bcount += 1
        mcount += 1
    # print(left_arm)
    return left_arm, firstc
