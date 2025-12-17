import sys
import os
from collections import defaultdict

SYMBOLS = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,!?')

CHUNK_SIZE = 8192


def process_general(input_file: str, output_dir: str) -> None:
    """Порядок 0: частоты символов без учёта контекста."""
    char_counts = defaultdict(int)

    with open(input_file, 'r', encoding='utf-8', buffering=CHUNK_SIZE) as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(0)

        buffer = ''
        total_chars = 0

        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            buffer += chunk.lower()

            i = 0
            while i < len(buffer):
                ch = buffer[i]
                if ch in SYMBOLS:
                    char_counts[ch] += 1
                    total_chars += 1
                i += 1

            buffer = buffer[i:]

            progress = (f.tell() / file_size) * 100 if file_size else 100
            print(f"\rorder 0: {progress:.1f}%", end='')

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "order_0.csv")
    print("\nSaving order 0...")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('order,context,symbol,probability\n')
        for ch, count in char_counts.items():
            prob = count / total_chars if total_chars else 0.0
            f.write(f'0,"","{ch}",{prob:.10f}\n')


def process_order(input_file: str, output_dir: str, order: int) -> None:
    """Порядок N: частоты символов после N предыдущих."""
    context_counts = defaultdict(lambda: defaultdict(int))

    with open(input_file, 'r', encoding='utf-8', buffering=CHUNK_SIZE) as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(0)

        buffer = ''
        context = ''

        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            buffer += chunk.lower()

            i = 0
            while i < len(buffer):
                ch = buffer[i]
                if ch in SYMBOLS:
                    if len(context) == order:
                        # есть полный контекст — считаем переход
                        context_counts[context][ch] += 1
                        context = context[1:] + ch
                    else:
                        # достраиваем контекст
                        context += ch
                else:
                    # встретили неразрешённый символ — сбрасываем контекст
                    context = ''
                i += 1

            buffer = buffer[i:]

            progress = (f.tell() / file_size) * 100 if file_size else 100
            print(f"\rorder {order}: {progress:.1f}%", end='')

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"order_{order}.csv")
    print(f"\nSaving order {order}...")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('order,context,symbol,probability\n')
        for ctx, char_counts in context_counts.items():
            total = sum(char_counts.values())
            if not total:
                continue
            for ch, count in char_counts.items():
                prob = count / total
                f.write(f'{order},"{ctx}","{ch}",{prob:.10f}\n')

    context_counts.clear()


def main():
    if len(sys.argv) != 3:
        print(f"usage: python {sys.argv[0]} <input_file> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    # порядок 0
    process_general(input_file, output_dir)

    # порядки 1..13, каждый в своём файле
    max_order = 13
    for order in range(1, max_order + 1):
        process_order(input_file, output_dir, order)


if __name__ == "__main__":
    main()
