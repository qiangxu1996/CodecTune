#import numpy as np
from encoder_tune import *
import argparse
import threading
#import cv2 as cv
import pdb
#import faulthandler

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
    
    count=0
    while(is_encode_done() == False):
      fps = float(encoder_run())
      stats = get_frame_stats()
       #Create the python dictionary with all the stats
      stats_dict = dict((key, getattr(stats, key)) for key in dir(stats) if not key.startswith('__'))
      print("Segment " + str(count) + " of video " + str(video) + " had metrics FPS: " + str(fps) + " and SSIM: " + str(stats_dict['ssim']))
      #Optional: Just printing the dict, this is debugging 
      #for k,v in stats_dict.iteritems():
      #    print("\t" + k + ": " + str(v))         
      count = count + 1


    return 0
    

if __name__ == '__main__':
    main()

