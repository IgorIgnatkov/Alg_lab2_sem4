from PIL import Image
import random


def generate_large_image(output_path="image_2048_2048_sizes.png", pattern='solid', color=(255, 255, 255)):
    img = Image.new('RGB', (2048, 2048))

    if pattern == 'solid':
        for x in range(img.width):
            for y in range(img.height):
                img.putpixel((x, y), color)

    elif pattern == 'gradient':
        for x in range(img.width):
            gradient = int((x / img.width) * 255)
            for y in range(img.height):
                img.putpixel((x, y), (gradient, gradient, gradient))

    elif pattern == 'noise':
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                pixels[x, y] = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )

    img.save(output_path, format='PNG', compress_level=6)
    print(f"Изображение сохранено как: {output_path}")


generate_large_image(pattern="gradient")
