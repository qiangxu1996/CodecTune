## Reproduction
- Prerequisites
  - Training and Preset Data
    - AMD EPYC 7662 with 256GB of memory
      ```
      https://www.rcac.purdue.edu/compute/bell
      ```
    - Google Youtube User Generated Content date: 2/21/2021
      ```
      https://media.withyoutube.com/
      ```
  - Fixed Workload Data
    ```
    TBD QIANG
    ```

For the process and individual dependencies required to build specific elements of this artifact refer to the repsective subfolder Readme.md files.  

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
- TBD QIANG
