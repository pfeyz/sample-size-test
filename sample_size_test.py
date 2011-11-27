#! /usr/bin/env python2

"""
TODO:

  - change sample_size to mean the number of ngrams per sample.

  - when atomic unit is set to utterance, generate ngrams from utterances until
    there are more than sample_size tokens ngrams generated.

"""
from __future__ import print_function
import itertools
import pickle
import random
from datetime import datetime
from multiprocessing import Pool

from os import path
from stats import dice_stat, meanstdv

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

def pick_random_utterances(samples, ngrams):
    num_ngrams = 0
    picked = []
    while num_ngrams < samples:
        g = random.choice(ngrams)
        num_ngrams += len(g)
        picked.extend(g)
    return picked

def stat_fun(args):
    x, y, ngrams, reps = args
    vals = [dice_stat(pick_random_utterances(x, ngrams),
                      pick_random_utterances(y, ngrams))
                      for _ in range(reps)]
    return x, y, meanstdv(vals)

def logger():
    times = [datetime.now(), datetime.now()]
    def log(message):
        start_time, last_job = times
        now = datetime.now()
        print("\n%s in %s [%s]" % (message, now - last_job, now - start_time))
        times[1] = now
    return log

if __name__ == "__main__":
    log = logger()
    utterance_file_base = path.join('utterances', 'MOT')
    reps = 10000
    n_size = 2

    word_file = utterance_file_base + "-word.pk"
    pos_file = utterance_file_base + "-pos.pk"

    base_sizes = (100, 200, 500, 1000, 5000)
    equal_pairs = [(i, i) for i in base_sizes]
    combo_pairs = [(a, b) for a, b in itertools.combinations(base_sizes, 2)
                   if a != b]
    tag_pairs = [(175, 412), (308, 433), (362, 498), (425, 540), (243, 548),
                 (428, 598), (556, 600), (659, 632)]
    word_pairs = [(1004, 3652), (2159, 3886), (2607, 4409), (3352, 6277),
                  (898, 6708), (3623, 8622), (5673, 9259), (8794, 10368)]

    start_time = then = datetime.now()
    word_utterances = pickle.load(open(word_file))
    pos_utterances = pickle.load(open(pos_file))
    pool = Pool()
    word_ngrams = [generate_ngrams(n_size, u) for u in word_utterances]
    pos_ngrams = [generate_ngrams(n_size, u) for u in pos_utterances]

    log("set up")
    print("Starting analysis")
    for pair_name, pairs in (("Equal Pairs", equal_pairs),
                             ("Different-sized Pairs", combo_pairs)):
        for feature, grams in (("pos", pos_ngrams), ("word", word_ngrams)):
            print("%s %s" % (pair_name, feature.capitalize()))
            args = [(x, y, grams, reps) for x, y in pairs]
            for x, y, (mean, stdev) in pool.map(stat_fun, args):
                print("dice(%s %s) = %s, %s" % (x, y, mean, stdev))
            del args
            log("ran analysis")

    for feature, pairs, grams in (("pos", tag_pairs, pos_ngrams),
                                  ("word", word_pairs, word_ngrams)):
        print("Eve-Peter %s" % (feature.capitalize()))
        args = [(x, y, grams, reps) for x, y in pairs]
        for x, y, (mean, stdev) in pool.map(stat_fun, args):
            print("dice(%s %s) = %s, %s" % (x, y, mean, stdev))
        del args
        log("ran analysis")

    pool.close()
    pool.join()
