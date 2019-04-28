import numpy as np
# Modified version of levenshtein distance taken
# from https://www.python-course.eu/levenshtein_distance.php
def iterative_levenshtein(s, t):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    rows = len(s)+1
    cols = len(t)+1
    dist = [[[0,[]] for x in range(cols)] for x in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for i in range(1, rows):
        dist[i][0] = [i,[]]
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for i in range(1, cols):
        dist[0][i] = [i, []]

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 1
            x = [dist[row-1][col][0]+1, dist[row][col-1][0]+1, dist[row-1][col-1][0]+cost]
            index = x.index(min(x))
            if (index==0):
                dist[row][col][0] = x[0]
                dist[row][col][1] = dist[row-1][col][1] + [('ins',col,row)]
            elif (index==1):
                dist[row][col][0] = x[1]
                dist[row][col][1] = dist[row][col-1][1] + [('del',col,row)]
            elif (index==2):
                dist[row][col][0] = x[2]
                if (cost==1):
                    dist[row][col][1] = dist[row-1][col-1][1] + [('sub',col,row)]
                else:
                    dist[row][col][1] = dist[row-1][col-1][1]
            else:
                assert(False)
    return dist[row][col]

if __name__=="__main__":
    A = [(42, 2), (42,2), (49,2), (49,2), (51,2), (51,2),  (49,4),  (47, 2), (47,2), (46,2), (46,2), (44,2), (44,2), (42,4),
             (49, 2), (49,2), (47,2), (47,2), (46,2), (46,2), (44,4),  (49, 2), (49,2), (47,2), (47,2), (46,2), (46,2), (44,4),
              (42, 2), (42,2), (49,2), (49,2), (51,2), (51,2),  (49,4),  (47, 2), (47,2), (46,2), (46,2), (44,2), (44,2), (42,4)]
    inf = np.inf
    B = [(84.0, 1.0), (42.0, 3.0), (42.0, 2.0), (49.0, 3.0), (77.0, 2.0), (51.0, 2.0), (51.0, 2.0), (77.0, 1.0), (49.0, 2.0), (49.0, 1.0), (47.0, 2.0), (47.0, 2.0), (46.0, 2.0), (46.0, 2.0), (44.0, 2.0), (44.0, 3.0), (42.0, 1.0), (42.0, 2.0), (42.0, 1.0), (49.0, 2.0), (49.0, 2.0), (47.0, 2.0), (47.0, 2.0), (46.0, 2.0), (46.0, 3.0), (75.0, 1.0), (44.0, 3.0), (-inf, 1.0), (49.0, 2.0), (49.0, 1.0), (77.0, 1.0), (49.0, 2.0), (47.0, 2.0), (47.0, 2.0), (46.0, 2.0), (46.0, 2.0), (44.0, 3.0), (-inf, 1.0), (42.0, 3.0), (42.0, 2.0), (49.0, 2.0), (49.0, 2.0), (51.0, 2.0), (51.0, 3.0), (49.0, 3.0), (-inf, 1.0), (47.0, 3.0), (47.0, 2.0), (46.0, 2.0), (46.0, 2.0), (44.0, 2.0), (44.0, 2.0), (42.0, 1.0), (42.0, 2.0)]
    C = [(42.0, 2.0), (42.0, 2.0), (49.0, 2.0), (49.0, 2.0), (51.0, 2.0), (51.0, 2.0), (49.0, 3.0), (-inf, 1.0), (47.0, 1.0), (-inf, 1.0), (47.0, 1.0), (-inf, 1.0), (46.0, 2.0), (46.0, 2.0), (44.0, 2.0), (44.0, 2.0), (42.0, 3.0), (-inf, 1.0), (49.0, 2.0), (49.0, 2.0), (47.0, 2.0), (47.0, 2.0), (46.0, 2.0), (46.0, 2.0), (44.0, 4.0), (49.0, 2.0), (49.0, 2.0), (47.0, 2.0), (47.0, 2.0), (46.0, 2.0), (46.0, 2.0), (44.0, 4.0), (42.0, 2.0), (42.0, 2.0), (49.0, 2.0), (49.0, 2.0), (51.0, 2.0), (51.0, 1.0), (49.0, 4.0), (-inf, 1.0), (47.0, 2.0), (47.0, 1.0), (46.0, 2.0), (46.0, 2.0), (44.0, 2.0), (44.0, 2.0), (42.0, 4.0), (35.0, 2.0)]
    print(iterative_levenshtein(A, B)[0]/len(B))
    print(iterative_levenshtein(A, C)[0]/len(C))
