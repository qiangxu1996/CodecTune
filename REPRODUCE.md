# Reproduction

## Dataset and Enviroment

- Training and Preset Data
  - AMD EPYC 7662 with 256GB RAM
    ```
    https://www.rcac.purdue.edu/compute/bell
    ```
  - YouTube UGC as of date: 2/21/2021
    ```
    https://media.withyoutube.com/
    ```
  
- Fixed Workload Data
  
  - Intel Xeon E5-2609 v3 with 32GB RAM
  - The following video files from YouTube UGC
  
  ```
  CoverSong-014c
  CoverSong-0239
  HowTo-017a
  HowTo-06eb
  Lecture-003a
  Lecture-07e0
  LiveMusic-0cd5
  LiveMusic-0d9f
  LyricVideo-068d
  LyricVideo-081c
  MusicVideo-0355
  MusicVideo-0752
  NewsClip-04ba
  NewsClip-0c81
  Sports-0104
  Sports-07d0
  TelevisionClip-1862
  TelevisionClip-19de
  VerticalVideo-0750
  VerticalVideo-0dac
  Vlog-033a
  Vlog-03d5
  ```

For the process and individual dependencies required to build specific elements of this artifact refer to the repsective subfolder README.md files.  

## Reproducing Preset Data
- Modify CDBTune/environment/encoder_tune.cpp line 41 with the target preset e.g. "ultrafast" or "slower"
  - This step must be repeated for each preset data to be generated
- Build encoder_tune.cpp as directed in the respective Readme.md
- Modify paths as appropriate in CDBTune/environment/driver.py
  - If running on a slurm based HPC system, modify paths as appropriate in CDBTune/codecDriverSlurmScript

## Reproducing Training Data
- CDBTune/Readme.md has steps for running train.py in CDBTune/evironment/tuner/
  - If running on a slurm based HPC system, modify paths as appropriate in CDBTune/trainingSlurmScript

## Reproducing Fixed Workload Data
- For the preset performances, run codec-tuner/preset-perf.py by following codec-driver/README.md
- For the three configuration tuning algorithms, run fixed-workload/tuner.py according to fixed-workload/README.md

