
def are_equivalent( a, b ):
    """
    Returns true if two lists are equivalent
    to each other.
    Ordering is important.

    [1, 2, 3], [1, 2, 3] == True
    [1, 2, 3], [1, 3, 2] == False
    [1, 2, 3], [4, 5, 6] == False
    """
    difference = [i for i, j in zip(a, b) if i != j]
    return len(difference) == 0

def not_equivalent( a, b ):
    return not are_equivalent( a, b )

