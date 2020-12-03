import sys
import numpy as np
import matplotlib.pyplot as plt
from attrdict import AttrDict

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel

from wrappers import make_simple_env, MatplotlibWrapper

from ttc import solve_ttc_multiscale, solve_ttc
from ttc.util import rgb2gray, uniform_blur, restrict

from collections import deque

class TTCController(object):
    
    def __init__(self, a=0.001, 
            downsample_size=5, 
            default_act=0.0, 
            smooth_window=10,
            max_velocity=1.0):
        self.a = a
        self.downsample_size = downsample_size
        self.default_act = default_act
        self.max_velocity = max_velocity
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
            act = np.clip(-2 * self.a * smooth_T, -self.max_velocity, 0)
            print('TTC={}, Smooth TTC={}, act={}'.format(T, np.mean(self.recent_ttcs), act))
        else:
            T = np.inf
            act = self.default_act
        self.prev_frame = frame
        
        return act, {'TTC': T}

env = make_simple_env()

assert isinstance(env, MatplotlibWrapper)

fig, ax = env.fig, env.ax 

obs = env.reset()

img_h, img_w = obs[0].shape[:2]

done = False
timestep = 0
velocity = np.zeros((3,))

controller = TTCController()

while not done:
    act, ctrl_info = controller.step(obs[0])
    obs, _, _, _ = env.step(act)
    
    # For logging
    velocity = obs[1][3:]
    distance_to_ground = obs[-1]
    ax.set_title("Velocity = ({:.2f}, {:.2f}, {:.2f})\n Distance to Ground: {:.8f} TTC = {:.3f}".format(\
        *velocity, distance_to_ground, ctrl_info['TTC']))
    
    timestep += 1

    if distance_to_ground < 1.0:
        obs = env.reset()
