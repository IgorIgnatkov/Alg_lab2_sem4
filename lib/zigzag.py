import numpy as np

def zigzag_scan(matrix):
    N = matrix.shape[0]
    result = np.empty(N * N, dtype=matrix.dtype)
    index = 0
    row, col = 0, 0
    up = True

    for _ in range(N * N):
        result[index] = matrix[row, col]
        index += 1

        if up:
            if col == N - 1:
                row += 1
                up = False
            elif row == 0:
                col += 1
                up = False
            else:
                row -= 1
                col += 1
        else:
            if row == N - 1:
                col += 1
                up = True
            elif col == 0:
                row += 1
                up = True
            else:
                row += 1
                col -= 1

    return result

def inverse_zigzag_scan(array, N):
    matrix = np.empty((N, N), dtype=array.dtype)
    index = 0
    row, col = 0, 0
    up = True

    for _ in range(N * N):
        matrix[row, col] = array[index]
        index += 1

        if up:
            if col == N - 1:
                row += 1
                up = False
            elif row == 0:
                col += 1
                up = False
            else:
                row -= 1
                col += 1
        else:
            if row == N - 1:
                col += 1
                up = True
            elif col == 0:
                row += 1
                up = True
            else:
                row += 1
                col -= 1

    return matrix
