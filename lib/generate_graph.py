import matplotlib.pyplot as plt

def plot_size_vs_quality(data, output_path):
    plt.figure(figsize=(10, 6))
    for img_label, sizes in data.items():
        quals = sorted(sizes.keys())
        bytesizes = [sizes[q] for q in quals]
        plt.plot(quals, bytesizes, label=img_label)

    plt.xlabel('Качество сжатия')
    plt.ylabel('Размер файла')
    plt.title('Размер файла и качество сжатия')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()
