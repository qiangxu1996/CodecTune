import numpy as np
import knobs
from encoder_tune import *
import os
import knobs
import pdb

BEST_NOW = ""
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOB_DETAILS = knobs.init_knobs()

class MyEncoder(object):
    def __init__(self, video, width, height, fps, num_metric=42):
        self.video = video
        self.width = width
        self.height = height
        self.fps = fps
        
        self.steps = 0
        self.score = 0.0
        self.terminate = False
        self.last_external_metrics = []
        self.default_externam_metrics = None
        self.num_metric = num_metric

        knobs.init_knobs(num_more_knobs=0)
        self.default_knobs = knobs.get_init_knobs()
        
        #create an x265 encoder
        encoder_create(self.width, self.height, self.fps)
        #load the picture queue with frames in it's own thread
        # push_frame_thread(self.video)
        
        # create a new thread to push frames
        # c++ main w/o l116
        
    
    def _encode_complete(self):
        return is_encode_done()

    def _get_external_metrics(self):
        pass
        #NO?
        # encoder 
        # run() (operator()())
        # extract statistics

    def _get_internal_metrics(self):

        #Do the Encode
        encode_fps = float(encoder_run())
        stats = get_frame_stats()
        
        #get the frame Stats
        stats_dict = dict((key, getattr(stats, key)) \
        for key in dir(stats) if not key.startswith('__')) #ignore default python attributes
        
        return stats_dict, encode_fps

        
    def eval(self, knob):
        flag = self._apply_knobs(knob)
        if flag != 0:
            return {"ssim": 0.0, "encode_fps": 0.0}

        ssim , encode_fps = self._get_state(self)
        
        return {"ssim": ssim,
                "encode_fps": encode_fps}
        
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
        restart_time = 123 # random value
        filename = 'bestnow.log'
        flag = self._apply_knobs(knob)
        if flag != 0:
            return -10000000.0, np.array([0] * self.num_metric), True, self.score - 10000000, [0, 0, 0], restart_time
        s = self._get_state()
        if s is None:
            return -10000000.0, np.array([0] * self.num_metric), True, self.score - 10000000, [0, 0, 0], restart_time
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
        self.terminate = self._encode_complete()
        terminate = self._terminate()
        knobs.save_knobs(
            knob=knob,
            metrics=external_metrics,
            knob_file='%s/tuner/save_knobs/knob_metric.txt' % PROJECT_DIR
        )
        
        return reward, next_state, terminate, self.score, external_metrics, restart_time
    
    def set_video(video):
        self.video = video
       
    def _get_state(self):
        #ssim is both external and internal - encode fps is only external     
        internal_metrics, encode_fps = self._get_internal_metrics() #calls encoder
        external_metrics = [internal_metrics['ssim'], encode_fps]
        
        # turn internal_metrics into a list of values
        #pdb.set_trace()
        keys = internal_metrics.keys()
        keys.sort()
        
        result = np.zeros(self.num_metric)
        for idx in xrange(len(keys)):
            key = keys[idx]
            data = internal_metrics[key]
            result[idx] = data
            
        return external_metrics, result
        
        
    def _apply_knobs(self, knob):
        """ Apply Knobs to the instance
        """
        #Yiming <"thread_pools","32">
        knob_list = []
        for k, v in knob.items():
            kv = (k, str(v))
            knob_list.append(kv)
        return encoder_config(knob_list)
        
    
    def initialize(self):
        """Initialize the encoder instance environment
        """
        self.score = 0.0
        self.steps = 0
        self.terminate = False
        self.last_external_metrics = []
        push_frame_thread(self.video)
        flag = self._apply_knobs(self.default_knobs)
        i = 0
        while not flag:
            flag = self._apply_knobs(self.default_knobs)
            i += 1
            if i >= 5:
                print("Initialize: {} times ....".format(i))


        '''
        def_knobs = {}

        
        
        for item in KNOB_DETAILS:
            flag = self._apply_knobs([(str(item),str(KNOB_DETAILS[item][1][2]))])
            def_knobs[str(item)] = str(KNOB_DETAILS[item][1][2])
            if flag != 0:
                print("Knob Application of knob " + str(item) + " with value " +str(KNOB_DETAILS[item][1][2]) + " resulted in error " + str(flag) + " in my encoder initialize")
       ''' 
        external_metrics, internal_metrics = self._get_state()
        state = internal_metrics
        self.default_externam_metrics = external_metrics
        self.last_external_metrics = external_metrics
        
        knobs.save_knobs(
            self.default_knobs,
            metrics=external_metrics,
            knob_file='%s/tuner/save_knobs/knob_metric.txt' % PROJECT_DIR
        )
        
        return state, external_metrics
    
    
    def _get_reward(self, external_metrics):
        target_fps = 30
        reward = external_metrics[0]
        if external_metrics[1] < target_fps:
           reward -= (target_fps - external_metrics[1]) / 10
        self.score += reward
        return reward

    
    def _terminate(self):
        return self.terminate
        
