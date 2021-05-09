import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def ssim_to_db(ssim):
    return -10 * np.log10(1 - ssim)

if __name__ == '__main__':
    preset_root = Path(sys.argv[1])
    fps = pd.read_csv(preset_root / 'fps.csv')
    ssim = pd.read_csv(preset_root / 'ssim.csv')
    ssim_num = ssim_to_db(ssim.iloc[:, 1:])
    ssim_num[fps.iloc[:, 1:] < 30] = 0
    ssim.iloc[:, 1:] = ssim_num
    ssim.sort_values('vid', inplace=True, ignore_index=True)
    preset = ssim.max(1, numeric_only=True)

    algo_root = Path(sys.argv[2])
    def get_relative_ssim(file):
        p = pd.read_csv(algo_root / file)
        p.sort_values('vid', inplace=True, ignore_index=True)
        return ssim_to_db(p['ssim']) / preset

    rand = get_relative_ssim('top-rand.csv')
    ea = get_relative_ssim('top-ea.csv')
    actgan = get_relative_ssim('top-actgan.csv')

    idx = range(len(preset))
    plt.axhline(1, c='k', lw=.75)
    plt.scatter(idx, rand, marker='o', label='Random')
    plt.scatter(idx, ea, marker='*', label='Genetic algo')
    plt.scatter(idx, actgan, marker='x', label='ACTGAN')
    plt.legend()
    plt.xticks([])
    plt.xlabel('Videos')
    plt.ylabel('Improvement over best preset (%)')
    plt.savefig('preset-cmp.pdf')
