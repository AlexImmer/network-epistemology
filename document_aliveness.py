import numpy as np
import pandas as pd
import pickle
from scipy.spatial.distance import cdist
from tqdm import tqdm

from loading import load_corpus, load_doc_topics


def obtain_min_distances_threshd(X_topic, years, max_mem=36000000):
    res = {}
    for year in sorted(list(years))[1:]:
        cols = np.arange(0, 100)
        X_prev = X_topic[X_topic['year'] < year][cols]
        X_cur = X_topic[X_topic['year'] == year][cols]
        ix_stepsize = int(max_mem / len(X_cur))
        min_dist = pd.DataFrame(index=X_prev.index)
        print(year)
        for i in tqdm(range(0, len(X_prev), ix_stepsize)):
            X_prevsub = X_prev.iloc[i: i+ix_stepsize].values
            min_dist.iloc[i: i+ix_stepsize] = cdist(X_prevsub, X_cur.values, metric='cityblock').min(axis=1)
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
    _, _, dates_corpus = load_corpus()
    X_multopic = load_doc_topics()
    X_multopic = pd.DataFrame(X_multopic)
    X_multopic['year'] = dates_corpus
    min_dists = obtain_min_distances(X_multopic, set(dates_corpus))
    pickle.dump(min_dists, 'data/min_dists.pkl')
