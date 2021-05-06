This directory provides tuning algorithms for tuning the encoding performance for a fixed workload, i.e., a certain video.

## Setup

The scripts depend on Python packages [DEAP](https://deap.readthedocs.io/en/master/) and [pandas](https://pandas.pydata.org/). The ACTGAN algorithm additionally depends on [TensorFlow](https://www.tensorflow.org/) 1.x.

Before using `tuner.py`, set the variable `driver_path` to the compiled codec driver and select a suitable `timeout` (see `codec_driver/README.md` for more information).

## Usage

Three algorithms (random, genetic algorithm, and ACTGAN) are provided. For the first two algorithms,

```bash
python tuner.py {rand|ea} <video file>
```

runs the selected algorithm. A CSV file with the same name as the video file will be saved under the current directory, containing all the configurations tried and the corresponding performance results.

The third algorithm ACTGAN depends on the outputs of random. To run ACTGAN, change into the `ACTGAN` directory,

```bash
python normalGAN.py <random result file>
python dataout.py <random result file>-out.csv
python ../tuner.py feed <video file> <random result file>-out-clean.csv
```

and a CSV file with the same name as the video will be saved under the current directory, containing the performance results of the configurations recommended by ACTGAN.

The script `top-config.py` is provided to extract the best configurations of a certain algorithm for multiple videos. Put the CSV files for the same algorithm into a separate directory, then

```bash
python top-config.py <csv directory> <output csv>
```

will produce an output CSV file containing the best configuration and performance values for each video.

## Ackownledgement

Code in the ACTGAN directory are adapted from the [ACTGAN](https://github.com/anon4review/ACTGAN/tree/master/code/ACTGAN) project.

