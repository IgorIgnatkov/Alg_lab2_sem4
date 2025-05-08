import numpy as np
from PIL import Image
import json
import math
from block import reassemble_from_blocks
from algs.DCT import idct_2d_transform
from quantization import dequantize
from zigzag import inverse_zigzag_scan
from algs.RLE import rle_decode_ac_coefficients
from VLI import decode_vli
from algs.huffman import HuffmanTable, huffman_decode_data
from color import ycbcr_to_rgb

def upsample_channel_nearest_neighbor(channel, target_height, target_width):
    if channel.size == 0:
        return np.full((target_height, target_width), 128, dtype=np.uint8)
    upsampled = channel.repeat(2, axis=0).repeat(2, axis=1)
    return upsampled[:target_height, :target_width]

def dpcm_decode_dc(dc_diffs):
    dc_diffs = np.array(dc_diffs, dtype=np.int32)
    dc_coeffs = np.empty_like(dc_diffs)
    dc_coeffs[0] = dc_diffs[0]
    for i in range(1, len(dc_diffs)):
        dc_coeffs[i] = dc_diffs[i] + dc_coeffs[i-1]
    return dc_coeffs.tolist()

def decompress_image(input_path, output_path):
    with open(input_path, 'rb') as f:
        magic = f.read(6)
        header_len = int.from_bytes(f.read(4), 'big')
        metadata_bytes = f.read(header_len)
        metadata = json.loads(metadata_bytes.decode('utf-8'))

        y_len = metadata['data_len_y']
        cb_len = metadata['data_len_cb']
        cr_len = metadata['data_len_cr']

        y_data = f.read(y_len)
        cb_data = f.read(cb_len)
        cr_data = f.read(cr_len)

    block_size = metadata['block_size']
    width = metadata['original_width']
    height = metadata['original_height']

    q_y = np.array(metadata['q_table_y'], dtype=np.uint8)
    q_c = np.array(metadata['q_table_c'], dtype=np.uint8)

    huff_dc_y = HuffmanTable(metadata['huff_dc_y_bits'], metadata['huff_dc_y_huffval'])
    huff_ac_y = HuffmanTable(metadata['huff_ac_y_bits'], metadata['huff_ac_y_huffval'])
    huff_dc_c = HuffmanTable(metadata['huff_dc_c_bits'], metadata['huff_dc_c_huffval'])
    huff_ac_c = HuffmanTable(metadata['huff_ac_c_bits'], metadata['huff_ac_c_huffval'])

    padded_dims = {
        'Y': tuple(metadata['padded_dims_y']),
        'Cb': tuple(metadata['padded_dims_cb']),
        'Cr': tuple(metadata['padded_dims_cr'])
    }

    components = {
        'Y': (y_data, huff_dc_y, huff_ac_y, q_y, padded_dims['Y']),
        'Cb': (cb_data, huff_dc_c, huff_ac_c, q_c, padded_dims['Cb']),
        'Cr': (cr_data, huff_dc_c, huff_ac_c, q_c, padded_dims['Cr'])
    }

    reconstructed_channels = {}

    for comp_name, (comp_data, dc_table, ac_table, q_matrix, (padded_h, padded_w)) in components.items():
        num_blocks = (padded_h // block_size) * (padded_w // block_size)
        decoded_units = huffman_decode_data(comp_data, dc_table, ac_table, num_blocks)

        dc_diffs = []
        quantized_blocks = []

        for dc_cat, dc_vli_bits, ac_rle in decoded_units:
            dc_diff = decode_vli(dc_cat, dc_vli_bits)
            dc_diffs.append(dc_diff)
            ac_coeffs = rle_decode_ac_coefficients(ac_rle, num_ac_coeffs=block_size*block_size - 1)
            zigzag_array = np.array([dc_diff] + ac_coeffs, dtype=np.int32)
            block = inverse_zigzag_scan(zigzag_array, block_size)
            quantized_blocks.append(block)

        dc_coeffs = dpcm_decode_dc(dc_diffs)

        final_blocks = []
        for i, quant_block in enumerate(quantized_blocks):
            quant_block[0, 0] = dc_coeffs[i]
            dequant_block = dequantize(quant_block, q_matrix)
            idct_block = idct_2d_transform(dequant_block)
            idct_block_shifted = idct_block + 128.0
            idct_block_clipped = np.clip(idct_block_shifted, 0, 255).astype(np.uint8)
            final_blocks.append(idct_block_clipped)

        reassembled = reassemble_from_blocks(final_blocks, padded_h, padded_w)

        if comp_name == 'Y':
            final = reassembled[:height, :width]
        else:
            final = reassembled[:math.ceil(height/2), :math.ceil(width/2)]

        reconstructed_channels[comp_name] = final

    y_channel = reconstructed_channels['Y']
    cb_upsampled = upsample_channel_nearest_neighbor(reconstructed_channels['Cb'], y_channel.shape[0], y_channel.shape[1])
    cr_upsampled = upsample_channel_nearest_neighbor(reconstructed_channels['Cr'], y_channel.shape[0], y_channel.shape[1])

    ycbcr_image = np.stack((y_channel, cb_upsampled, cr_upsampled), axis=-1)
    rgb_image = ycbcr_to_rgb(ycbcr_image)

    img_out = Image.fromarray(rgb_image)
    img_out.save(output_path)
