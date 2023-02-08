import numpy as np
# Tuning of the robot
tuning = np.array([40, 45, 50, 55, 59, 64])
# minStrings = 6

note_midi_dict = {
        "E": [40, 52, 64],
        "F": [41, 53, 65],
        "F#": [42, 54, 66],
        "Gb": [42, 54, 66],
        "G": [43, 55, 67],
        "G#": [44, 56, 68],
        "Ab": [44, 56, 68],
        "A": [45, 57, 69],
        "A#": [46, 58, 70],
        "Bb": [46, 58, 70],
        "B": [47, 59, 71],
        "C": [48, 60, 72],
        "C#": [49, 61, 73],
        "Db": [49, 61, 73],
        "D": [50, 62, 74],
        "D#": [51, 63],
        "Eb": [51, 63]
    }

root_midi_dict = {
        "E": note_midi_dict["E"][0],
        "F": note_midi_dict["F"][0],
        "F#": note_midi_dict["F#"][0],
        "Gb": note_midi_dict["Gb"][0],
        "G": note_midi_dict["G"][0],
        "G#": note_midi_dict["G#"][0],
        "Ab": note_midi_dict["Ab"][0],
        "A": note_midi_dict["A"][0],
        "A#": note_midi_dict["A#"][0],
        "Bb": note_midi_dict["Bb"][0],
        "B": note_midi_dict["B"][0],
        "C": note_midi_dict["C"][0],
        "C#": note_midi_dict["C#"][0],
        "Db": note_midi_dict["Db"][0],
        "D": note_midi_dict["D"][0],
        "D#": note_midi_dict["D#"][0],
        "Eb": note_midi_dict["Eb"][0]    
}

chord_interval_dict = {
        "Major": [4, 7],
        "Minor": [3, 7],
        "Dom7": [4, 7, 10],
        "Major7": [4, 7, 11],
        "Minor7": [3, 7, 10]
}