import numpy as np
from encoder_tune import *
import os
import knobs

BEST_NOW = ""

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
        
        
    def _get_best_now(self, filename):
        with open(BEST_NOW  + filename) as f:
            lines = f.readlines()
        best_now = lines[0].split(',')
        return [float(best_now[0]), float(best_now[1])]
    
    
    def record_best(self, external_metrics):
        filename = 'bestnow.log'
        best_flag = False
        if os.path.exists( BEST_NOW  + filename):
            ssim_best = external_metrics[0]
            fps_best = external_metrics[1]

            with open(BEST_NOW  + filename) as f:
                lines = f.readlines()
            best_now = lines[0].split(',')
            ssim_best_now = float(best_now[0])
            fps_best_now = float(best_now[1])
            if ssim_best > ssim_best_now or fps_best > fps_best_now:
                best_flag = True
                with open(BEST_NOW  + filename, 'w') as f:
                    f.write(str(ssim_best) + ',' + str(fps_best))
        else:
            file = open(BEST_NOW  + filename, 'wr')
            ssim_best = external_metrics[0]
            fps_best = external_metrics[1]

            file.write(str(ssim_best) + ',' + str(fps_best))
        return best_flag
        
        
    def step(self, knob):
        #apply_knobs
        #Yiming?
        filename = 'bestnow.log'
        flag = self._apply_knobs(knob)
        if not flag:
            return -10000000.0, np.array([0] * self.num_metric), True, self.score - 10000000, [0, 0, 0]
        s = self._get_state(knob)
        if s is None:
            return -10000000.0, np.array([0] * self.num_metric), True, self.score - 10000000, [0, 0, 0]
        external_metrics, internal_metrics = s
        
        reward = self._get_reward(external_metrics)
        flag = self.record_best(external_metrics)
        if flag == True:
            print('Better performance changed!')
        else:
            print('Performance remained!')
        
        best_now_performance = self._get_best_now(filename)
        self.last_external_metrics = best_now_performance
        
        next_state = internal_metrics
        terminate = self._terminate()
        knobs.save_knobs(
            knob=knob,
            metrics=external_metrics,
            knob_file='knob_metric.txt'
        )
        return reward, next_state, terminate, self.score, external_metrics
        
        
    def _get_state(self, knob):
        #get_internal_metrics
        #Eduardo
        
        
    def _apply_knobs(self, knob):
        """ Apply Knobs to the instance
        """
        #Yiming <"thread_pools","32">
        return config(knob)
        
        
    
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
        
        
        