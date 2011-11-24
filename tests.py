import unittest
from os import path
from os.path import dirname, abspath

from dump_speaker_data import extract_feature_utterances
from sample_size_test import generate_ngrams
from stats import dice_stat

here = dirname(abspath(__file__))

class TestUtteranceExtracting(unittest.TestCase):
    def setUp(self):
        self.filename = path.join(here, "fixtures", "eve01.xml")
        self.utterances = extract_feature_utterances([self.filename],
                                                     'word', 'MOT', 0)
        self.corpus = reduce(list.__add__, self.utterances)  # flatten

    def test_extraction(self):
        mot_words = extract_feature_utterances([self.filename],
                                               'word', 'MOT', 0)
        self.assertEqual(len(mot_words), 804)

        chi_pos = extract_feature_utterances([self.filename], 'pos', 'CHI', 0)
        self.assertEqual(len(chi_pos), 741)

        all_words = extract_feature_utterances([self.filename], 'pos')
        self.assertEqual(len(all_words), 1588)

    def test_statistic_funs(self):
        ngrams = generate_ngrams(3, self.corpus)
        self.assertEqual(dice_stat(ngrams, ngrams), 1)

    def test_ngrams(self):
        ngrams = generate_ngrams(2, self.corpus)
        for first, second in [ngrams[i:i+2] for i in range(len(ngrams) - 2)]:
            self.assertEquals(first.split()[-1], second.split()[0])

if __name__ == "__main__":
    unittest.main()
