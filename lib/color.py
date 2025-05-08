import numpy as np

def rgb_to_ycbcr(rgb_image):
    rgb_image_float = rgb_image.astype(np.float32)

    r = rgb_image_float[:, :, 0]
    g = rgb_image_float[:, :, 1]
    b = rgb_image_float[:, :, 2]

    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.168736 * r - 0.331264 * g + 0.5 * b + 128.0
    cr = 0.5 * r - 0.418688 * g - 0.081312 * b + 128.0

    ycbcr_image = np.zeros_like(rgb_image_float)
    ycbcr_image[:, :, 0] = y
    ycbcr_image[:, :, 1] = cb
    ycbcr_image[:, :, 2] = cr

    ycbcr_image = np.clip(ycbcr_image, 0, 255)

    return ycbcr_image.astype(np.uint8)

def ycbcr_to_rgb(ycbcr_image):
    ycbcr_image_float = ycbcr_image.astype(np.float32)

    y = ycbcr_image_float[:, :, 0]
    cb = ycbcr_image_float[:, :, 1]
    cr = ycbcr_image_float[:, :, 2]

    r = y + 1.402 * (cr - 128.0)
    g = y - 0.344136 * (cb - 128.0) - 0.714136 * (cr - 128.0)
    b = y + 1.772 * (cb - 128.0)

    rgb_image = np.zeros_like(ycbcr_image_float)
    rgb_image[:, :, 0] = r
    rgb_image[:, :, 1] = g
    rgb_image[:, :, 2] = b

    rgb_image = np.clip(rgb_image, 0, 255)

    return rgb_image.astype(np.uint8)
