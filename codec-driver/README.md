A wrapper that drives the x265 encoder to encode videos.

## Dependencies

- OpenCV
- oneTBB

## Build

```bash
mkdir build && cd build
cmake .. && make
```

The executable `codec_driver` is located in the `build` directory.

## Usage

To encode a video using certain preset and configuration,

```bash
codec_driver <video file> <preset> <config file>
```

where `<preset>` can be one of the presets from the x265 [documentation](https://x265.readthedocs.io/en/master/presets.html), and `<config file>` is a text file where each line contains a configuration parameter and its value. The available configurations can also be found in the [documentation](https://x265.readthedocs.io/en/master/cli.html). As an example,

```
me 3
early-skip 0
rect 1
```

Minimally, the configuration file can be an empty file.

### Benchmarking Presets

A script `preset-perf.py` is provided to benchmark the performance of different presets.

To use the script, first change the `driver_path` variable to point to the compiled codec driver, change the `timeout` variable to the longest encoding time before killing the encoder, and create an empty `config.txt` under the current directory.

After configuration, run

```bash
python preset-perf.py <video dir>
```

where `<video dir>` contains all the videos to be tested.

After successful execution, two files `fps.csv` and `ssim.csv` are saved under the current directory, containing the frame rates and SSIM values for each video and preset respectively. A value of 0 indicates encoding time longer than `timeout`.

