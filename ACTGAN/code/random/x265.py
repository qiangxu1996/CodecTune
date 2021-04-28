import csv
import random
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from deap import algorithms, base, creator, tools

random.seed(0)
summary = re.compile(r'encoded \d+ frames in [\d.]+s \(([\d.]+) fps\), [\d.]+ kb/s, Avg QP:[ \d.]+, SSIM Mean Y: ([\d.]+) \([ \d.]+ dB\)')
driver_path = ''

knobs = [
    ('ctu', [1, 2, 4]),  # [64, 32, 16]
    ('min-cu-size', [1, 2, 4]),  # [32, 16, 8]
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

def individual(t=list):
    return t(random.choice(r) for _, r in knobs)


class Evaluator:
    TARGET_FPS = 30
    FPS_FACTOR = .1
    REWARD_MIN = -FPS_FACTOR * TARGET_FPS

    def __init__(self, vid_file):
        self.vid_file = vid_file

        output_file = Path(vid_file).with_suffix('.csv').name
        self.csvfile = open(output_file, 'w', newline='')
        self.writer = csv.writer(self.csvfile)
        header = [k for k, _ in knobs]
        header.extend(['fps', 'ssim', 'reward'])
        self.writer.writerow(header)
    
    def __call__(self, config_values):
        config_values = config_values[:]
        config_values[0] *= 16
        config_values[1] *= 8

        reward = Evaluator.REWARD_MIN
        with TemporaryDirectory() as tmpdirname:
            config_path = Path(tmpdirname, 'config.txt')
            with open(config_path, 'w', encoding='utf-8') as config_file:
                for (k, _), v in zip(knobs, config_values):
                    print(k, v, file=config_file)

            try:
                out = subprocess.run(
                    [driver_path, self.vid_file, str(config_path)],
                    capture_output=True, timeout=30, text=True)
            except subprocess.TimeoutExpired:
                return reward,

            match = summary.fullmatch(out.stderr.splitlines()[-1])
            if match:
                fps = float(match.group(1))
                ssim = float(match.group(2))
                reward = ssim
                if fps < Evaluator.TARGET_FPS:
                    reward -= Evaluator.FPS_FACTOR * (Evaluator.TARGET_FPS - fps)
                config_values.extend([fps, ssim, reward])
                self.writer.writerow(config_values)
                self.csvfile.flush()
                print(fps, ssim, reward)

        return reward,


def rand(eval):
    i = 0
    while i < 300:
        config_values = individual()
        reward = eval(config_values)[0]
        if reward > Evaluator.REWARD_MIN:
            i += 1

def ea(eval):
    pop_size = 30
    creator.create('FitnessMax', base.Fitness, weights=(1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMax)
    pop = [individual(creator.Individual) for _ in range(pop_size)]

    toolbox = base.Toolbox()
    toolbox.register('mate', tools.cxUniform, indpb=.1)
    low = [r[0] for _, r in knobs]
    up = [r[-1] for _, r in knobs]
    toolbox.register('mutate', tools.mutUniformInt, low=low, up=up, indpb=.1)
    toolbox.register('select', tools.selTournament, tournsize=3)
    toolbox.register('evaluate', eval)

    algorithms.eaMuPlusLambda(pop, toolbox, pop_size, 30, .2, .5, 25)

if __name__ == '__main__':
    eval = Evaluator(sys.argv[1])
    ea(eval)
