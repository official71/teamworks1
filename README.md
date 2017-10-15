# ISE

### packages required

* [Stanford CoreNLP software suite](https://stanfordnlp.github.io/CoreNLP/) and its [Python wrapper](https://github.com/infobiac/PythonNLPCore)
* [__Apache TIKA__](https://github.com/chrismattmann/tika-python), extracting text from webpages
* __googleapiclient.discovery__, Google Search API
* __argparse__, argument parsing

### design
* Documents returned from Google search are wrapped in a class, where text contents are extracted and saved
* For every searched document, the NLP annotator is run twice: 
    * First time without the expensive "parse" and "relation" annotators, simply screening the sentences by their tokens, only save the sentences that contain tokens of that are relevant to the relation, e.g. for relation *Work_In* the sentence must have at least one token of type *PERSON* and one of type *ORGANIZATION*. Besides, the sentences that are too long (>50 tokens) are also discarded, because we found that long sentences seldom produce what we want, but significantly increase the cost of parsing;
    * Second time running with the "parse" and "relation" annotators, since the number of sentences are significantly reduced in the first step, the performance is acceptable. The relational tuples are also wrapped in a class for easy hashing and comparison between tuples.
* If any one of the tuples returned by a document is new in the output set, include it in the set; otherwise update the one in the set if the confidence has improved for the tuple, but it does not count as a new tuple.