import csv
import re
import subprocess
import sys
from pathlib import Path

presets = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow', 'placebo']
summary = re.compile(r'encoded \d+ frames in [\d.]+s \(([\d.]+) fps\), [\d.]+ kb/s, Avg QP:[ \d.]+, SSIM Mean Y: ([\d.]+) \([ \d.]+ dB\)')
driver_path = 'build/codec_driver'
timeout = 30

if __name__ == '__main__':
    with open('fps.csv', 'w', newline='') as fpsfile, \
        open('ssim.csv', 'w', newline='') as ssimfile:
        fpswriter = csv.writer(fpsfile)
        ssimwriter = csv.writer(ssimfile)
        headers = ['vid'] + presets
        fpswriter.writerow(headers)
        ssimwriter.writerow(headers)

        for vid in Path(sys.argv[1]).iterdir():
            print(vid)
            fpsrow = [vid.stem]
            ssimrow = [vid.stem]
            for p in presets:
                try:
                    out = subprocess.run(
                        [driver_path, vid, p, 'config.txt'],
                        capture_output=True, timeout=timeout, text=True)
                except subprocess.TimeoutExpired:
                    fpsrow.append(0)
                    ssimrow.append(0)
                    continue
                match = summary.fullmatch(out.stderr.splitlines()[-1])
                fpsrow.append(match.group(1))
                ssimrow.append(match.group(2))
            fpswriter.writerow(fpsrow)
            ssimwriter.writerow(ssimrow)
            fpsfile.flush()
            ssimfile.flush()
