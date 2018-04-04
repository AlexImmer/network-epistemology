import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from tqdm import tqdm
from multiprocessing import Pool

from loading import load_corpus, load_doc_topics, load_delta


def obtain_min_dist_split(X_topic, years, max_mem=10**7):
    for year in tqdm(sorted(list(years))[1:]):
        try:
            load_delta(year)
            print('already computed', year)
            continue
        except:
            print('to compute', year)
            pass
        cols = np.arange(0, 100)
        X_prev = X_topic.loc[(X_topic['year'] < year), cols]
        global X_cur
        X_cur = X_topic.loc[(X_topic['year'] == year), cols].values
        ix_stepsize = int(max_mem / len(X_cur))
        min_dist = pd.DataFrame(index=X_prev.index, columns=['min_dist', 'closest_doc'])
        X_prev = X_prev.values
        X_prevs = [X_prev[i: i+ix_stepsize] for i in range(0, len(X_prev), ix_stepsize)]
        with Pool(processes=32) as pool:
            res_list = pool.map(compute_dists, X_prevs)
        dists = []
        closest = []
        for res in res_list:
            dists.extend(res[0])
            closest.extend(res[1])
        min_dist['min_dist'] = dists
        min_dist['closest_doc'] = closest
        min_dist.to_pickle('data/{year}_distances.pd'.format(year=year))
        print('dumped', year)


def compute_dists(X_prev):
    dists = cdist(X_prev, X_cur.values, metric='cityblock')
    min_dists = dists.min(axis=1)
    closest_ixs = X_cur.index[dists.argmin(axis=1)]
    return min_dists, closest_ixs


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
    ids_corpus, _, dates_corpus = load_corpus()
    print('load doc topics')
    X_multopic = load_doc_topics()
    X_multopic = pd.DataFrame(X_multopic, index=ids_corpus)
    X_multopic['year'] = dates_corpus
    print('compute distances')
    years = set(dates_corpus)
    del dates_corpus
    del ids_corpus
    obtain_min_dist_split(X_multopic, years, max_mem=10**7)
    print('finished.')
