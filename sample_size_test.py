import argparse
import itertools
import random
from sys import argv

from talkbank_parser import MorParser

class NGramException(Exception):
    pass

def generate_ngrams(n, words):
    """ Generates ngram strings from list of words

    >>> generate_ngrams(2, 'the boy beat the ram'.split(' '))
    ['the boy', 'boy beat', 'beat the', 'the ram']

    >>> generate_ngrams(1, 'we are family'.split(' '))
    ['we', 'are', 'family']

    >>> generate_ngrams(3, 'this aggression will not stand man'.split(' '))
    ['this aggression will', 'aggression will not', 'will not stand', 'not stand man']

    >>> generate_ngrams(4, 'this cat ate'.split(' '))
    Traceback (most recent call last):
        ...
    NGramException: Not enough words to generate an ngram

    """

    if n > len(words):
        raise NGramException('Not enough words to generate an ngram')
    if n < 1:
        raise NGramException('Cannot compute ngram with n < 1: %s' % n)
    return [" ".join(words[i:i+n])
            for i in range(len(words) - n + 1)]

def pick_random_ngrams(n, samples, utterances):
    r""" Picks SAMPLES number of ngrams from utterances.
    Utterances should be a list of list of words.

    >>> utterances = [u.split(' ') for u in ["the man taught the dog",
    ... "we are family", "don't let anybody out",
    ... "harry caught himself being an idiot again",
    ... "stephen read the newspaper with his feet up on an ottoman",
    ... "jon's lazy susan is full of crazy things"]]

    >>> random.seed(5)
    >>> len(pick_random_ngrams(2, 10, utterances))
    10

    """

    ngrams = [generate_ngrams(n, ut) for ut in utterances]
    all_grams = list(itertools.chain(*ngrams))
    return [random.choice(all_grams) for i in range(samples)]

def pick_random_utterances(n, samples, utterances):
    """
    Picks SAMPLES number of random utterances and generates bigrams from all
    selected.

    >>> utterances = [u.split(' ') for u in ["the man taught the dog",
    ... "we are family", "don't let anybody out",
    ... "harry caught himself being an idiot again",
    ... "stephen read the newspaper with his feet up on an ottoman",
    ... "jon's lazy susan is full of crazy things"]]

    >>> sample_size = 50
    >>> ngram_size = 2
    >>> longest_utterance = max(len(u) for u in utterances)
    >>> grams = pick_random_utterances(ngram_size, sample_size, utterances)
    >>> len(grams) >= sample_size < sample_size + (longest_utterance - ngram_size)
    True

    """
    population = [u for u in utterances if len(u) >= n]
    # if len(population) < samples:
    #     raise Warning("There are more pidgeons than holes")
    num_ngrams = 0
    ngrams = []
    while num_ngrams < samples:
        picked_utterance = random.choice(population)
        grams = generate_ngrams(n, picked_utterance)
        num_ngrams += len(grams)
        ngrams.extend(grams)
    return ngrams

def dice_stat(a, b):
    # calculate the dice coefficient
    shared = len(a & b)
    coeff = (2.0 * shared)/(len(a) + len(b))
    return round(coeff, 5)

# Jaccard
def jaccard_stat(a, b):
    # calculate the jaccard coefficient
    shared = len(a & b)
    coeff = shared / (len(a) + len(b) - shared)
    return round(coeff, 5)

#McNemar
def mcnemar_stat(a,b,c,d):
    # calculate the mcnemar
    # square = all tokens produced in (a or b) and (c or d)
    pass

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--ngram-size', action='store', type=int,
        help="The size of the ngrams to use", required=True)
    parser.add_argument('-sample-size', '-s', action='store', type=int,
        help="The number of samples to use. What this means depends on the "
        "atomic_unit parameter.", required=True)
    parser.add_argument('-a', '--atomic-unit', action='store', required=True,
        choices=("utterance", "ngram"),
        help=("'utterance' will select SAMPLE_SIZE number of utterances and then "
              "make ngrams out of all of them. 'ngram' will generate SAMPLE_SIZE "
              "ngrams."))
    parser.add_argument('filename', action='store',
        help='The CHILDES XML file to read')
    return parser.parse_args(args)

if __name__ == "__main__":
    args = parse_args(argv[1:])
    print args
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    utterances = [[u.word for u in utterance]
                  for speaker, utterance in parser.parse(args.filename)
                  if len(utterance) >= args.ngram_size]
    fun = pick_random_utterances if args.atomic_unit == 'utterance' \
          else pick_random_ngrams
    print fun(args.ngram_size, args.sample_size, utterances)
