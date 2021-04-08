import csv
import random
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

random.seed(0)
summary = re.compile(r'encoded \d+ frames in [\d.]+s \(([\d.]+) fps\), [\d.]+ kb/s, Avg QP:[ \d.]+, SSIM Mean Y: ([\d.]+) \([ \d.]+ dB\)')
driver_path = ''

knobs = [
    ('ctu', [64, 32, 16]),
    ('min-cu-size', [32, 16, 8]),
    ('bframes', list(range(9))),  # [0, 16]
    ('b-adapt', [0, 1, 2]),
    ('rc-lookahead', list(range(41))),  # [bframes, 250]
    ('lookahead-slices', list(range(1, 17))),
    ('scenecut', list(range(11))),  # no max
    ('ref', list(range(1, 6))),  # [1, 16]
    ('limit-refs', [0, 1, 2, 3]),
    ('me', [0, 1, 2, 3]),  # [1, 6]
    ('merange', list(range(93))),  # [0, 32768]
    ('subme', list(range(6))),  # [0, 8]
    ('rect', [0, 1]),
    ('amp', [0, 1]),
    ('limit-modes', [0, 1]),
    ('max-merge', [1, 2, 3, 4, 5]),
    ('early-skip', [0, 1]),
    ('rskip', [0, 1, 2]),
    ('fast-intra', [0, 1]),
    ('b-intra', [0, 1]),
    ('sao', [0, 1]),
    ('signhide', [0, 1]),
    ('weightp', [0, 1]),
    ('weightb', [0, 1]),
    ('aq-mode', list(range(5))),
    ('cutree', [0, 1]),
    ('rd', [1, 2, 3, 4, 5]),
    ('rdoq-level', [0, 1, 2]),
    ('tu-intra-depth', [1, 2, 3, 4]),
    ('tu-inter-depth', [1, 2, 3, 4]),
    ('limit-tu', list(range(5))),
]

if __name__ == '__main__':
    vid_file = sys.argv[1]
    output_file = Path(vid_file).with_suffix('.csv').name
    with open(output_file, 'w', newline='') as csvfile, \
        TemporaryDirectory() as tmpdirname:
        writer = csv.writer(csvfile)
        header = [k for k, _ in knobs]
        header.extend(['fps', 'ssim', 'reward'])
        writer.writerow(header)

        i = 0
        while i < 300:
            config_values = [random.choice(r) for _, r in knobs]
            config_path = Path(tmpdirname, 'config.txt')
            with open(config_path, 'w', encoding='utf-8') as config_file:
                for (k, _), v in zip(knobs, config_values):
                    print(k, v, file=config_file)

            try:
                out = subprocess.run(
                    [driver_path, vid_file, str(config_path)],
                    capture_output=True, timeout=30, text=True)
            except subprocess.TimeoutExpired:
                continue

            match = summary.fullmatch(out.stderr.splitlines()[-1])
            if match:
                fps = float(match.group(1))
                ssim = float(match.group(2))
                reward = ssim
                if fps < 30:
                    reward -= (30 - fps) / 10
                config_values.extend([fps, ssim, reward])
                writer.writerow(config_values)
                i += 1
                print(i, fps, ssim)
