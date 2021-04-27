import numpy as np
from encoder_tune import *

class MyEncoder(object):
    def __init__(self, video, width, height, fps):
        self.video = video
        self.width = width
        self.height = height
        self.fps = fps
        
        self.steps = 0
        self.score = 0.0
        self.terminate = False
        self.last_external_metrics = []
        self.default_externam_metrics = None
        self.num_metric = 0
        
        #create an x265 encoder
        encoder_create(width, height, fps)
        #load the picture queue with frames in it's own thread
        push_frame_thread(video)
        
        # create a new thread to push frames
        # c++ main w/o l116
        
    
    def _encode_complete(self):
        return is_encode_done()
    
    def _get_external_metrics(self):
        #NO?
        # encoder 
        # run() (operator()())
        # extract statistics
        
    def _get_internal_metrics(self):
        #Eduardo
        #Do the Encode
        #get the frame Stats {ssim,encode_fps}
        #stats_dict = dict((key, getattr(stats, key)) for key in dir(stats) if not key.startswith('__'))
        
    def eval(self, knob):
        #Kenneth
        #report the results?
        #{ssim,encode_fps}
        
        
        
    def step(self, knob):
        #apply_knobs
        #Yiming?
        
        
        
    def _get_state(self, knob):
        #get_internal_metrics
        #Eduardo
        
        
    def _apply_knobs(self, knob):
        """ Apply Knobs to the instance
        """
        #Yiming <"thread_pools","32">
        self.encoder.config(knob)
    
    def initialize(self):
        """Initialize the encoder instance environment
        """
        #Kenneth
        #apply_knobs
        pass
    
    
    def _get_reward(self, external_metrics):
        #Qiang
        #reward = ssim
        #if encode_fps < Evaluator.TARGET_FPS:
           #reward -= Evaluator.FPS_FACTOR * (Evaluator.TARGET_FPS - encode_fps
        pass
        
        
        