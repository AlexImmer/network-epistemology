import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from tqdm import tqdm
from multiprocessing import Pool

from loading import load_corpus, load_doc_topics, load_concept_distances

k = 100  # n topics


def obtain_min_dist_split(X_topic, years, max_mem=10**7, l0=False, subset=False):
    # only accept either or none
    assert not (subset and l0)
    dist_metric = compute_dists_l0 if l0 \
        else (compute_dists_subset if subset else compute_dists_l1)
    norm = 'l0' if l0 else ('Sub' if subset else '')
    for year in tqdm(sorted(list(years))[1:]):
        try:
            load_concept_distances(year, l0, subset)
            continue
        except:
            pass
        cols = np.arange(0, k)
        X_prev = X_topic.loc[(X_topic['year'] < year), cols]
        global X_cur
        X_cur = X_topic.loc[(X_topic['year'] == year), cols]
        ix_stepsize = int(max_mem / len(X_cur))
        min_dist = pd.DataFrame(index=X_prev.index, columns=['min_dist', 'closest_doc'])
        X_prev = X_prev.values
        X_prevs = [X_prev[i: i+ix_stepsize] for i in range(0, len(X_prev), ix_stepsize)]
        with Pool(processes=32) as pool:
            res_list = pool.map(dist_metric, X_prevs)
        dists = []
        closest = []
        for res in res_list:
            dists.extend(res[0])
            closest.extend(res[1])
        min_dist['min_dist'] = dists
        min_dist['closest_doc'] = closest
        min_dist.to_pickle('data/{year}_distances{norm}.pd'.format(year=year, norm=norm))


def compute_dists_l1(X_prev):
    # l1 distance between topic distributions
    dists = cdist(X_prev, X_cur.values, metric='cityblock')
    min_dists = dists.min(axis=1)
    closest_ixs = X_cur.index[dists.argmin(axis=1)]
    return min_dists, closest_ixs


def compute_dists_l0(X_prev):
    # l0 distance for values >= 1/k so its limited by k
    dists = cdist(X_prev >= 1/k, X_cur.values >= 1/k, metric='hamming')
    min_dists = (dists.min(axis=1) * k).astype(np.int16)
    closest_ixs = X_cur.index[dists.argmin(axis=1)]
    return min_dists, closest_ixs


def compute_dists_subset(X_prev):
    # number of elements not covered (0 if X_cur contains a superset of
    # topics for an element in X_prev). 1 if one topic is not covered etc.
    dists = (cdist(X_prev >= 1/k, X_cur.values >= 1/k, metric='russellrao') * k) - k \
            + np.sum(X_prev >= 1/k, axis=1)[:, np.newaxis]
    min_dists = (dists.min(axis=1)).astype(np.int16)
    closest_ixs = X_cur.index[dists.argmin(axis=1)]
    return min_dists, closest_ixs


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
    print('Compute Subset')
    obtain_min_dist_split(X_multopic, years, max_mem=10**7, subset=True)
    print('Compute L0')
    obtain_min_dist_split(X_multopic, years, max_mem=10**7, l0=True)
    print('Compute L1')
    obtain_min_dist_split(X_multopic, years, max_mem=10**7)
    print('finished.')
