import unittest
from os import path
from os.path import dirname, abspath

from datatypes import MorToken
from dump_speaker_data import extract_feature_utterances, rewriter
from sample_size_test import generate_ngrams
from stats import dice_stat

here = dirname(abspath(__file__))

class TestUtteranceExtracting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "setting up", cls
        cls.filename = path.join(here, "fixtures", "eve01.xml")
        cls.utterances = extract_feature_utterances([cls.filename], 'word', 'MOT')
        cls.corpus = reduce(list.__add__, cls.utterances)  # flatten


    def test_extraction(self):
        mot_words = extract_feature_utterances([self.filename], 'word', 'MOT')
        self.assertEqual(len(mot_words), 804)

        chi_pos = extract_feature_utterances([self.filename], 'pos', 'CHI')
        self.assertEqual(len(chi_pos), 741)

        all_words = extract_feature_utterances([self.filename], 'pos')
        self.assertEqual(len(all_words), 1588)

    def test_statistic_funs(self):
        ngrams = generate_ngrams(3, self.corpus)
        self.assertEqual(dice_stat(ngrams, ngrams), 1)
        self.assertEqual(dice_stat(ngrams, []), 0)

    def test_ngrams(self):
        ngrams = generate_ngrams(2, self.corpus)
        for first, second in [ngrams[i:i+2] for i in range(len(ngrams) - 2)]:
            self.assertEquals(first.split()[-1], second.split()[0])

    def _mtf(self, prefix=None, word=None, stem=None, pos=None, subPos=None, sxfx=None, sfx=None):
        return MorToken(prefix or [], word, stem, pos, subPos or [], sxfx or [], sfx or [])


    def test_translation(self):
        pairs = (
            (self._mtf(word="nook", pos="fam"), "chi"),
            (self._mtf(word="stool",pos="n", subPos=["prop"], sfx=["POSS"]),
             "n-pr"),
            (self._mtf(word="steve", pos="n", subPos=["prop"], sfx=["PL"]),
             "n-pr-pl"),
             (self._mtf(word="steve", pos="n", subPos=["prop"], sfx=["PL"]),
             "n-pr-pl"),
             (self._mtf(pos="part", sfx=["PERF"]), "prt-pf"),
             (self._mtf(pos="part", sfx=["PROG"]), "prt-pg"),
             (self._mtf(pos=""), "ptl"),
            )

        for input, expected in pairs:
            self.assertEquals(rewriter(input), expected)

if __name__ == "__main__":
    unittest.main()
