from preprocess import Corpus, CorpusNotes
import glob, os
# from models import Autoencoder

if __name__ == '__main__':
    
    datasetPath = '../datasets/Wikifonia/'
    ds_size = 6391

    init = 0
    batch_size = 100
    end = init + min(batch_size, ds_size-init)
    
    while init < ds_size:
        end = init + batch_size
        corpusNotes = CorpusNotes(datasetPath, batch_size, init, end)
        # corpusNotes.get_measure_notes_chords(0)
        print (f'fNum {init}') 
        # corpusNotes.save_corpus_notes_chords()
        init = end