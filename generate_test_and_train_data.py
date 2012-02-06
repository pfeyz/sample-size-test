from math import ceil, floor
from sys import argv, exit

if __name__ == "__main__":
    try:
        print argv
        infile, out1, out2, x, y = argv[1], argv[2], argv[3], int(argv[4]), int(argv[5])
    except IndexError:
        print "Script takes 3 args: inputfile, outx, outy, X, Y"
        print "output file 'outx' will be X / (X + Y) % of inputfile"
        print "output file 'outy' will be Y / (X + Y) % of inputfile"
        exit()
    with open(infile) as fh:
        lines = fh.readlines()

    num_lines = len(lines)
    denom = float(x + y)
    head, tail = ceil(num_lines * (x / denom)), floor(num_lines * (y / denom))
    head, tail = int(head), int(tail)
    assert (head + tail) == num_lines
    with open("{0}.txt".format(out1), 'w') as fh:
        for line in lines[:head]:
            fh.write(line)
    with open("{0}.txt".format(out2), 'w') as fh:
        for line in lines[head:]:
            fh.write(line)
