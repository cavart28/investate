import numpy as np

def chunk_up_down_count(chunk, n_derivative=0):

    diff_chunk = np.diff(chunk, n_derivative)

    first = diff_chunk[0]
    n_up = 0
    for second in diff_chunk[1:]:
        if first <= second:
            n_up += 1
        first = second
    n_down = len(diff_chunk) - 1 - n_up

    return n_up, n_down

if __name__ == '__main__':

    test = [1,2,3,4,4,4,3,2,2,1,-1,2,4,6,9]
    print(chunk_up_down_count(test, n_derivative=1))