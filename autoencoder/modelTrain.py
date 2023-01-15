import music21
import os, glob, pickle
import numpy as np
from tqdm import tqdm
from itertools import chain

dirPath = 'midi_dataset'

class LoadDataset:
    def __init__(self, dirPath):
        self.dirPath = dirPath
        self.fpaths = glob.glob(os.path.join(self.dirPath, '*.pkl'))
        self.corpus_notes = []
        self.corpus_chords = []
        self.load_dataset()
        self.unpack_corpus_notes()
    
    def load_dataset(self):
        for fpath in self.fpaths:
            with open(fpath, 'rb') as f:
                self.corpus_notes += pickle.load(f)
                self.corpus_chords += pickle.load(f)
    
    # Write a function to get note durations from corpus_notes. Each item in corpus_notes is a list of notes in a measure. Each note is a tuple (midi, offset, duration)
    def unpack_corpus_notes(self):
        self.note_durations = []
        self.note_midis = []
        self.note_offsets = []

        for measure in self.corpus_notes:
            durations_measure = [note[2] for note in measure]
            self.note_durations.append(durations_measure)

            midis_measure = [note[0] for note in measure]
            self.note_midis.append(midis_measure)

            offsets_measure = [note[1] for note in measure]
            self.note_offsets.append(offsets_measure)

    def convert_to_float(self, lst):
        return [float(item) for item in lst]

    def get_unique_values(self):
        self.unique_note_durations = sorted(set(chain.from_iterable(self.note_durations)))
        self.unique_note_offsets = sorted(set(chain.from_iterable(self.note_offsets)))


if __name__ == '__main__':
    dataset = LoadDataset(dirPath)
    # print (f'len corpus notes: {len(dataset.corpus_notes)}; len corpus notes[0]: {len(dataset.corpus_notes[0])}; corpus_notes[0]: {dataset.corpus_notes[0]} ; len corpus notes[0][0]: {len(dataset.corpus_notes[0][0])}')
    # print (f'len corpus chords: {len(dataset.corpus_chords)}; len corpus chords[0]: {len(dataset.corpus_chords[0])}; corpus_chords[0]: {dataset.corpus_chords[0]} ; len corpus chords[0][0]: {len(dataset.corpus_chords[0][0])}')
    dataset.unpack_corpus_notes()
    durs = dataset.note_durations
    offs = dataset.note_offsets
    # unique_offs = dataset.get_unique_values(offs)
    dataset.get_unique_values()
    print (f'len unique_offs: {len(dataset.unique_note_offsets)}, unique_offs: {dataset.unique_note_offsets}')
    
    # print ((f'offs[0]: {offs[0:10]}'))
    # print (dataset.corpus[0])