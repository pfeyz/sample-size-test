import random

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

