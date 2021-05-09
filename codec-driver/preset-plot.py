import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

presets = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow', 'placebo']

if __name__ == '__main__':
    root = Path(sys.argv[1])
    fps = pd.read_csv(root / 'fps.csv')
    ssim = pd.read_csv(root / 'ssim.csv')
    fps = fps.iloc[:, 1:].to_numpy()
    ssim = ssim.iloc[:, 1:].to_numpy()
    ssim = -10 * np.log10(1 - ssim)
    fps[fps < 30] = 0
    ssim[fps < 30] = 0

    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    for f, s in zip(fps, ssim):
        nonzero = np.count_nonzero(f)
        ax1.plot(presets[:nonzero], f[:nonzero])
        ax2.plot(presets[:nonzero], s[:nonzero])
    ax1.set_xlabel('Preset')
    ax1.set_ylabel('Encoding frame rate')
    ax2.set_xlabel('Preset')
    ax2.set_ylabel('SSIM (dB)')
    fig1.savefig('preset-fps.pdf')
    fig2.savefig('preset-ssim.pdf')
