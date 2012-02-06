#! /usr/bin/env python2


from glob import glob
from dump_speaker_data import extract_feature_utterances
from sample_size_test import generate_ngrams


files = glob("/home/paul/corpora/Brown/Eve/*.xml")
utterances = extract_feature_utterances(files, "pos", "MOT")
bigrams = [generate_ngrams(2, ut) for ut in utterances if len(ut) > 1]
bigrams = reduce(list.__add__, bigrams, [])
poses = set([word for ut in utterances for word in ut])

print "# Utterances:", len(utterances)
print "# Bigrams:", len(bigrams)
print "# Bigrams Types", len(set(bigrams))
print "# of parts of speech tags:", len(poses)

"""
WORDS
# Utterances: 10445
# Bigrams: 36079
# Bigrams Types 10162

POS
# Utterances: 10445
# Bigrams: 36079
# Bigrams Types 294

"""
