def meanstdv(x):
    """ from
    http://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html
    """

    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std

def dice_stat(a, b):
    # calculate the dice coefficient
    a, b = set(a), set(b)
    shared = len(a & b)
    try:
        coeff = (2.0 * shared)/(len(a) + len(b))
    except ZeroDivisionError:
        return 0
    return round(coeff, 5)

# Jaccard
def jaccard_stat(a, b):
    # calculate the jaccard coefficient
    a, b = set(a), set(b)
    shared = len(a & b)
    try:
        coeff = shared / float(len(a) + len(b) - shared)
    except ZeroDivisionError:
        return 0
    return round(coeff, 5)

#McNemar
def mcnemar_stat(a,b,c,d):
    # calculate the mcnemar
    # square = all tokens produced in (a or b) and (c or d)
    pass

