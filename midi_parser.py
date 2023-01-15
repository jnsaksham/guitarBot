from calendar import c
import numpy as np
import os, glob
from mido import MidiFile
import mido
from jsb_parser import get_fretboard_states, get_picking_states, play_notes
from fretboard_mapgen import mapgen, gen_poly_states, limit_pitches
from pluck_mapgen import rightHand
import time

"""
Steps-
- Read MIDI file - Done
- Unpack into pitch, vel and time arrays - Done
- Clean pitch to fir bot's range - Done
- Clean time array to remove '1's
    - Add 1s to get the total wait durs
- Convert time to duration taking into account tempo
- Align time array with vel and note
- Convert time to seconds
- Define offsetstates - template
- Define offsetstates - bot trigger
- Output fretboardstates, onsetstates and offsetstates, durationstates (onset and offset) in bot-readable format
"""

## GuitarBot string map
bot_string_map = {'E': 1, 'A': 2, 'D': 3, 'G': 4, 'B': 5, 'e': 6}

## GuitarBot picking map
bot_picking_map = {'o': 1, 'h': 4, 'g': 5, 'p': 2, 'd': 3}

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

def timeTrackSeconds(timetrack, tempo, tpb):
    """
    Generate timetrack in seconds from the extracted timetrack
    inputs:
        - timetrack (originally extracted ticks)
        - tempo in microseconds per beat
        - tpb: ticks per beat
        - returns: Array of timestamps appearing in the timetrack
    """
    timetrack = np.cumsum(timetrack)
    seconds = mido.tick2second(timetrack, int(tpb), int(tempo))
    return seconds
    

def getTimeTrack(track):
    """
    Returns all the time values in the array
    """
    msg_types = ['note_on', 'note_off']
    timetrack = np.array([])
    for msg in track:
        if msg.type in msg_types:
            timetrack = np.append(timetrack, msg.time)
    return timetrack

def getPitchTrack(track):
    """
    Returns all the pitch values in the array
    """
    msg_types = ['note_on', 'note_off']
    pitchtrack = np.array([])
    for msg in track:
        if msg.type in msg_types:
            pitchtrack = np.append(pitchtrack, msg.note)
    return pitchtrack

def getVelTrack(track):
    """
    Returns all the velocity values in the array
    """ 
    msg_types = ['note_on', 'note_off']
    veltrack = np.array([])
    for msg in track:
        if msg.type in msg_types:
            veltrack = np.append(veltrack, msg.velocity)  
    return veltrack

def getMIDIInfo(track):
    timetrack = getTimeTrack(track)
    pitchtrack = getPitchTrack(track)
    veltrack = getVelTrack(track)
    return timetrack, pitchtrack, veltrack

def genOnsetOffsetmasks(timetrack, pitchtrack, veltrack):
    """
    Generate onset and offset masks using timetrack in seconds, clean pitch track and velocity track
    Returns: onset mask and offset mask
    """
    onset_mask = []
    offset_mask = []

    # Get onset timestamps from timetrack
    for i, vel in enumerate(veltrack):
        if vel > 0:
            onset_mask.append(timetrack[i])
        else:
            offset_mask.append(timetrack[i])

    return onset_mask, offset_mask

def genWrapper(fpath, tempoBPM):
    tempo = mido.bpm2tempo(tempoBPM)
    mid = MidiFile(fpath)
    timetrack = []
    pitchtrack = []
    veltrack = []
    for track in mid.tracks:
        # track = mid.tracks[0]
        tpb = mid.ticks_per_beat
        ttrack, ptrack, vtrack = getMIDIInfo(track)
        if len(ptrack > 0):
            timetrack.append(ttrack)
            pitchtrack.append(ptrack)
            veltrack.append(vtrack)

    pitchtrack = pitchtrack[0]
    timetrack = timetrack[0]
    veltrack = veltrack[0]
    
    # Fix pitch to not exceed 10th fret. 9th in case of hammer-on
    pitchtrack = pitch_fix(pitchtrack)

    # Convert time to seconds
    timetrack = timeTrackSeconds(timetrack, tempo, tpb)

    return timetrack, pitchtrack, veltrack

