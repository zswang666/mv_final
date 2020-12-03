import sys
import numpy as np
import matplotlib.pyplot as plt
from attrdict import AttrDict

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel

from wrappers import MatplotlibWrapper
from controller import TTCController

def run_experiment(env, controller_kwargs={}):
    assert isinstance(env, MatplotlibWrapper)

    fig, ax = env.fig, env.ax 

    obs = env.reset()

    m, n = obs[0].shape[:2]

    done = False
    timestep = 0
    velocity = np.zeros((3,))


    foe_marker = None
    controller = TTCController(**controller_kwargs)

    while not done:
        act, ctrl_info = controller.step(obs[0])
        obs, _, _, _ = env.step(act)
        
        # For logging
        velocity = obs[1][3:]
        distance_to_ground = obs[-1]
        ax.set_title("Velocity = ({:.2f}, {:.2f}, {:.2f})\n Distance to Ground: {:.8f} TTC = {:.3f}".format(\
            *velocity, distance_to_ground, ctrl_info['TTC']))
        
        if ctrl_info['TTC'] < np.inf:
            if foe_marker is not None:
                foe_marker.remove()
            x0, y0 = ctrl_info['x0'], ctrl_info['y0']    
            foe_marker = ax.annotate('X', 
                                    (x0+(n)/2, y0+(m)/2), 
                                    textcoords="offset points", 
                                    xytext=(0,0), 
                                    color='r',
                                    ha='center') 
        
        timestep += 1

        if distance_to_ground < 1.0:
            obs = env.reset()
