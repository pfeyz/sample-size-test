# -*- py-shell-name: "python2" -*-

from __future__ import print_function
import itertools
import pickle
import sys
from os.path import dirname, abspath, basename, splitext
from os.path import join as pjoin

from talkbank_parser import MorParser

here = dirname(abspath(__file__))

def extract_feature_utterances(filenames, feature, speaker=None, cutoff=0):
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    corpus = itertools.chain(*(parser.parse(i) for i in filenames))
    utterances = [[w._asdict()[feature] for w in u[1]]
                  for u in corpus
                  if ((u[0] == speaker or speaker is None)
                      and len(u[1]) >= cutoff)]
    return utterances

if __name__ == "__main__":
    try:
        speaker, feature, cutoff = sys.argv[1:4]
        filenames = sys.argv[4:]
    except ValueError:
        raise Exception("Three+ args required: speaker, feature (pos, word) "
                    "and xml files")

    name = splitext(basename(filenames[0]))[0]
    utterances = extract_feature_utterances(filenames, feature, int(cutoff))
    outfn = pjoin(here, 'utterances', "%s-%s.pk" % (speaker, feature))
    print("pickling utterances")
    with open(outfn, 'w') as fh:
        pickle.dump(utterances, fh)
