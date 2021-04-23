import numpy as np
from encoder_tune import *
import argparse
import threading
import cv2 as cv
import pdb
import faulthandler

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
    
    #encoder = Encoder(width, height, fps)
    #encoder_thread(encoder)
    #encoder_thread(width, height, fps, video)
    
    #add_frame(encoder, video)
    #cleanup()
    ##
    
    encoder_create(width, height, fps)
    #load_video(video)
    #pdb.set_trace()
    push_frame_thread(video)
    print("before encoder_run")
    faulthandler.enable()
    encoder_run()
    print("before get_qp")
    qp = get_qp()
    print("before cleanup")
    cleanup()
    
    print(qp, 'lets gooooooooooo')
    
    return 0
    

if __name__ == '__main__':
    main()
