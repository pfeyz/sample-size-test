from dump_speaker_data import rewriter, rule_size
from tag_translations import rewrite_rules as rules

if __name__ == "__main__":
    for pattern, rewrite in sorted(rules, key=rule_size, reverse=True):
        print rule_size((pattern, rewrite)),
        for key, val in sorted(pattern.items(), key=lambda x: x[0]):
            if isinstance(val, str):
                print "{0}={1}".format(key, val),
            else:
                print "{0}={1}".format(key, ",".join(val)),
        print "->", rewrite
