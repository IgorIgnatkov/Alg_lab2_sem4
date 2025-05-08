import numpy as np

def _get_С_factor(k):
    return 1.0 / np.sqrt(2.0) if k == 0 else 1.0

def _create_dct_1d_matrix(N):
    T = np.zeros((N, N), dtype=np.float64)
    for k in range(N):
        for n in range(N):
            T[k, n] = np.cos((2 * n + 1) * k * np.pi / (2 * N))
    return T

def dct_2d_transform(block):
    N = block.shape[0]
    if block.dtype == np.uint8:
        block = block.astype(np.float64) - 128.0
    else:
        block = block.astype(np.float64)

    T = _create_dct_1d_matrix(N)
    dct_intermediate = T @ block @ T.T

    C = np.array([_get_C_factor(k) for k in range(N)], dtype=np.float64)
    C_matrix = np.outer(C, C)

    dct_coeffs = 0.25 * C_matrix * dct_intermediate
    return dct_coeffs

def idct_2d_transform(dct_coeffs):
    N = dct_coeffs.shape[0]

    T = _create_dct_1d_matrix(N)
    C = np.array([_get_C_factor(k) for k in range(N)], dtype=np.float64)
    C_matrix = np.outer(C, C)

    S_prime = C_matrix * dct_coeffs

    block = 0.25 * (T.T @ S_prime @ T)
    return block
