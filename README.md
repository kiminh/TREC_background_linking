
# IR-BERT @ TREC 2020 News Track (Background Linking)

This repo has the implementation of two methods
* Weighted Search Query + BM25 [code here](./src/IR-BERT/wBT+BM25.py)
* IR-BERT [code here](./src/IR-BERT/IR-BERT.py)

## Data Process and Observation [code here](./src/IR-BERT/Preprocess.py)

* lower case
* stemmer
* remove stop words

## Best method (IR-BERT)

* We propose IR-BERT, which combines the retrieval
power of BM25 with the contextual understanding gained through a BERT based model.

![Image of Yaktocat](https://github.com/Anup-Deshmukh/TREC_background_linking/blob/master/res1.png)


