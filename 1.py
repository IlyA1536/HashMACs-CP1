import hashlib
import random
import string
import statistics
import math
import matplotlib.pyplot as plt

NAME = 'Дорошенко Ілля Олександрович'
RUNS = 100
LETTERS = string.ascii_letters + string.digits


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def change(text):
    chars = list(text)
    for pos in random.sample(range(len(chars)), 4):
        chars[pos] = random.choice(LETTERS.replace(chars[pos], ''))
    return ''.join(chars)


def preimage(base, random_mode):
    target = sha(base)[-4:]
    i = 0
    lines = []

    while True:
        i += 1

        if random_mode:
            ending = change(base.split(' | ', 1)[1])
            message = NAME + ' | ' + ending
        else:
            message = base + str(i)

        h = sha(message)

        if i <= 30:
            lines.append((i, message, h))

        if h[-4:] == target and message != base:
            return i, base, sha(base), lines, [(i, message, h)]


def birthday(base, random_mode):
    seen = {}
    used = set()
    lines = []
    i = 0

    while True:
        if random_mode:
            ending = change(base.split(' | ', 1)[1])
            message = NAME + ' | ' + ending

            if message in used:
                continue

            used.add(message)
        else:
            message = base + str(i + 1)

        i += 1
        h = sha(message)
        short = h[-8:]

        if i <= 30:
            lines.append((i, message, h))

        if short in seen:
            return i, base, sha(base), lines, [
                seen[short], (i, message, h)
            ]

        seen[short] = (i, message, h)


attacks = [
    ('Прообраз: числа', False, preimage),
    ('Прообраз: випадкові зміни', True, preimage),
    ('Дні народження: числа', False, birthday),
    ('Дні народження: випадкові зміни', True, birthday),
]

all_counts = []

with open('results.txt', 'w', encoding='utf-8') as f:
    for title, random_mode, attack in attacks:
        print('Виконується', title, flush=True)
        counts = []

        for run in range(1, RUNS + 1):
            part = ''.join(random.choices(LETTERS, k=16))
            kind = 'preimage' if attack == preimage else 'birthday'
            base = NAME + ' | ' + kind + ' | ' + part

            count, start, start_hash, first30, found = attack(
                base, random_mode
            )
            counts.append(count)

            if run == 1:
                f.write('\n' + title + '\n')
                f.write('Початкове повідомлення: ' + start + '\n')
                f.write('SHA-256: ' + start_hash + '\n')
                f.write('Перші 30 повідомлень:\n')

                for num, message, h in first30:
                    f.write(f'{num}. {message}\n   {h}\n')

                f.write('Знайдено:\n')

                for num, message, h in found:
                    f.write(f'{num}. {message}\n   {h}\n')

                f.write(f'Кількість спроб: {count}\n')

            if run % 10 == 0:
                print(f'  {run}/{RUNS}', flush=True)

        avg = statistics.mean(counts)
        var = statistics.variance(counts)
        delta = 1.984 * math.sqrt(var / RUNS)

        f.write('\n' + title + ': статистика 100 запусків\n')

        for j, count in enumerate(counts, start=1):
            f.write(f'{j}: {count}\n')

        f.write(f'Середнє: {avg:.2f}\n')
        f.write(f'Дисперсія: {var:.2f}\n')
        f.write(
            f'95% довірчий інтервал: '
            f'[{avg-delta:.2f}; {avg+delta:.2f}]\n'
        )

        print(f'Середнє: {avg:.2f}; дисперсія: {var:.2f}')
        all_counts.append(counts)


fig, axes = plt.subplots(2, 2, figsize=(12, 8))

for ax, (title, _, _), counts in zip(
    axes.flat, attacks, all_counts
):
    ax.hist(counts, bins=15, edgecolor='black')
    ax.set_title(title)
    ax.set_xlabel('Кількість повідомлень')
    ax.set_ylabel('Кількість запусків')

plt.tight_layout()
plt.savefig('histograms.png', dpi=150)

print('Створено results.txt та histograms.png')
