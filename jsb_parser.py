import numpy as np
import os, glob, time


def load_pkl(dsPath):
    with open(dsPath, 'rb') as p:
        data = pickle.load(p, encoding="latin1")
    return data

def load_npz(path):
    b = np.load(path, allow_pickle = True, encoding='bytes')
    return b


def extract_voicing(chorale, vtype):
    """
    chorale = any chorale with 4-part voicing. Shape = (n, 4)
    vtype = ['s', 'a', 't', 'b']
    """
    if vtype == 's':
        melody = chorale[:, 0]
    elif vtype == 'a':
        melody = chorale[:, 1]
    elif vtype == 't':
        melody = chorale[:, 2]
    elif vtype == 'b':
        melody = chorale[:, 3]
    else:
        print ('select a valid vtype: s/a/t/b')
    
    # Ensure that the pitches are within bot's playable range
    melody = pitch_fix(melody)
    
    return melody 

def pitch_fix(array, lowest=40, highest=73):
    # Wrap pitches in the permissible ranges
    final_array = []
    for midiNote in array:
        if midiNote > highest:
            i = (midiNote-highest)//12
            midiNote = midiNote-(i+1)*12
        if midiNote < lowest:
            i = (lowest-midiNote)//12
            midiNote = midiNote + (i+1)*12
        final_array.append(midiNote)
    return final_array

# Find locations of changes:
def notemap_voicing(array):
    """
    Generates an array to trigger the right hand 

    Rule:
    - play at 1 if pitch isn't NaN
    - Find all the changes
    - handle NaN
    
    Stage 2-
        - If any phrase is more than 8 16th notes, then group them into quarters before splitting the note further
    """
    
    diff = np.nonzero(np.diff(array))[0]+1
    # Add first pluck if first note isn't NaN
    if array[0] != 'NaN':
        diff = np.append(0, diff)
    diff = [int(d) for d in diff]
    return diff

def note_dur(array, tempo):
    """
    Generates an array consisting note durations in seconds
    array: melody of one voice
    """
    notemap = notemap_voicing(array)
    print (notemap)
    delta = np.diff(notemap)
    step_size = 60/(tempo*4)
    notesDur = [d*step_size for d in delta]
    return notesDur

## Define note to fretboard mapping
def get_fretboard_states(array, bot_string_map):
    """
    Returns a fretboard len(array)x6 dimensions map for all the midi numbers in the array
    Current rule:
    - We always play the bass notes on top 3 strings.
    - Treble notes: Bottom 2 strings.
    """
    states = []
    string_nums = []
    for i, midiNum in enumerate(array):
        if  39 < midiNum <= 45:
            string_num = bot_string_map.get('E')
            pos = midiNum-40 +1 # 1 is to adjust the position as per bot's setting
            state = [pos,0,0,0,0,0]
        elif 45 < midiNum <= 50:
            string_num = bot_string_map.get('A')
            pos = midiNum-45 +1 # 1 is to adjust the position as per bot's setting
            state = [0, pos, 0, 0, 0, 0]
        elif 50 < midiNum <= 59:
            string_num = bot_string_map.get('D')
            pos = midiNum-50 +1 # 1 is to adjust the position as per bot's setting
            state = [0, 0, pos, 0, 0, 0]
#         elif 54 < midiNum <= 58:
#             pos = midiNum-55 +1 # 1 is to adjust the position as per bot's setting
#             state = [0, 0, 0, pos, 0, 0]
        elif 58 < midiNum <= 63:
            string_num = bot_string_map.get('B')
            pos = midiNum-59 +1 # 1 is to adjust the position as per bot's setting
            state = [0, 0, 0, 0, pos, 0]
        elif midiNum >= 64:
            string_num = bot_string_map.get('e')
            pos = midiNum-64 +1 # 1 is to adjust the position as per bot's setting
            state = [0,0,0,0,0,pos]
        else:
            state = 'NaN'
            print (f'Found invalid note at {i}th location in the array')
        states.append(state)
        string_nums.append(string_num)
    return states, string_nums

def get_picking_states(string_nums, bot_picking_map, pickType='h'):
    """
    Inputs: onset beat,  fretboard states 
    pickType: Decides whether the whole voicing will be played via hammerOns or plucking.
    ## h(4) / o(1) / p(2) / g (glide)
    
    
    returns: 3D matrix of fret positions and pickStyle. shape n, 6, 6
    """
    style = bot_picking_map.get(pickType)
    final_map = []
    for i in np.arange(len(string_nums)):
        template = np.ones(6, dtype=int)
        template[string_nums[i]-1] = style
        final_map.append(template)
    return final_map

