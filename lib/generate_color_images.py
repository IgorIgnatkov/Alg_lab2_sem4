from PIL.Image import Image


def generate_color_images():
    base_images = [
        ('Lenna.png', 'lenna_color'),
        ('image_2048_2048_sizes.png', 'image_2048_2048_sizes_color')
    ]

    for src_name, prefix in base_images:
        color_path = f'photos/{prefix}.png'
        color_img = Image.open(src_name).convert('RGB')
        color_img.save(color_path)

        gray_img = image_to_grayscale(color_img)
        gray_img.save(f'photos/{prefix}_gray.png')

        dithered_img = image_to_dithered(color_img)
        dithered_img.save(f'photos/{prefix}_dithered.png')


def image_to_grayscale(img):
    return img.convert('L')


def image_to_dithered(img):
    return img.convert('1')
