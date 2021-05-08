## Dependencies

- C++
   - OpenCV


   ```OpenCV
   apt-get install libopencv-dev
   ```
   
   - oneTBB


   ```TBB
   git clone https://github.com/wjakob/tbb.git
   cd tbb/build
   cmake ..
   make -j
   sudo make install
   ```
 
- Python 2.7.17
   - numpy
   - cv2
   - argparse


## Build

- Build x265 Encoder
   Follow x265_git (https://bitbucket.org/multicoreware/x265_git/wiki/Home) instructions to build x265 encoder. Afterwards, 
   
   ```x265
   make install
   ```
   
   for linux system. 
- Build encoder_tune.cpp
   - In `CodecTune/CDBTune/environment`,
   
      ```mkdir
      mkdir build
      cmake .. && make
      ```
      
   - Copy `encoder_tune.so` and replace it in `environment`

## Train

- In `CodecTune/CDBTune/tuner`
- Run `train.py`. Example:

   ```train
   python train.py --input [video path/video.mkv] --width 1920 --height 1080 --fps 30
   ```

## Acknowledgement
The DDPG reinforcement learning network presented here is directly inherited from CDBTune. The knobs.py mysql.py and train.py were modified accordingly to the x265 encoder environment so that the RL network training can apply to encoder configuration optimization. 

