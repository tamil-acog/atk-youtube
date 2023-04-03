import bisect


def find_lt(a, x):
    """Find rightmost value less than x"""
    if x == '00:00:00' or x == 0:
        return 0
    i = bisect.bisect_left(a, x)
    if i:
        if a[i] == x:
            return i
        else:
            return i+1










