import numpy as np

BASE_Q_LUMINANCE = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
], dtype=np.uint8)

BASE_Q_CHROMINANCE = np.array([
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99]
], dtype=np.uint8)

def adjust_quantization_matrix(base_matrix, quality_factor):

    base_matrix_float = base_matrix.astype(np.float64)

    if quality_factor < 50:
        scale_factor = 5000.0 / quality_factor
    else:
        scale_factor = 200.0 - 2.0 * quality_factor

    adjusted = (base_matrix_float * scale_factor + 50.0) / 100.0
    adjusted = np.floor(adjusted)
    adjusted[adjusted < 1] = 1
    adjusted[adjusted > 255] = 255

    return adjusted.astype(np.uint8)

def quantize(dct_block, quant_matrix):
    quantized = np.round(dct_block / quant_matrix.astype(np.float64))
    return quantized.astype(np.int32)

def dequantize(quantized_block, quant_matrix):
    dequantized = quantized_block.astype(np.float64) * quant_matrix.astype(np.float64)
    return dequantized
