import sys
import numpy as np
import matplotlib.pyplot as plt
from attrdict import AttrDict

import gym
from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel


GRAVITY = -9.81
UNITY_STEP_FREQ = 50 # hz

#### Environment parameters (NOTE: can also be set across episode as they make effect at episode start)
default_config = AttrDict({
    "mass": 1.0,
    "thrust_multiplier": 30.0,
    "action_mode": [0.0, 1.0][1], # thrust control (0.0) / velocity control (1.0)
    "dust_storm": AttrDict({ # TODO: thicker dust storm not obvious
        "enable": 0.0, # float value other than 0.0 will enable
        "start_size_multiplier": 25.0 # particle size; larger value gives thicker dust storm
    }),
    "wind_zone": AttrDict({ # NOTE: remember to set freeze_position.x/y to false when enabling wind zone
        "enable": 0.0, # float value other than 0.0 will enable
        "force": AttrDict({ # constant directional wind force over the object
            "x": 1.0, 
            "y": 0.0, # y-axis wind force should always be zero as this is up-and-down direction
            "z": 1.0,
        })
    }),
    "rigid_body": AttrDict({ 
        "freeze_position": AttrDict({ # float value other than 0.0 is true
            "x": 1.0,
            "y": 0.0, # never fix y translation as we are doing free fall
            "z": 1.0,
        }),
        "freeze_rotation": AttrDict({ # float value other than 0.0 is true
            "x": 1.0,
            "y": 1.0,
            "z": 1.0,
        })
    }),
    "cloud_shadow": AttrDict({ # TODO: cloud movement looks discrete
        "enable": 0.0, # float value other than 0.0 will enable
        "speed_multiplier": 5.0, # larger values give faster moving cloud (shadow)
        "coverage_modifier": 0.0, # -1.0 ~ 1.0, larger value gives larger coverage of shadow 
    }),
    "rotational_light": AttrDict({ # light rotates about x-axis within +-interval with fixed step size
        "enable": 1.0, # float value other than 0.0 will enable
        "interval": 10.0, # light rotate in the range of light_original_rotation +- interval
        "step": 1.0 # larger number gives faster rotating light source
    }),
    "position": AttrDict({ # starting position of the object
        "x": -120.9,
        "y": 27.4834, 
        "z": 792.7
    })
})
####

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
         # idk what obs[1][:1] is
        return ray_obs[2] * DistanceWrapper.RAY_MAX + DistanceWrapper.RAY_OFFSET

    def observation(self, obs):        
        dist_curr = self._process_ray(obs[1])
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

        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('key_press_event', key_press) 
        
        # helper
        print("Select matplotlib window. Press arrow keys to move (only up and down). \n" +
              "Don't use w/s since some keys are conflict with matplotlib default hotkey.\n" +
              "Press q to end game.")

    def reset(self):
        obs = self.env.reset()
        self.im = self.ax.imshow(obs[0])
        plt.tight_layout()
        self.fig.subplots_adjust(top=0.898)
        plt.show(block=False)
        return obs

    def step(self, a):
        # process keyboard to get action
        act = 0.0
        if self.key_ws[0]:
            act += 1.0
        elif self.key_ws[1]:
            self.act -= 1.0
        else: # No keyboard action
            act = a
        self.key_ws = np.array([False] * 2)

        obs, reward, done, info = self.env.step(act)
        img = obs[0]
        self.im.set_data(img)    
        
        # update mpl windows
        self.fig.canvas.draw()
        plt.pause(0.05)

        return obs, reward, done, info
    
def make_simple_env():
    return make_unity_env(default_config)
    
def make_unity_env(config):
    # setup environment
    if sys.platform == "win32":
        env_build = "../env/FreeFall/windows/FreeFall.exe"
    elif sys.platform == "linux":
        env_build = "../env/FlyCamera/linux/FreeFall.x86_64"
    elif sys.platform == "darwin":
        env_build = "../env/FreeFall/mac.app"
    else:
        raise AttributeError("{} platform is not supported.".format(sys.platform))
    channel = EnvironmentParametersChannel()
    unity_env = UnityEnvironment(env_build, side_channels=[channel])
    env = UnityToGymWrapper(unity_env, uint8_visual=True, allow_multiple_obs=True)
    env = DistanceWrapper(env)
    env = MatplotlibWrapper(env)
    assign_config(channel, config)

    return env

