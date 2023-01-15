import music21
import os, glob, pickle
import numpy as np
from tqdm import tqdm

class Corpus:
    def __init__(self, path, batch_size, initFileNum, endFileNum):
        self.path = path
        self.initFileNum = initFileNum
        self.endFileNum = endFileNum
        # self.numFiles = numFiles
        self.batch_size = batch_size
        self.filenames = glob.glob(os.path.join(self.path, '*.mxl')) [self.initFileNum:self.endFileNum]
        self.corpus = []
        self.read_corpus()

    # def __len__(self):
    #     return int(len(self.filenames) // self.batch_size)

    # def __getitem__(self,idx):
    #     X = np.empty(self.batch_size)
    #     batch = self.filenames[idx * self.batch_size : (idx+1) * self.batch_size]
    #     for i, ID in enumerate(batch):
    #         print (i)
    #         self.corpus.append(music21.converter.parse(ID))
    #     return X
    
    def read_corpus(self):
        for file in tqdm(self.filenames):
            try:
                self.corpus.append(music21.converter.parse(file))
            except:
                print(f'Error parsing {file}')
                continue
    
    def save_corpus(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.corpus, f)

    def load_corpus(self, filename):
        with open(filename, 'rb') as f:
            self.corpus = pickle.load(f)

    def get_corpus(self):
        return self.corpus

    def get_corpus_size(self):
        return len(self.corpus)

    def get_corpus_info(self):
        for i, piece in enumerate(self.corpus):
            print("Piece {} has {} parts".format(i, len(piece.parts)))

    def get_corpus_part(self, piece, part):
        return self.corpus[piece].parts[part]

    def get_corpus_part_info(self, piece, part):
        print(self.corpus[piece].parts[part].measures(0, 1))

    def get_corpus_part_notes(self, piece, part):
        return self.corpus[piece].parts[part].flat.notes

    def get_corpus_part_notes_info(self, piece, part):
        for i, note in enumerate(self.corpus[piece].parts[part].flat.notes):
            print("Note {} is {}".format(i, note))

    def get_corpus_part_notes_duration(self, piece, part):
        for i, note in enumerate(self.corpus[piece].parts[part].flat.notes):
            print("Note {} has duration {}".format(i, note.duration.quarterLength))

    def get_corpus_part_notes_pitch(self, piece, part):
        for i, note in enumerate(self.corpus[piece].parts[part].flat.notes):
            print("Note {} has pitch {}".format(i, note.pitch))

    def get_corpus_part_notes_pitch_name(self, piece, part):
        for i, note in enumerate(self.corpus[piece].parts[part].flat.notes):
            print("Note {} has pitch name {}".format(i, note.pitch.name))

    def get_corpus_part_notes_pitch_name_octave(self, piece, part):
        for i, note in enumerate(self.corpus[piece].parts[part].flat.notes):
            print("Note {} has pitch name {} and octave {}".format(i, note.pitch.name, note))


