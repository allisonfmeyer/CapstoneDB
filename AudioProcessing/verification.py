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
    A = [(54,1.0), (54, 1.0), (56, 1.0), (57, 1.0)]
    B = [(54,2.0), (56, 1.0), (58, 1.0)]
    print(iterative_levenshtein(A, B))
