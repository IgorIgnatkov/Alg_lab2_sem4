import os
from lib.compressor import compress_image
from lib.decompressor import decompress_image
from lib.generate_graph import plot_size_vs_quality


def main():
    quality_levels = [0, 20, 40, 60, 80, 100]
    test_photos = [
        ('photos/lenna_color.png', 'Lenna_color'),
        ('photos/lenna_color_gray.png', 'Lenna_gray'),
        ('photos/lenna_color_dithered.png', 'Lenna_dithered'),
        ('photos/image_2048_2048_sizes_color.png', 'image_2048_2048_sizes_color'),
        ('photos/image_2048_2048_sizes_color_gray.png', 'image_2048_2048_sizes_gray'),
        ('photos/image_2048_2048_sizes_color_dithered.png', 'image_2048_2048_sizes_dithered')
    ]

    results = {}

    for img_path, label in test_photos:
        results[label] = {}
        for q in quality_levels:
            actual_quality = q if q > 0 else 1
            cmp_path = f'output_photos/{label}/{label}_q{actual_quality}.myjpeg'
            decmp_path = f'output_photos/{label}/{label}_q{actual_quality}_decompressed.png'

            compress_image(img_path, cmp_path, quality=actual_quality)
            decompress_image(cmp_path, decmp_path)

            results[label][q] = os.path.getsize(cmp_path)

    plot_size_vs_quality(results, 'graph.png')


if __name__ == '__main__':
    main()
