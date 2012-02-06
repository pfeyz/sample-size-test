#! /usr/bin/env python2

"""
TODO:

  - change sample_size to mean the number of ngrams per sample.

  - when atomic unit is set to utterance, generate ngrams from utterances until
    there are more than sample_size tokens ngrams generated.

"""
from __future__ import print_function
import itertools
from datetime import datetime
from multiprocessing import Pool
from sys import argv, exit

from util.stats import dice_stat, meanstdv
from util.misc import pick_random_utterances, get_utterances

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

if __name__ == "__main__":

    try:
        tagged_file, speaker = argv[1:3]
    except ValueError:
        print("Script requires two args: Filename of slash-tagged file to analyze and speaker name.")
        exit()
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
    word_utterances = get_utterances(tagged_file, speaker, lambda word, pos: word)
    pos_utterances = get_utterances(tagged_file, speaker, lambda word, pos: pos)
    print(list(word_utterances))
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
