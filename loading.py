import json
import pickle
import numpy as np
import pandas as pd


corpus_files = ['publication_data/dblp-ref-0.json',
                'publication_data/dblp-ref-1.json',
                'publication_data/dblp-ref-2.json',
                'publication_data/dblp-ref-3.json']


def load_file(dblp_file):
    ids, texts, dates = [], [], []
    with open(dblp_file) as f:
        for line in f:
            line = json.loads(line)
            text = line.get('title', '') + '. ' + line.get('abstract', '')
            text = text.replace('- ', '')
            ids.append(line['id'])
            dates.append(line['year'])
            texts.append(text)
    return ids, texts, dates


def load_corpus(files=None):
    files = files or corpus_files
    ids_corpus, text_corpus, dates_corpus = [], [], []
    for file in files:
        ids, corpus, dates = load_file(file)
        ids_corpus.extend(ids)
        text_corpus.extend(corpus)
        dates_corpus.extend(dates)
    return ids_corpus, text_corpus, dates_corpus


def load_doc_topics(file=None):
    file = file or 'data/X_multopic.npy'
    return np.load(file)


def load_delta(year):
    file = 'data/{year}_distances.pd'.format(year=year)
    return pd.read_pickle(file)
