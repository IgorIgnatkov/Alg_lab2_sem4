import numpy as np
import os
from PIL import Image
import math
import json
from color import rgb_to_ycbcr
from block import split_into_blocks
from algs.DCT import dct_2d_transform
from quantization import adjust_quantization_matrix, quantize, BASE_Q_LUMINANCE, BASE_Q_CHROMINANCE
from zigzag import zigzag_scan
from algs.RLE import rle_encode_ac_coefficients
from VLI import get_vli_category_and_value
from algs.huffman import HuffmanTable, huffman_encode_data
from huffman_tables import DEFAULT_DC_LUMINANCE_BITS, DEFAULT_DC_LUMINANCE_HUFFVAL
from huffman_tables import DEFAULT_AC_LUMINANCE_BITS, DEFAULT_AC_LUMINANCE_HUFFVAL
from huffman_tables import DEFAULT_DC_CHROMINANCE_BITS, DEFAULT_DC_CHROMINANCE_HUFFVAL
from huffman_tables import DEFAULT_AC_CHROMINANCE_BITS, DEFAULT_AC_CHROMINANCE_HUFFVAL

def downsample_channel_420(channel):
    original_height, original_width = channel.shape
    new_height = math.ceil(original_height / 2)
    new_width = math.ceil(original_width / 2)
    downsampled = np.zeros((new_height, new_width), dtype=np.uint8)
    for r in range(new_height):
        for c in range(new_width):
            block = channel[r*2:min(r*2+2, original_height), c*2:min(c*2+2, original_width)]
            downsampled[r, c] = int(np.round(np.mean(block.astype(np.float64))))
    return downsampled

def dpcm_encode_dc(dc_coeffs):
    dc_coeffs = np.array(dc_coeffs, dtype=np.int32)
    diffs = np.empty_like(dc_coeffs)
    diffs[0] = dc_coeffs[0]
    for i in range(1, len(dc_coeffs)):
        diffs[i] = dc_coeffs[i] - dc_coeffs[i-1]
    return diffs.tolist()


def compress_image(image_path, output_path, quality=75, block_size=8):
    print(f"Сжатие {image_path} с качеством {quality}")

    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img_rgb = np.array(img)


    height, width, _ = img_rgb.shape

    ycbcr = rgb_to_ycbcr(img_rgb)
    y = ycbcr[:, :, 0]
    cb = ycbcr[:, :, 1]
    cr = ycbcr[:, :, 2]

    cb_ds = downsample_channel_420(cb)
    cr_ds = downsample_channel_420(cr)

    q_y = adjust_quantization_matrix(BASE_Q_LUMINANCE, quality)
    q_c = adjust_quantization_matrix(BASE_Q_CHROMINANCE, quality)

    huff_dc_y = HuffmanTable(DEFAULT_DC_LUMINANCE_BITS, DEFAULT_DC_LUMINANCE_HUFFVAL)
    huff_ac_y = HuffmanTable(DEFAULT_AC_LUMINANCE_BITS, DEFAULT_AC_LUMINANCE_HUFFVAL)
    huff_dc_c = HuffmanTable(DEFAULT_DC_CHROMINANCE_BITS, DEFAULT_DC_CHROMINANCE_HUFFVAL)
    huff_ac_c = HuffmanTable(DEFAULT_AC_CHROMINANCE_BITS, DEFAULT_AC_CHROMINANCE_HUFFVAL)

    components = {
        'Y': (y, q_y, huff_dc_y, huff_ac_y),
        'Cb': (cb_ds, q_c, huff_dc_c, huff_ac_c),
        'Cr': (cr_ds, q_c, huff_dc_c, huff_ac_c)
    }

    compressed_data = {}
    padded_dims = {}
    total_blocks = 0

    for comp_name, (channel, q_matrix, dc_table, ac_table) in components.items():
        blocks = split_into_blocks(channel, block_size, fill_value=128)
        padded_height = math.ceil(channel.shape[0] / block_size) * block_size
        padded_width = math.ceil(channel.shape[1] / block_size) * block_size
        padded_dims[comp_name] = (padded_height, padded_width)

        quantized_blocks = []
        dc_coeffs = []

        for block in blocks:
            block_shifted = block.astype(np.float64) - 128.0
            dct_block = dct_2d_transform(block_shifted)
            quant_block = quantize(dct_block, q_matrix)
            quantized_blocks.append(quant_block)
            dc_coeffs.append(quant_block[0, 0])

        dc_diffs = dpcm_encode_dc(dc_coeffs)

        data_units = []
        for i, quant_block in enumerate(quantized_blocks):
            dc_diff = dc_diffs[i]
            dc_cat, dc_vli = get_vli_category_and_value(dc_diff)
            ac_coeffs = zigzag_scan(quant_block)[1:]
            ac_rle = rle_encode_ac_coefficients(ac_coeffs.tolist())
            data_units.append((dc_cat, dc_vli, ac_rle))

        compressed_bytes = huffman_encode_data(data_units, dc_table, ac_table)
        compressed_data[comp_name] = compressed_bytes
        total_blocks += len(blocks)
        print(f"{comp_name}: {len(blocks)} blocks, compressed size {len(compressed_bytes)} bytes")

    metadata = {
        "original_width": width,
        "original_height": height,
        "block_size": block_size,
        "quality": quality,
        "padded_dims_y": padded_dims['Y'],
        "padded_dims_cb": padded_dims['Cb'],
        "padded_dims_cr": padded_dims['Cr'],
        "q_table_y": q_y.tolist(),
        "q_table_c": q_c.tolist(),
        "huff_dc_y_bits": huff_dc_y.bits,
        "huff_dc_y_huffval": huff_dc_y.huffval,
        "huff_ac_y_bits": huff_ac_y.bits,
        "huff_ac_y_huffval": huff_ac_y.huffval,
        "huff_dc_c_bits": huff_dc_c.bits,
        "huff_dc_c_huffval": huff_dc_c.huffval,
        "huff_ac_c_bits": huff_ac_c.bits,
        "huff_ac_c_huffval": huff_ac_c.huffval,
        "data_len_y": len(compressed_data['Y']),
        "data_len_cb": len(compressed_data['Cb']),
        "data_len_cr": len(compressed_data['Cr']),
    }

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, 'wb') as f:
        f.write(b'MYJPEG')
        header_bytes = json.dumps(metadata).encode('utf-8')
        f.write(len(header_bytes).to_bytes(4, 'big'))
        f.write(header_bytes)
        f.write(compressed_data['Y'])
        f.write(compressed_data['Cb'])
        f.write(compressed_data['Cr'])


    print(f"Сжатие завершено, файл сохранен в: {output_path}")