def get_onsets(onsets_bass, onsets_soprano):
    """
    onsets_bass = output of notemap_voicing(bass). Same for soprano. 
    """

    all_onsets = np.sort(np.array(onsets_bass + list(set(onsets_soprano) - set(onsets_bass))))

    # Common onsets: merge fretboard_state and picking_state
    common_onsets = np.sort(list(set(onsets_bass).intersection(onsets_soprano)))

    # Only bass
    bass_onsets = list(set(onsets_bass)-set(common_onsets))

    # Only soprano
    soprano_onsets = list(set(onsets_soprano)-set(common_onsets))
    

    return all_onsets, common_onsets, bass_onsets, soprano_onsets

def merge_fretboard_states(array1, array2):
    
    return list(np.array(array1) + np.array(array2))

def merge_picking_states(array1, array2):
    return list((np.array(array1) + np.array(array2))-1)

def get_final_masks(onsets_bass, onsets_soprano, fretboard_states_bass, fretboard_states_soprano, picking_states_bass, picking_states_soprano, tempo):
    
    all_onsets, common_onsets, bass_onsets, soprano_onsets = get_onsets(onsets_bass, onsets_soprano)
    final_dur_mask = np.diff(all_onsets)
    # Add half quarter note duration at the end to match array sizes
    final_dur_mask = np.append(final_dur_mask, 4)
    final_dur_mask = final_dur_mask*(60)/(tempo*4)
    
    final_pitch_mask = np.ones((len(all_onsets), 6))
    final_picking_mask = np.ones((len(all_onsets), 6))

    for onset in common_onsets:
        fs1 = fretboard_states_bass[onset]
        fs2 = fretboard_states_soprano[onset]
        index = np.where(all_onsets == onset)
        final_pitch_mask[index] = merge_fretboard_states(fs1, fs2)
        # final_pitch_mask[index] = [int(f) for f in final_pitch_mask[index]]
        ps1 = picking_states_bass[onset]
        ps2 = picking_states_soprano[onset]
        final_picking_mask[index] = merge_picking_states(ps1, ps2)
        # final_picking_mask[index] = [int(f) for f in final_picking_mask[index]]

    for onset in bass_onsets:
        index = np.where(all_onsets == onset)
        final_pitch_mask[index] = fretboard_states_bass[onset]
        # final_pitch_mask[index] = [int(f) for f in final_pitch_mask[index]]
        final_picking_mask[index] = picking_states_bass[onset]
        # final_picking_mask[index] = [int(f) for f in final_picking_mask[index]]

    for onset in soprano_onsets:
        index = np.where(all_onsets == onset)
        final_pitch_mask[index] = fretboard_states_soprano[onset]
        # final_pitch_mask[index] = [int(f) for f in final_pitch_mask[index]]
        final_picking_mask[index] = picking_states_soprano[onset]
        # final_picking_mask[index] = [int(f) for f in final_picking_mask[index]]

    return final_pitch_mask, final_picking_mask, final_dur_mask


def play_notes(fretboard_states, pluck_states, note_durations, guitar_bot_udp, bot_picking_map, strumq):
    """
    Play the final sequence (after all voicings combined)
    """
    for i in np.arange(len(fretboard_states)):
        ifretnumber_tmp = fretboard_states[i]
        ifretnumber = [int(i) for i in ifretnumber_tmp]
        iplaycommand_tmp = pluck_states[i]
        iplaycommand = [int(i) for i in iplaycommand_tmp]
        guitar_bot_udp.send_msg_left(iplaycommand, ifretnumber)
        pluckStyle = bot_picking_map.get('p')
        if pluckStyle in iplaycommand:
            print (pluckStyle)
            string = iplaycommand.index(pluckStyle)
            strumq.put(string)
            print (string)
            print('plucked')

        print (iplaycommand, ifretnumber)
        time.sleep(note_durations[i])
        print (note_durations[i])

def play_chorale(chorale, tempo, bot_string_map, bot_picking_map, guitar_bot_udp, strumq):
    # Extract bass and soprano from given track and play on the guitarBot
    bass = extract_voicing(chorale, 'b')
    soprano = extract_voicing(chorale, 's')
    
    onsets_bass = notemap_voicing(bass)
    onsets_soprano = notemap_voicing(soprano)
    
    # Get fretboard states
    fretboard_states_bass, string_nums_bass = get_fretboard_states(bass, bot_string_map)
    fretboard_states_soprano, string_nums_soprano = get_fretboard_states(soprano, bot_string_map)

    # Get picking states
    picking_states_bass = get_picking_states(string_nums_bass, bot_picking_map, 'h')
    picking_states_soprano = get_picking_states(string_nums_soprano, bot_picking_map, 'p')
    
    final_pitch_mask, final_picking_mask, final_dur_mask = get_final_masks(onsets_bass, onsets_soprano, fretboard_states_bass, fretboard_states_soprano, picking_states_bass, picking_states_soprano, tempo)
    
    play_notes(final_pitch_mask, final_picking_mask, final_dur_mask, guitar_bot_udp, bot_picking_map, strumq)
