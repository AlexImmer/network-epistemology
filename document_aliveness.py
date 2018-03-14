import numpy as np
import pandas as pd
import pickle
from multiprocessing import Pool
from scipy.spatial.distance import cdist
from tqdm import tqdm

from loading import load_corpus, load_doc_topics


def compute_cdist(X_prev, X_cur):
    return cdist(X_prev.values, X_cur.values, metric='cityblock').min(axis=1)


def obtain_min_distances_parallel(X_topic, years, max_mem=36000000):
    res = {}
    for year in tqdm(sorted(list(years))[1:]):
        cols = np.arange(0, 100)
        X_prev = X_topic[X_topic['year'] < year][cols]
        X_cur = X_topic[X_topic['year'] == year][cols]
        ix_stepsize = int(max_mem / len(X_cur))

        with Pool(processes=4) as pool:
            iterable = [(X_prev.iloc[i: i+ix_stepsize].copy(), X_cur.copy())
                        for i in range(0, len(X_prev), ix_stepsize)]
            X_prevsubs = pool.imap(compute_cdist, iterable)

        min_dist = pd.DataFrame(index=X_prev.index)
        for i, res in zip(range(0, len(X_prev), ix_stepsize), X_prevsubs):
            min_dist.iloc[i: i+ix_stepsize] = res

        res[year] = min_dist
    return res


def obtain_min_distances(X_topic, years):
    res = {}
    for year in tqdm(sorted(list(years))[1:]):
        cols = np.arange(0, 100)
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
    _, _, dates_corpus = load_corpus()
    print('load doc topics')
    X_multopic = load_doc_topics()
    X_multopic = pd.DataFrame(X_multopic)
    X_multopic['year'] = dates_corpus
    print('compute distances')
    min_dists = obtain_min_distances_parallel(X_multopic, set(dates_corpus), max_mem=10**9)
    print('dump results')
    pickle.dump(min_dists, 'data/min_dists.pkl')
    print('finished.')
