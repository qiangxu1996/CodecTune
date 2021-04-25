#import numpy as np
from encoder_tune import *
import argparse
import threading
#import cv2 as cv
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
    #faulthandler.enable()
    # total_time = float(encoder_run())
    # qp = float(get_qp())
    # print("total_time 1", total_time)
    # print("get_qp 1", qp)
    # total_time = float(encoder_run())
    # qp = float(get_qp())
    # print("total_time 2", total_time)
    # print("get_qp 2", qp)
    #cleanup() #DEBUG
    
    while(is_encode_done() == False):
        total_time = float(encoder_run())
        print(get_frame_stats())
        stats = get_frame_stats()
        #print(stats.__dict__)
        print("Segment SSIM is: ",stats.ssim)
        qp = float(get_qp())
        print("Segement FPS is: ", total_time)
        print("Segement QP is: ", qp)
    
    #print(qp, 'lets gooooooooooo')
    #print(total_time, '  this is total time') 
    
    return 0
    

if __name__ == '__main__':
    main()