def getPitchMask(pitchtrack, veltrack):
    onset_pitches = []
    offset_pitches = []
    for i, vel in enumerate(veltrack):
        if vel > 0:
            onset_pitches.append(pitchtrack[i])
        else:
            offset_pitches.append(pitchtrack[i])
    return onset_pitches, offset_pitches

def playMonophony(onset_mask, pitchtrack, veltrack, guitar_bot_udp, bot_picking_map, bot_string_map):
    """
    Only works for midi files with monophonic melody. No chords or anything.
    """
    # Get onset duration array
    # print (f'onset_mask: {onset_mask}')
    onset_duration = np.diff(onset_mask)
    # print (f'onset_duration: {onset_duration}')
    onset_duration = np.append(onset_duration, onset_duration[-1])
    
    # Get onset pitch array
    onset_pitches, offset_pitches = getPitchMask(pitchtrack, veltrack)
    onset_fretboard_states, onset_string_nums = get_fretboard_states(onset_pitches, bot_string_map)
    onset_picking_states = get_picking_states(onset_string_nums, bot_picking_map, 'p')

    play_notes(onset_fretboard_states, onset_picking_states, onset_duration, guitar_bot_udp)

def rollupTracks(timetrack, pitchtrack, veltrack):
    timestamps = np.unique(timetrack)
    pitches = []
    vels = []
    
    # generate onset and offset masks
    onset_mask = []
    
    for i, t in enumerate(timestamps):
        # print (f't: {t}')
        locs = np.where(timetrack==t)[0]
        pitches_ts = pitchtrack[locs]
        pitches_unique = np.unique(pitches_ts)
        # Limit pitches to 6
        pitches_unique_limited = limit_pitches(pitches_unique)
        # print (f'i: {i}, t: {t}, pitches_unique: {pitches_unique}')
        pitches.append(pitches_unique_limited)
        vel_ts = veltrack[locs][0]
        vels.append(vel_ts)
        if vel_ts > 0:
            # Onset
            onset_mask.append(True)
        else:
            # Offset
            onset_mask.append(False)

    return timestamps, pitches, vels

def durfromTimestamp(timestamps):
    durations = np.diff(timestamps)
    durations = np.append(durations, durations[-1])
    return durations

def get_indices(array, val):
    arr = []
    for a in array:
        if a == val:
            arr.append(a)
    return np.array(a)



def play_notes(i, fretboard_states, pluck_states, note_duration, vel, pitch, guitar_bot_udp, bot_picking_map, strumq):
    """
    Play the final sequence (after all voicings combined)
    """
    ifretnumber_tmp = fretboard_states
    ifretnumber = [int(j) for j in ifretnumber_tmp]
    iplaycommand_tmp = pluck_states
    iplaycommand = [int(j) for j in iplaycommand_tmp]

    # print(f'iplaycommand: {iplaycommand}')
    # print (f'ifretnumber: {ifretnumber}')
    # print (f'pitch {pitch}')
    # print (f'note_duration: {note_duration} s')
    # print ('-----------')

    rightHand(iplaycommand, ifretnumber, guitar_bot_udp, strumq, note_duration)


def playPolyphony(durations, fretboard_states, string_states, vels, pitches, guitar_bot_udp, strumq):
    for i, dur in enumerate(durations):
        play_notes(i, fretboard_states[i], string_states[i], durations[i], vels[i], pitches[i], guitar_bot_udp, bot_picking_map, strumq)


def playMIDI(fpath, tempoBPM, bot_picking_map, guitar_bot_udp, strumq):
    # Create onset and offset masks
    timetrack, pitchtrack, veltrack = genWrapper(fpath, tempoBPM)
    
    pitchtrack = np.array(pitchtrack)
    veltrack = np.array(veltrack)
    timestamps, pitches, vels = rollupTracks(timetrack, pitchtrack, veltrack)
    # print (f'timestamps: {timestamps}')
    # print (f'pitches: {pitches}')
    # print (f'vels: {vels}')

    # Generate map of every note on the fretboard and corresponding string
    fretmap, stringmap = mapgen()
    fretboard_states, string_states = gen_poly_states(pitches, vels, fretmap, stringmap, bot_picking_map)

    durations = durfromTimestamp(timestamps)
    
    # Polyphony
    playPolyphony(durations, fretboard_states, string_states, veltrack, pitches, guitar_bot_udp, strumq)