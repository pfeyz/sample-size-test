# -*- py-shell-name: "python2" -*-

from __future__ import print_function
import itertools
import logging
import pickle
import sys
from os.path import dirname, abspath, basename, splitext
from os.path import join as pjoin

from talkbank_parser import MorParser
from tag_translations import rewrite_rules

here = dirname(abspath(__file__))

logging.basicConfig(filename='translations.log', format='[%(levelname)s] %(message)s')

def rule_size(rule):
    size = 0
    constraints, rewrite = rule
    for feature, pattern in constraints.items():
        if isinstance(pattern, str):
            size += 1
        else:
            for item in pattern:
                size += 1
    return size

class BoomException(Exception):
    pass

def rewriter(mortoken):
    """ Accepts a MorToken and returns the translated part of speech. If there
    is no suitable translation, mortoken.pos is returned.
    """

    token = mortoken._asdict()
    rules = sorted(rewrite_rules, key=rule_size, reverse=True)
    for pattern, rewrite in rules:
        # rule matches if pattern's values are equal to those in token. pattern
        # can be a subset.
        match = True
        for attrib, value in pattern.items():
            if isinstance(value, str):
                if token[attrib] != value:
                    match = False
            else:
                for part in value:
                    if part not in token[attrib]:
                        match = False
        if match:
            return mortoken.word, rewrite
    logging.warning("failed to translate {0}".format(mortoken.__repr__()))

    return mortoken.word, mortoken.pos

def extract_feature_utterances(filenames, feature, speaker=None, cutoff=0):
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    corpus = itertools.chain(*(parser.parse(i) for i in filenames))
    if feature == "pos":
        f = rewriter
    elif feature == "word":
        f = lambda x: x.word
    utterances = [[f(w) for w in u[1]]
                      for u in corpus
                      if ((u[0] == speaker or speaker is None)
                          and len(u[1]) >= cutoff)]

    return utterances

if __name__ == "__main__":
    try:
        speaker, feature, cutoff = sys.argv[1:4]
        filenames = sys.argv[4:]
    except ValueError:
        raise Exception("Three+ args required: speaker, feature (pos | word) "
                    "and xml files")

    name = splitext(basename(filenames[0]))[0]
    utterances = extract_feature_utterances(filenames, feature,
                                            speaker, int(cutoff))
    for line in utterances:
        print(line)
    outfn = pjoin(here, 'utterances', "%s-%s.pk" % (speaker, feature))
    print("pickling utterances")
    with open(outfn, 'w') as fh:
        pickle.dump(utterances, fh)
