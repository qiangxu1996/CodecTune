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
        self.last_external_metrics = None
        self.default_externam_metrics = None
        self.num_metric = 0
        
        self.encoder = Encoder(width, height, fps)
    
    def _get_external_metrics(self):
        
    def _get_internal_metrics(self):
        
    def eval(self, knob):
        
    def step(self, knob):
        
    def _get_state(self, knob):
        
    def _apply_knobs(self, knob):
    
    def initialize(self):
        """Initialize the encoder instance environment
        """
        pass
    
    def _apply_knobs(self, knob):
        """ Apply Knobs to the instance
        """
        pass
    
    def _get_reward(self, external_metrics):