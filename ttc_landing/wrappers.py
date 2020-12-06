import sys
import numpy as np
import matplotlib.pyplot as plt
from attrdict import AttrDict

import gym
from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel

def assign_config(_channel, _config, k_prefix=None):
    for k, v in _config.items():
        k = ".".join([k_prefix, k]) if k_prefix is not None else k
        if isinstance(v, AttrDict):    
            assign_config(_channel, v, k)
        else:
            _channel.set_float_parameter(k, v)

class DistanceWrapper(gym.ObservationWrapper):
    
    RAY_MAX = 1000
    RAY_OFFSET = -0.1446

    # raycast
    def _process_ray(self, ray_obs):
         # idk what ray_obs[:1] is
        return ray_obs[2] * DistanceWrapper.RAY_MAX + DistanceWrapper.RAY_OFFSET

    def observation(self, obs):        
        dist_curr = self._process_ray(obs[2])
        obs.append(dist_curr)
        return obs

class MatplotlibWrapper(gym.Wrapper):
    
    def __init__(self, env):
        super().__init__(env)
         
        # interface
        self.key_ws = np.array([False] * 2)

        def key_press(event): # NOTE: cannot handle multiple key press at the same time
            try:
                key = event.key.lower()
            except:
                key = event.key
            self.key_ws[0] = True if key in ['w', 'up'] else False
            self.key_ws[1] = True if key in ['s', 'down'] else False
            if key == 'q':
                self.env.close()
                sys.exit()
            sys.stdout.flush()

        self.fig, self.axes = plt.subplots(1, 2, figsize=(9,4.8))
        self.fig.canvas.mpl_connect('key_press_event', key_press)
        self._render = False 

        # helper
        print("Select matplotlib window. Press arrow keys to move (only up and down). \n" +
              "Don't use w/s since some keys are conflict with matplotlib default hotkey.\n" +
              "Press q to end game.")

    def render(self):
        self._render = True

    def reset(self):
        obs = self.env.reset()
        plt.rcParams.update({'font.size': 13, 'font.weight' : 'bold'})
        self.axes[0].set_title("UAV's View")
        self.axes[1].set_title("Third-Person View")
        for ax in self.axes:
            ax.set_xticks([])
            ax.set_yticks([])
        self.ims = [self.axes[0].imshow(obs[0]), self.axes[1].imshow(obs[1])]
        plt.tight_layout()
        self.fig.subplots_adjust(top=0.898, bottom=0.0)
        if self._render:
            plt.show(block=False)

        return obs

    def step(self, a):
        # process keyboard to get action
        act = np.zeros((6,))
        if self.key_ws[0]:
            act[1] += 1.0
        elif self.key_ws[1]:
            act[1] -= 1.0
        else: # No keyboard action
            act = a
        self.key_ws = np.array([False] * 2)

        # TODO: In velocity control, fix effect of gravity update later than taking action (otherwise -0.2 offset)

        obs, reward, done, info = self.env.step(act)
        img0 = obs[0]
        img1 = obs[1]
        self.ims[0].set_data(img0)
        self.ims[1].set_data(img1)

        return obs, reward, done, info

    def update_fig(self):
        # update mpl windows
        self.fig.canvas.draw()
        if self._render:
            plt.pause(0.05)
     
def make_unity_env(config):
    # setup environment
    if sys.platform == "win32":
        env_build = "../env/FreeFallVer2/windows/FreeFall.exe"
    elif sys.platform == "linux":
        env_build = "../env/FreeFallVer2/linux/FreeFall.x86_64"
    elif sys.platform == "darwin":
        env_build = "../env/FreeFallVer2/mac.app"
    else:
        raise AttributeError("{} platform is not supported.".format(sys.platform))
    channel = EnvironmentParametersChannel()
    unity_env = UnityEnvironment(env_build, side_channels=[channel], additional_args=["-batchmode"])
    env = UnityToGymWrapper(unity_env, uint8_visual=True, allow_multiple_obs=True)
    env = DistanceWrapper(env)
    env = MatplotlibWrapper(env)
    assign_config(channel, config)

    return env

