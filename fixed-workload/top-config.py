import sys
from pathlib import Path

import pandas as pd

if __name__ == '__main__':
    tops = pd.DataFrame()
    for res in Path(sys.argv[1]).iterdir():
        data = pd.read_csv(res)
        idx = data['reward'].argmax()
        top = data.iloc[[idx]].copy()
        top.insert(0, 'vid', res.stem)
        tops = tops.append(top)
    tops.to_csv(sys.argv[2], index=False)
