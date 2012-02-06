import glob
import sys
from os.path import basename

from dump_speaker_data import rewriter
from talkbank_parser import MorParser

def xml_to_tagfile(filename):
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    corpus = parser.parse(filename)
    for speaker, tokens in corpus:
        yield speaker, [rewriter(t) for t in tokens]


if __name__ == "__main__":
    files = sorted(glob.glob("/home/paul/corpora/Brown/Eve/*.xml"))
    for xmlfile in files:
        sys.stderr.write(xmlfile + "\n")
        outf = ('split-outputs/MOT-%s' % basename(xmlfile)).rstrip('.xml') + '.txt'
        print outf
        with open(outf, 'w') as fh:
            for speaker, words in xml_to_tagfile(xmlfile):
                if speaker != "MOT":
                    continue
                 #            with open('larc-tagged-output-mother.txt', 'w') as fh:
                fh.write(" ".join(["{0}/{1}".format(
                    pair[0] if pair[0] else 'XXX', pair[1].upper() if pair[1] else 'YYY')
                    for pair in words]) + "\n")