class CorpusNotes(Corpus):
    def __init__(self, path, batch_size, initFileNum, endFileNum):
        super().__init__(path, batch_size, initFileNum, endFileNum)
        self.notes = []
        self.saveFname = f'midi_dataset/notes_chords_fnum_{self.initFileNum}-{self.endFileNum}.pkl'
        self.extract_notes()
        self.get_measure_notes_chords(0)
        # self.save_corpus_notes_chords()
     
    def extract_notes(self):
        for piece in self.corpus:
            for part in piece.parts:
                for note in part.flat.notes:
                    self.notes.append(note)

    def get_notes_info(self):
        for i, note in enumerate(self.notes):
            print("Note {} is {}".format(i, note))

    def get_notes_duration(self):
        for i, note in enumerate(self.notes):
            print("Note {} has duration {}".format(i, note.duration.quarterLength))

    def get_notes_pitch_name_octave(self):
        for i, note in enumerate(self.notes):
            print("Note {} has pitch name {} and octave {}".format(i, note.pitch.name, note))
    
    def get_timestamps_piece_part_tempo(self, piece, part, tempo):
        timestamps = []
        for i, note in enumerate(self.corpus[piece].parts[part].flat.notes):
            timestamps.append(note.offset * tempo/100)
        return timestamps

    def get_measures(self, piece, part):
        measures = []
        # print (self.corpus[piece].parts[part])
        for i, measure in enumerate(self.corpus[piece].parts[part].measures(0, None)):
            # print (i)
            measures.append(measure)
        return measures

    def get_measures_notes(self, piece, part):
        measures_notes = []
        for i, measure in enumerate(self.corpus[piece].parts[part].measures(0, None)):
            measures_notes.append(measure.notes)
        return measures_notes
    
    # Still to test
    def get_tempo(self, piece, part):
        for i, measure in enumerate(self.corpus[piece].parts[part].measures(0, None)):
            if measure.tempo:
                tempo = measure.tempo
            else:
                continue   
    
    def get_measure_notes_chords(self, part):
        corpus_notes = []
        corpus_chords = []
        corpus_notes_symbols = []
        corpus_chords_symbols = []
        for piece in tqdm(np.arange(self.batch_size)):
            try:
                measures = self.get_measures(piece, part)
            except:
                print(f'Error parsing {piece}, part: {part}')
                continue
            for measure in measures:
                measure_notes_symbols = []
                measure_chords_symbols = []
                measure_notes = []
                measure_chords = []
                if isinstance(measure, music21.stream.Measure):
                    for data in measure:
                        if isinstance(data, music21.note.Note):
                            measure_notes_symbols.append((data.name, data.pitch.octave, data.offset, data.duration.quarterLength))
                            measure_notes.append((data.pitch.midi, data.offset, data.duration.quarterLength))
                        if isinstance(data, music21.harmony.ChordSymbol):
                            measure_chords_symbols.append(([p.name for p in data.pitches], [p.octave for p in data.pitches], data.offset, data.duration.quarterLength))
                            measure_chords.append(([p.midi for p in data.pitches], data.offset, data.duration.quarterLength))
                if len(measure_notes) > 0 and len(measure_chords) > 0:
                    corpus_notes.append(measure_notes)
                    corpus_chords.append(measure_chords)
                    corpus_notes_symbols.append(measure_notes_symbols)
                    corpus_chords_symbols.append(measure_chords_symbols)
        self.corpus_notes = corpus_notes
        self.corpus_chords = corpus_chords
        self.corpus_notes_symbols = corpus_notes_symbols
        self.corpus_chords_symbols = corpus_chords_symbols
    
    # Write a function to save corpus_notes and corpus_chords to a file
    def save_corpus_notes_chords(self):
        with open(self.saveFname, 'wb') as f:
            pickle.dump(self.corpus_notes, f)
            pickle.dump(self.corpus_chords, f)
            # pickle.dump(self.corpus_notes_symbols, f)
            # pickle.dump(self.corpus_chords_symbols, f)
    
    # Write a function to load corpus_notes and corpus_chords from a file
    def load_corpus_notes_chords(self, filename):
        with open(filename, 'rb') as f:
            self.corpus_notes = pickle.load(f)
            self.corpus_chords = pickle.load(f)
            # self.corpus_notes_symbols = pickle.load(f)
            # self.corpus_chords_symbols = pickle.load(f)
    
    
    def print_content_by_measure(self):
        """
        input list containing notes/ chords per measure as individual item
        """
        print (f'measure notes - len: {len(self.corpus_notes)}, len[0]: {len(self.corpus_notes[0])}')
        print (f'measure chords - len: {len(self.corpus_chords)}, len[0]: {len(self.corpus_chords[0])}')


# Write a class to load .pkl files from a directory and combine them into one dataset
# Class should include methods from corpusNotes class to extract notes and chords from the dataset

