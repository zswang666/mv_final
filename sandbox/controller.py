from collections import deque

import numpy as np

from ttc import solve_ttc_multiscale, solve_ttc
from ttc.util import rgb2gray, uniform_blur, restrict

class TTCController(object):
    
    def __init__(self, a=0.001, 
            downsample_size=5, 
            default_act=0.0, 
            smooth_window=10,
            max_velocity=1.0,
            velocity_limit=0):
        self.a = a
        self.downsample_size = downsample_size
        self.default_act = default_act
        self.max_velocity = max_velocity
        self.velocity_limit = velocity_limit
        self.recent_ttcs = deque(maxlen=smooth_window)
        self.prev_frame = None        
    
    def _preprocess_image(self, obs):
        frame = uniform_blur(restrict(rgb2gray(obs)), self.downsample_size)
        return frame

    def reset(self):
        self.recent_ttcs.clear()
        self.prev_frame = None

    def step(self, img_obs):
        frame = self._preprocess_image(img_obs)
        if self.prev_frame is not None:            
            T, x0, y0, Ex, Ey, Et, v = solve_ttc_multiscale(self.prev_frame, frame)
            self.recent_ttcs.append(T)
            smooth_T = np.mean(self.recent_ttcs)
            act = np.clip(-2 * self.a * smooth_T, -self.max_velocity, self.velocity_limit)
            print('TTC={}, Smooth TTC={}, act={}'.format(T, np.mean(self.recent_ttcs), act))
        else:
            x0 = y0 = T = np.inf            
            act = self.default_act
        self.prev_frame = frame
        
        return act, {'TTC': T, 'V*': act, 'x0': x0, 'y0': y0}


