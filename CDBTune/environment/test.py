import numpy as np
from encoder_tune import *
import argparse
import threading
import cv2 as cv

def get_args():
    parser = argparse.ArgumentParser(description="train noise2noise model",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--video", type=str, required=True,
                            help="video")
    parser.add_argument("--width", type=int, required=True,
                            help="width")
    parser.add_argument("--height", type=int, required=True,
                            help="height")
    parser.add_argument("--fps", type=int, required=True,
                            help="fps")

    args = parser.parse_args()
    return args

def main():
    args = get_args()
    video = args.video
    width = args.width
    height = args.height
    fps = args.fps
    
    vid = cv.VideoCapture(video)
    
    encoder = Encoder(width, height, fps)
    t1 = threading.Thread(encoder.run())
    
    add_frame(encoder, vid)
    t1.join()
    cleanup()

if __name__ == '__main__':
    main()
