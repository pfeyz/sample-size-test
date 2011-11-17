import glob
import itertools
import pickle
from talkbank_parser import MorParser

parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
filenames = glob.glob("/home/paul/corpora/Brown/Eve/*.xml")
corpus = itertools.chain(*(parser.parse(i) for i in filenames))
corpus = filter(lambda x: x[0] == 'MOT', corpus)
with open("data.pk", 'w') as fh:
    pickle.dump(corpus, fh)
