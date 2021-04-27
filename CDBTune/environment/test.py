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
        stats = get_frame_stats()

        #Create the python dictionary with all the stats
        stats_dict = dict((key, getattr(stats, key)) for key in dir(stats) if not key.startswith('__'))

        #Optional: Just printing the dict, this is debugging 
        for k,v in stats_dict.iteritems():

            print("\t" + k + ": " + str(v))  

    return 0
    

if __name__ == '__main__':
    main()

