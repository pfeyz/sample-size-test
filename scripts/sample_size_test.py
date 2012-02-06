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
from tag_translations import rewrite_rules

class NGramException(Exception):
    pass

def generate_ngrams(n, sentence):
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

    if n > len(sentence):
        raise NGramException('Not enough words to generate an ngram')
    if n < 1:
        raise NGramException('Cannot compute ngram with n < 1: %s' % n)
    return [" ".join(sentence[i:i+n])
            for i in range(len(sentence) - n + 1)]

def pick_random_utterances(samples, ngrams):
    """
    args
      samples: the number of samples to generate
      ngrams: the ngrams to pick from

    Erin: i need it to count types of bigrams instead of tokens for the sample
        sizes. so i changed the pick_random_utterances block of code a bit.  my
        worry is that what i did returns not a list of lists but a list of
        bigrams. and it feeds dice_stat.  and i don't know if that will be a
        problem.  i can send you the old and new blocks of code.  or you wanna
        use github?
    """
    num_ngrams = 0
    picked = []
    while num_ngrams < samples:
        utterance_grams = random.choice(ngrams)
        keepers = []
        for ng in utterance_grams:
            if ng in picked:
                utterance_grams.remove(ng)
                keepers.extend(utterance_grams)
        if keepers:  # ignore blank utterances
            picked.append(keepers)
            num_ngrams += len(keepers)

    return picked

def stat_fun(args):
    x, y, ngrams, reps = args
    vals = [dice_stat(pick_random_utterances(x, ngrams),
                      #takes an utterance selected randomly and adds all grams in it to g
                      pick_random_utterances(y, ngrams))
                      for _ in range(reps)]
    return x, y, meanstdv(vals)

def report(action, then, start):
    n = datetime.now()
    print("\n%s in %s [%s]" % (action, n - then, n - start))
    return n

def get_utterances(filename, target_speaker="", filter_fun=None):
    with open(filename) as fh:
        corp = None
        for line in fh:
            if not line.strip():
                continue
            tokens = line.split()
            speaker, words = tokens[0], tokens[1:]
            if speaker == "Parsing":
                corp = line.strip().split(" ")[1].split("/")[-1]  # oh god.
            if target_speaker == "" or speaker == target_speaker:
                yield corp, " ".join(filter_fun(*(w.split('/'))) for w in words)

if __name__ == "__main__":
    reps = 1
    n_size = 2

    base_sizes = (100, 200, 500, 1000, 5000)
    equal_pairs = [(i, i) for i in base_sizes]
    combo_pairs = [(a, b) for a, b in itertools.combinations(base_sizes, 2)
                   if a != b]
    tag_pairs = [(175, 412), (308, 433), (362, 498), (425, 540), (243, 548),
                 (428, 598), (556, 600), (659, 632)]
    word_pairs = [(1004, 3652), (2159, 3886), (2607, 4409), (3352, 6277),
                  (898, 6708), (3623, 8622), (5673, 9259), (8794, 10368)]

    start_time = then = datetime.now()
    word_utterances = get_utterances("larc-tagged-output.txt", "MOT", lambda word, pos: word)
    pos_utterances = get_utterances("larc-tagged-output.txt", "MOT", lambda word, pos: pos)
    pool = Pool()
    # generates a list lists, i.e. a list of utterances broken into ngrams.
    word_ngrams = [generate_ngrams(n_size, u) for u in word_utterances
                   if len(u) >= n_size]
    pos_ngrams = [generate_ngrams(n_size, u) for u in pos_utterances
                  if len(u) >= n_size]
    print("# word n-grams is ", len(word_ngrams))
    print("# tag n-grams is ", len(pos_ngrams))

    then = report("set up", then, start_time)
    print("Starting analysis")
    for pair_name, pairs in (("Equal Pairs", equal_pairs),
                             ("Different-sized Pairs", combo_pairs)):
        for feature, grams in (("pos", pos_ngrams), ("word", word_ngrams)):
            print("%s %s" % (pair_name, feature.capitalize()))
            args = [(x, y, grams, reps) for x, y in pairs]
            for x, y, (mean, stdev) in pool.map(stat_fun, args):
                print("dice(%s %s) = %s, %s" % (x, y, str(mean)[:6],
                                                str(stdev)[:6]))
                # made mean and sd strings to shorten to 4 dec places
            del args
            then = report("ran analysis", then, start_time)

    for feature, pairs, grams in (("pos", tag_pairs, pos_ngrams),
                                  ("word", word_pairs, word_ngrams)):
        print("Eve-Peter %s" % (feature.capitalize()))
        args = [(x, y, grams, reps) for x, y in pairs]
        for x, y, (mean, stdev) in pool.map(stat_fun, args):
            print("dice(%s %s) = %s, %s" % (x, y, str(mean)[:6], str(stdev)[:6]))
        del args
        then = report("ran analysis", then, start_time)

    pool.close()
    pool.join()
