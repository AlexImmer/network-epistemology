import json
import numpy as np
import pandas as pd

data_dir = 'data/'
corpus_files = ['publication_data/dblp-ref-0.json',
                'publication_data/dblp-ref-1.json',
                'publication_data/dblp-ref-2.json',
                'publication_data/dblp-ref-3.json']
unconnected = 'weird_publications.txt'


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
    file = file or data_dir + 'X_multopic.npy'
    return np.load(file)


def load_concept_distances(year, keep_closeest_doc=False):
    file = data_dir + '{year}_distances.pd'.format(year=year)
    df = pd.read_pickle(file)
    if not keep_closeest_doc:
        del df['closest_doc']
        df.columns = ['concept_distance']
    df.index.name = 'pub_id'
    return df


def load_transformation_distances(year):
    file = data_dir + 'transformation{year}.csv'.format(year=year)
    df = pd.read_csv(file, index_col=0)
    df.columns = ['transformation_distance']
    return df


def load_tradition_distances(year):
    file = data_dir + 'tradition{year}.csv'.format(year=year)
    df = pd.read_csv(file, index_col=0)
    df.columns = ['tradition_distance']
    return df


def load_distances(year):
    # TODO: remove broken papers
    conc = load_concept_distances(year)
    trans = load_transformation_distances(year)
    trad = load_tradition_distances(year)
    # conc contains all the right indices
    res = conc.merge(trans, how='left', left_index=True, right_index=True)
    res = res.merge(trad, how='left', left_index=True, right_index=True)
    return res


def load_disconnected_publications():
    pub_ids = pd.read_csv(data_dir + unconnected, index_col=0, names=[])
    return pub_ids
