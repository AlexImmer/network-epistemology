import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from tqdm import tqdm
from multiprocessing import Pool

from loading import load_corpus, load_doc_topics, load_graph_distances, data_dir, load_jump_transformation_distances, \
    load_jump_tradition_distances

k = 100  # n topics


def obtain_jump_edge_distances(X_topic, years, max_mem=10**7, tradition=True):
    col = ('tradition' if tradition else 'transformation') + '_distance'
    for year in tqdm(sorted(list(years))[1:]):
        try:
            if tradition:
                load_jump_tradition_distances(year)
            else:
                load_jump_transformation_distances(year)
            continue
        except:
            pass
        cols = np.arange(0, k)
        dists = load_graph_distances(year)
        # extend dists by current year pubs (dist = 0)
        current = X_topic.loc[(X_topic['year'] == year)].index
        current = pd.DataFrame(0, columns=[col], index=current)
        dists = dists.append(current)
        disconnected = dists[dists[col].isna()].index
        connected = dists[dists[col].notna()].index
        X_prev = X_topic.loc[(X_topic['year'] < year), cols]
        X_prev = X_prev.loc[disconnected]
        global X_cur
        X_cur = X_topic.loc[(X_topic['year'] <= year), cols]
        X_cur = X_cur.loc[connected]
        ix_stepsize = int(max_mem / len(X_cur))
        X_prevs = [X_prev.iloc[i: i+ix_stepsize] for i in range(0, len(X_prev), ix_stepsize)]
        with Pool(processes=18) as pool:
            res_list = pool.map(find_edges, X_prevs)
        map = {}
        for res in res_list:
            for s, e in zip(res[0], res[1]):
                if map.get(s):
                    map[s].append(e)
                else:
                    map[s] = [e]
        res = pd.DataFrame(index=list(map.keys()))
        res['topic_' + col] = res.index.map(lambda x: dists.loc[map[x], col].min())
        case = 'tradition' if tradition else 'transformation'
        file = data_dir + 'jump_{case}{year}.csv'.format(year=year, case=case)
        res.to_csv(file, index_label='pub_id')


def find_edges(X_prev):
    # number of elements not covered (0 if X_cur contains a superset of
    # topics for an element in X_prev). 1 if one topic is not covered etc.
    dists = (cdist(X_prev >= 1 / k, X_cur.values >= 1 / k, metric='russellrao') * k) - k \
            + np.sum(X_prev >= 1 / k, axis=1)[:, np.newaxis]
    starts, ends = np.where(dists == 0)
    return list(X_prev.index[starts]), list(X_cur.index[ends])


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
    obtain_jump_edge_distances(X_multopic, years, max_mem=10**7, tradition=True)
    print('Transformation')
    obtain_jump_edge_distances(X_multopic, years, max_mem=10**7, tradition=False)
    print('finished.')
