def rle_encode_ac_coefficients(ac_coeffs):
    rle = []
    zero_run = 0

    for coeff in ac_coeffs:
        if coeff == 0:
            zero_run += 1
            if zero_run == 16:
                rle.append((15, 0))  # ZRL
                zero_run = 0
        else:
            rle.append((zero_run, coeff))
            zero_run = 0

    rle.append((0, 0))
    return rle

def rle_decode_ac_coefficients(rle_encoded, num_ac_coeffs=63):
    ac_coeffs = []
    for run_length, value in rle_encoded:
        if run_length == 0 and value == 0:
            remaining = num_ac_coeffs - len(ac_coeffs)
            ac_coeffs.extend([0] * remaining)
            break
        elif run_length == 15 and value == 0:
            ac_coeffs.extend([0] * 16)
        else:
            ac_coeffs.extend([0] * run_length)
            ac_coeffs.append(value)

        if len(ac_coeffs) >= num_ac_coeffs:
            ac_coeffs = ac_coeffs[:num_ac_coeffs]
            break

    if len(ac_coeffs) < num_ac_coeffs:
        ac_coeffs.extend([0] * (num_ac_coeffs - len(ac_coeffs)))

    return ac_coeffs
