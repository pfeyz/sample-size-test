from __future__ import print_function
import itertools
import pickle
import sys
from os.path import dirname, abspath, basename, splitext
from os.path import join as pjoin

from talkbank_parser import MorParser

here = dirname(abspath(__file__))

if __name__ == "__main__":

    try:
        speaker, feature, cutoff = sys.argv[1:4]
        filenames = sys.argv[4:]
    except ValueError:
        raise Exception("Three+ args required: speaker, feature (pos, word) "
                    "and xml files")

    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    corpus = itertools.chain(*(parser.parse(i) for i in filenames))
    utterances = [[w._asdict()[feature] for w in u[1]]
                  for u in corpus
                  if u[0] == speaker and len(u[1]) >= int(cutoff)]
    name = splitext(basename(filenames[0]))[0]
    outfn = pjoin(here, 'utterances', "%s-%s.pk" % (speaker, feature))
    print("pickling utterances")
    with open(outfn, 'w') as fh:
        pickle.dump(utterances, fh)
