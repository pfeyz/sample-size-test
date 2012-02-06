import re
import sys

def filter_utterance(ufile, filter_fun, keep_corpora_markers=True):
    """ Yields each line in ufile, omitting words that fail filter_fun.

    ufile: filename of utterance file
    filter_fun: function which accepts a (word, tag) tuple and returns a boolean
                True = keep word, False = drop.
    keep_corpora_markers: if False, will omit lines marking file boundaries.
    """

    with open(ufile) as fh:
        for line in fh:
            if re.match("^Parsing.*", line):
                if keep_corpora_markers:
                    yield line
                continue
            tokens = line.split()
            try:
                speaker = tokens[0]
                words = tokens[1:]
                new_line = []
                for word, tag in [w.split('/') for w in words]:
                    if filter_fun(word, tag):
                        new_line.append("{0}/{1}".format(word, tag))
            except ValueError:
                print "Could not parse line", line
            if new_line:
                yield "{0} {1}".format(speaker, " ".join(new_line))

def fail_if_functional(word, tag):
    " Returns false if a word is a funtional unit "
    if tag in ["det", "aux", "mod"]:
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "  Usage: utterance_filter.py utterances.txt"
    else:
        ufile = sys.argv[1]
        for line in filter_utterance(ufile, fail_if_functional):
            print line
