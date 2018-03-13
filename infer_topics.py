import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from loading import load_corpus


def fit_topic_model(documents):
    # uniform priors on both document and topic distributions
    # batch learning and
    lda = LatentDirichletAllocation(n_components=100, doc_topic_prior=None, topic_word_prior=None,
                                    learning_method='batch', max_iter=30, evaluate_every=3,
                                    n_jobs=-1, verbose=2)
    X_multopic = lda.fit_transform(documents)
    return X_multopic


def model_topics():
    try:
        X_multopic = np.load('X_multopic.npy')
    except:
        lda = LatentDirichletAllocation(n_components=100, doc_topic_prior=None, topic_word_prior=None,
                                        learning_method='batch',
                                        max_iter=10, n_jobs=2, verbose=1)
        X_multopic = lda.fit_transform(X)
        np.save('X_multopic.npy', X_multopic)
    return X_multopic


if __name__ == '__main__':
    # extract topic distributions and persist them
    print('load data')
    ids_corpus, text_corpus, dates_corpus = load_corpus()

    print('tokenize and vectorize')
    # if there are other-language documents in the corpus, we should use no stop-word filter below
    # min df so they form a propagating graph
    # check binary=True should lead to different interpretation --> if only considered N, its
    # important to consider diversity more than specificity in vocabulary of a single document
    vectorizer = CountVectorizer(analyzer='word', stop_words='english', lowercase=True, max_df=0.3, min_df=25,
                                 binary=True)
    X = vectorizer.fit_transform(text_corpus)

    print('LDA')
    X_multopic = fit_topic_model(X)

    print('save topic distributions')
    np.save('data/X_multopic.npy', X_multopic)

    print('finished.')
