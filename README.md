# Stability of Epistemic Networks

## From Theory to Empiricism

The theoretical underpinnings of the question _Can knowledge get lost in modern epistemic networks_ follow from evolutionary epistemology and give rise to the hyptohesis that knowledge is condensed and persisted throughout time. On the empirical side, we want to show that a realistic model supports this hypothesis. In this context, it is sensible to work with co-author networks that are sufficiently self-contained and depict the most important entities and links of an epistemic network. We first want to show how a simplistic model might favor a hypothesis of lost information before proposing a more realistic model that would lead to confirmation of our hypothesis.

For a first small-scale study we could use the [String Theory Scientific Community](http://web.mit.edu/demoscience/StringTheory/scinet.html). However, it poses the challenge of extracting the network from HTML or raw text exports. The publication data necessary can be found on the [web of science](https://webofknowledge.com
) by filtering on the topic _String Theory_.

Ultimately, conducting the analysis on the [DBLP dataset](https://aminer.org/citation) would allow more coverage but also poses more computational challenges. The upside is that the data is much better structured.

## Extracting the Graph

As described in the project proposal, we ask for a network consisting of _authors_, _concepts_, and _publications_. First order relationships are depicted bold and a possible second order relationship dashed below:

![network](https://user-images.githubusercontent.com/7715036/35624275-d48bb322-068e-11e8-8140-70b21a6b47af.png)

Except for the concepts, such a graph can be readily extracted from aforementioned data. 

### Extracting Concepts

When extracting concepts from the textual data, we consider the title concatenated with the abstract. Based on all the publications we can then build a topic model using _Latent Semantic Analysis_ or _Latent Dirichlet Allocation_. For fast implementations, we can make use of scikit learn or [gensim](https://radimrehurek.com/gensim/tut2.html). Ultimately, we would want not a soft-clustered topic vector that allows a probabilistic interpretation as in LDA. The LDA model also promotes sparsity due to its Dirichlet prior. Having a probability distribution of topics associated to each document, we could easily compute a publication by publication distance matrix. Most reasonable would be to use KL-Divergence but it is not symmetric so an easy way to go is with _l1_ following Pinsker's inequality.

### Extracting the Dynamics

We are provided with publication date and for now it should be sufficient to consider a grouping by publication years. This will give us a separate graph for each year with slightly varying authors and concept distributions and distinct publications.

## Tracking lost Knowledge

As previously pointed out, we want to show that a more realistic model is in favor of our hypothesis whereas a simplistic model might contradict it. The simplistic model considers only authors and their publications. The more realistic model works with concepts. In the following, we define cases leading to loss of information within the epistemic community over time. The definitions presume the graphical structure as defined earlier.

### A Simplistic Model

It is harder to argue than in the case where we have access to concepts. Consider for example a publication that is cited just once but the citing publication is highly influential. It might be that the original publication was important and the main idea is still imminent or that it is forgotten. Note that in the following, a publication equals its contained knowledge and this piece of knowledge is present if the publication is not forgotten.

Note that when we talk about paths, these are across the graphs at different times due to shared entities. However, when we look at alive nodes at time _t_, we only consider prior graphs.

#### Transformation

Transformation of ideas presented in literature is done by citing these and thus re-using concepts and possibly extending them. Transformation and thus citation keeps an idea alive. 

**Definition**: _We say a publication is k-alive at time t by transformation if the shortest path between the publication and any publication in the graph at time t has length at most k._

In fact based on the value of _k_ we observe different outcomes so it would be interesting to plot loss of information versus k for starters. Considered paths here are of type _(publication)-(publication)-...-(publication)_ where links denote references.

#### Tradition

As in the transformation model we consider publications as the knowledge containers. Nonetheless, their information content can be passed on by the corresponding authors. An idea is then kept alive if the author is active.

**Definition**: _We say a publication is k-alive at time t by tradition if the shortest path spanned by co-authorships between any of the publication's authors and an author in the graph at time t has length at most k._ 

Here, a plot of _k_ versus loss would be insightful. Considered paths are of type _(original author)-(author)-...-(author)_ where links denote co-authorship.

### Concepts Explain Loss

The simplistic model would denote a piece of knowledge lost if two publications overlap significantly but just one is being cited and passed on. However, that does not necessarily constitute loss of knowledge. It is more instructive to think about a publication belonging to a certain very small topic that is being treated. Humans are certainly able to cluster publications into such small topic groups for example when finding references for an essay. Topic models are an approach to automatically infer vector representations of documents that let us compute similarity and hence cluster topics. 

In addition to _tradition_ and _transformation_ we can now consider recurring concepts as information persistence. This is not a graph problem anymore but rather a similarity search. As described earlier, we have a topic vectors associated to documents and can measure their similarity by the _l1_ distance.

**Definition**: _We say a publication is alive at time t by recurrence if there is a publication at time t that is conceptually **similar**._ 

**Definition**: _Two publications are conceptually delta-similar if the l1 distance of their topics is less or equal to delta._

Note that the _l1_ distance is upper bounded for this case by 2 and thus _delta_ is on the interval [0, 2].
