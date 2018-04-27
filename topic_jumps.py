import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from tqdm import tqdm
from multiprocessing import Pool

from loading import load_corpus, load_doc_topics, load_jump_edges, load_distances, data_dir

k = 100  # n topics


def compute_jump_edges(X_topic, years, max_mem=10**7, tradition=True):
    col = ('tradition' if tradition else 'transformation') + '_distance'
    for year in tqdm(sorted(list(years))[1:]):
        try:
            load_jump_edges(year, tradition)
            continue
        except:
            pass
        cols = np.arange(0, k)
        dists = load_distances(year)
        disconnected = dists[dists[col].isnull()].index
        # 2 stage filtering for speed in early years
        X_prev = X_topic.loc[(X_topic['year'] < year), cols]
        X_prev = X_prev.loc[disconnected, cols]
        global X_cur
        X_cur = X_topic.loc[(X_topic['year'] <= year), cols]
        ix_stepsize = int(max_mem / len(X_cur))
        X_prevs = [X_prev.iloc[i: i+ix_stepsize] for i in range(0, len(X_prev), ix_stepsize)]
        with Pool(processes=4) as pool:
            res_list = pool.map(find_edges, X_prevs)
        starts = []
        ends = []
        for res in res_list:
            starts.extend(res[0])
            ends.extend(res[1])
        edges = pd.DataFrame()
        edges['start'] = starts
        edges['end'] = ends
        case = 'tradition' if tradition else 'transformation'
        file = data_dir + '{year}_jump_edges_{case}.csv'.format(year=year, case=case)
        edges.to_csv(file, index=False)


def find_edges(X_prev):
    # number of elements not covered (0 if X_cur contains a superset of
    # topics for an element in X_prev). 1 if one topic is not covered etc.
    dists = (cdist(X_prev >= 1 / k, X_cur.values >= 1 / k, metric='russellrao') * k) - k \
            + np.sum(X_prev >= 1 / k, axis=1)[:, np.newaxis]
    starts, ends = np.where(dists == 0)
    return list(X_prev.index[starts]), list(X_cur.index[ends])


def obtain_min_distances(X_topic, years):
    res = {}
    for year in tqdm(sorted(list(years))[1:]):
        cols = np.arange(0, k)
        X_prev = X_topic[X_topic['year'] < year][cols]
        X_cur = X_topic[X_topic['year'] == year][cols]
        min_dist = cdist(X_prev.values, X_cur.values, metric='cityblock').min(axis=1)
        min_dist = pd.DataFrame(min_dist, index=X_prev.index)
        res[year] = min_dist
    return res


if __name__ == '__main__':
    # compute distance list following the scheme
    # list[year] : DataFrame.loc[pubs before year] : dist to closest pub of year in [0, 1]
    print('load corpus')
    ids_corpus, _, dates_corpus = load_corpus()
    print('load doc topics')
    X_multopic = load_doc_topics()
    X_multopic = pd.DataFrame(X_multopic, index=ids_corpus)
    X_multopic['year'] = dates_corpus
    print('compute distances')
    years = set(dates_corpus)
    del dates_corpus
    del ids_corpus
    print('Tradition')
    compute_jump_edges(X_multopic, years, max_mem=10**7, tradition=True)
    print('Transformation')
    compute_jump_edges(X_multopic, years, max_mem=10**7, tradition=False)
    print('finished.')
