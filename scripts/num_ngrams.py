import itertools
import glob

from sample_size_test import generate_ngrams
#from sample_size_test import
from talkbank_parser import MorParser

if __name__ == "__main__":
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    filenames = glob.glob("/home/paul/corpora/Brown/Eve/*.xml")
    corpus = list(itertools.chain(*(parser.parse(i) for i in filenames)))
    utterances = [[u.word for u in utterance]
                  for speaker, utterance in corpus
                  if len(utterance) >= 3 and speaker == 'MOT']

    print sum([len(generate_ngrams(3, g)) for g in utterances])
