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
            velocity_limit=0,
            disable_control=False # For showing freefall
        ):
        self.a = a
        self.downsample_size = downsample_size
        self.default_act = default_act
        self.max_velocity = max_velocity
        self.velocity_limit = velocity_limit
        self.disable_control = disable_control
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
            try:
                T, x0, y0, Ex, Ey, Et, v = solve_ttc_multiscale(self.prev_frame, frame)
                self.recent_ttcs.append(T)
                smooth_T = np.mean(self.recent_ttcs)
            
                unclip_act = -2 * self.a * smooth_T
                act = np.clip(unclip_act, -self.max_velocity, self.velocity_limit)
                ctrl_info = {'TTC': T, 'V*': act, 'unclipped_V*': unclip_act,  
                        'x0': x0, 'y0': y0, 'A': v[0], 'B': v[1], 'C': v[2],
                        'Ex': Ex, 'Ey': Ey, 'Et': Et, 'valid': True}
                print('(ttc_ctrl={}) TTC={}, Smooth TTC={}, desired vel={}, unclipped desired vel={}'.format(not self.disable_control, T, np.mean(self.recent_ttcs), act, unclip_act))
            except:
                act = self.default_act
                ctrl_info = {'valid': False, 'TTC': np.inf}
               
            if self.disable_control: # Estimate TTC only
                act = 0 # For thrust
        else:
            act = self.default_act
            ctrl_info = {'valid': False, 'TTC': np.inf}

        self.prev_frame = frame
        
        return act, ctrl_info


