def get_vli_category_and_value(number):
    if number == 0:
        return 0, ""

    magnitude = abs(number)
    category = magnitude.bit_length()

    if number > 0:
        value_bits = bin(magnitude)[2:].zfill(category)
    else:
        temp_val = (1 << category) - 1 - magnitude
        value_bits = bin(temp_val)[2:].zfill(category)

    return category, value_bits

def decode_vli(category, value_bits_str):
    if category == 0:
        if value_bits_str == "":
            return 0

    value_from_bits = int(value_bits_str, 2)
    sign_threshold = 1 << (category - 1)

    if value_from_bits >= sign_threshold:
        return value_from_bits
    else:
        return value_from_bits - ((1 << category) - 1)
