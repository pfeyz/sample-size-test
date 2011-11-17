#! /usr/bin/env python2

"""
TODO:

  - change sample_size to mean the number of ngrams per sample.

  - when atomic unit is set to utterance, generate ngrams from utterances until
    there are more than sample_size tokens ngrams generated.

"""
from __future__ import print_function
import argparse
import itertools
import random
import glob

from talkbank_parser import MorParser

class NGramException(Exception):
    pass

def meanstdv(x):
    """ from
    http://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html
    """

    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std

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
    a, b = set(a), set(b)
    shared = len(a & b)
    try:
        coeff = (2.0 * shared)/(len(a) + len(b))
    except ZeroDivisionError:
        return 0
    return round(coeff, 5)

# Jaccard
def jaccard_stat(a, b):
    # calculate the jaccard coefficient
    a, b = set(a), set(b)
    shared = len(a & b)
    try:
        coeff = shared / float(len(a) + len(b) - shared)
    except ZeroDivisionError:
        return 0
    return round(coeff, 5)

#McNemar
def mcnemar_stat(a,b,c,d):
    # calculate the mcnemar
    # square = all tokens produced in (a or b) and (c or d)
    pass

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--comparison-function', action='store',
                        choices=("dice", "jaccard", "mcnemar"), default="dice")
    parser.add_argument('-i', '--iterations', action='store', type=int,
        help="The number of times to run the tests", default=1)
    parser.add_argument('-n', '--ngram-size', action='store', type=int,
        help="The size of the ngrams to use", required=True)
    parser.add_argument('-f', '--feature', action='store',
        choices=('word', 'pos'), default='pos')
    parser.add_argument('-sample-size', '-s', action='store', type=tuple,
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

def do_comparison(fun, x_size, y_size, n, feature_name, corpus, target_speaker):
    if feature_name not in ("word", "pos"):
        raise Exception("feature_name must be 'word' or 'pos'")
    feat = (lambda x: x.pos) if feature_name == 'pos' else lambda x: x.word
    utterances = [[feat(u) for u in utterance]
                  for speaker, utterance in corpus
                  if len(utterance) >= n or speaker == target_speaker]
    picker = pick_random_utterances
    return fun(picker(n, x_size, utterances),
               picker(n, y_size, utterances))

    # make_grams = pick_random_utterances if args.atomic_unit == 'utterance' \
    #       else pick_random_ngrams

if __name__ == "__main__":
    base_sizes = (100, 200, 500, 1000, 5000)
    equal_pairs = [(i, i) for i in base_sizes]
    combo_pairs = [(a, b) for a, b in itertools.combinations(base_sizes, 2)
                   if a != b]
    tag_pairs = [(175, 412), (308, 433), (362, 498), (425,  540), (243, 548),
                 (428, 598), (556, 600), (659, 632)]
    word_pairs = [(1004, 3652), (2159, 3886), (2607, 4409), (3352, 6277),
                  (898, 6708), (3623, 8622), (5673, 9259), (8794, 10368)]
    word = lambda x: x.word
    tag = lambda x: x.tag
    sep = "-" * 20 + "\n"
    reps = 100
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    filenames = glob.glob("/home/paul/corpora/Brown/Eve/*.xml")
    corpus = list(itertools.chain(*(parser.parse(i) for i in filenames)))
    stat_fun = lambda x, y, feature: do_comparison(dice_stat, x, y, 3,
                                                   feature, corpus, 'MOT')

    for pair_name, pairs in (("Equal Pairs", equal_pairs),
                             ("Different-sized Pairs", combo_pairs)):
        for feature in ("pos", "word"):
            print("%s %s" % (pair_name, feature.capitalize()))
            for (x, y) in pairs:
                vals = [stat_fun(x, y, feature) for _ in range(reps)]
                print("  %s %s = %s" %(x, y, meanstdv(vals)))

    for feature, pairs in (("pos", tag_pairs), ("word", word_pairs)):
        print("Eve-Peter %s" % (feature.capitalize()))
        for (x, y) in pairs:
            val = sum([stat_fun(x, y, feature) for _ in range(reps)])
            print("  %s %s = %s" %(x, y, meanstdv(vals)))

    # args = parse_args(argv[1:])
    # for i in main(args):
    #     print i
