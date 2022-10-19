import numpy as np
import os, glob, time
from jsb_parser import get_fretboard_states, notemap_voicing, get_picking_states
from GuitarBotUDP import GuitarBotUDP

def load_npz(path):
    b = np.load(path) #, allow_pickle = True, encoding='bytes')
    return b

def get_final_masks(onsets, fretboard_states, picking_states, tempo):
    
    final_dur_mask = np.diff(onsets)
    # Add half quarter note duration at the end to match array sizes
    final_dur_mask = np.append(final_dur_mask, 4)
    final_dur_mask = final_dur_mask*(60)/(tempo*4)
    
    final_pitch_mask = np.ones((len(onsets), 6))
    final_picking_mask = np.ones((len(onsets), 6))

    for i, onset in enumerate(onsets):
        final_pitch_mask[i] = fretboard_states[onset]
        final_picking_mask[i] = picking_states[onset]

    return final_pitch_mask, final_picking_mask, final_dur_mask

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
        print ('select a valid vtype from s/a/t/b')
    
    # Ensure that the pitches are within bot's playable range
    melody = pitch_fix(melody)
    
    return melody 

def pitch_fix(array, lowest=41, highest=74):
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

def play_notes(fretboard_states, pluck_states, note_durations, guitar_bot_udp):
    """
    Play the final sequence (after all voicings combined)
    """
    numNotes = len(fretboard_states)
    for i in np.arange(numNotes):
        ifretnumber_tmp = fretboard_states[i]
        ifretnumber = [int(j) for j in ifretnumber_tmp]
        iplaycommand_tmp = pluck_states[i]
        iplaycommand = [int(k) for k in iplaycommand_tmp]
        print (iplaycommand)
        print (ifretnumber)
        guitar_bot_udp.send_msg_left(iplaycommand, ifretnumber)
        time.sleep(note_durations[i])

def play_chorale(chorale, tempo, bot_string_map, bot_picking_map, guitar_bot_udp):
    # Extract bass and soprano from given track and play on the guitarBot
    bass = extract_voicing(chorale, 'b')
    
    onsets_bass = notemap_voicing(bass)
    
    # Get fretboard states
    fretboard_states_bass, string_nums_bass = get_fretboard_states(bass, bot_string_map)

    # Get picking states
    picking_states_bass = get_picking_states(string_nums_bass, bot_picking_map, 'h')
    # print (len(picking_states_bass))
    final_pitch_mask, final_picking_mask, final_dur_mask = get_final_masks(onsets_bass, fretboard_states_bass, picking_states_bass, tempo)
    
    play_notes(final_pitch_mask, final_picking_mask, final_dur_mask, guitar_bot_udp)

if __name__ == "__main__":

    ## GuitarBot string map
    bot_string_map = {'E': 1, 'A': 2, 'D': 3, 'G': 4, 'B': 5, 'e': 6}

    ## GuitarBot picking map
    bot_picking_map = {'o': 1, 'h': 4, 'g': 5, 'p': 2, 'd': 3}

    ## Define note mappings
    # note_dict = {'C2': 36, 'C#2': 37, 'D2': 38, 'D#2': 39, 'E2': 40, 'F2': 41, 'F#2': 42, 'G2': 43, 'G#2': 44, 'A2': 45, 'A#2': 46, 'B2': 47, 'C3': 48, 'C#3': 49, 'D3': 50, 'D#3': 51, 'E3': 52, 'F3': 53, 'F#3': 54, 'G3': 55, 'G#3': 56, 'A3': 57, 'A#3': 58, 'B3': 59,'C4': 60, 'C#4': 61, 'D4': 62, 'D#4': 63, 'E4': 64, 'F4': 65, 'F#4': 66, 'G4': 67, 'G#4': 68, 'A4': 69, 'A#4': 70, 'B4': 71, 'C5': 72, 'C#5': 73, 'D5': 74, 'D#5': 75, 'E5': 76, 'F5': 77, 'F#5': 78, 'G5': 79, 'G#5': 80, 'A5': 81, 'A#5': 82, 'B5': 83}
    # note_dict = {v: k for k, v in note_dict.items()}

    fpath = 'Jsb16thSeparated.npz'
    setType = 'valid'
    idx = 7
    chorales = load_npz(fpath)
    chorale = chorales[setType][idx]
    tempo = 50

    UDP_IP = "192.168.1.50"
    UDP_PORT = 1001
    guitar_bot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    sleeptime = 4
    ROBOT = "xArms"
    PORT = 5004
    i = -1
    play_chorale(chorale, tempo, bot_string_map, bot_picking_map, guitar_bot_udp)