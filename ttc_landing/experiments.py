import sys
import numpy as np
import matplotlib.pyplot as plt
from attrdict import AttrDict

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel

from wrappers import MatplotlibWrapper
from controller import TTCController

import pickle
import csv
import os

from PIL import Image
import io

def to_img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

class ExperimentLogger(object):
    def __init__(self, base_dir):
        os.makedirs(base_dir)
        self.base_dir = base_dir
        self.csv_log_path = os.path.join(self.base_dir, 'log.csv')
        self.views = []
        self.Exs = []
        self.Eys = []
        self.Ets = []

        with open(self.csv_log_path, 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')          
            writer.writerow(['Timestep', 'TTC', 'x0', 'y0', 'A', 'B', 'C', 
                    'distance', 'actual_velocity_y', 'desired_velocity_y', 'unclipped_velocity_y'])

    def log(self, timestep, TTC, x0, y0, A, B, C, distance, actual_vel_y, desired_vel_y, unclipped_velocity_y):
        with open(self.csv_log_path, 'a', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')          
            writer.writerow([timestep, TTC, x0, y0, A[0], B[0], C[0], distance, actual_vel_y, desired_vel_y, unclipped_velocity_y])

    def snapshot(self, view, Ex, Ey, Et):
        self.views.append(view)
        self.Exs.append(Ex)
        self.Eys.append(Ey)
        self.Ets.append(Et)

    def _save(self, path, obj):
        with open(os.path.join(self.base_dir, path), 'wb') as f:
            pickle.dump(obj, f)
            
    def close_and_save(self):
        self._save('views.npy', (self.views))
        self._save('Exs.npy', (self.Exs))
        self._save('Eys.npy', (self.Eys))
        self._save('Ets.npy', (self.Ets))   

def run_experiment(env, logger_kwargs={'base_dir': 'tmp'}, controller_kwargs={}):
    assert isinstance(env, MatplotlibWrapper)

    logger = ExperimentLogger(**logger_kwargs)

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
        
        if ctrl_info['valid']:
            TTC = ctrl_info['TTC']
            x0, y0 = ctrl_info['x0'], ctrl_info['y0'] # FoE
            A, B, C = ctrl_info['A'], ctrl_info['B'], ctrl_info['C'] # The coefs of BCCE
            desired_vel_y, unclipped_desired_vel_y = ctrl_info['V*'], ctrl_info['unclipped_V*'] # Velocity commands
            Ex, Ey, Et = ctrl_info['Ex'], ctrl_info['Ey'], ctrl_info['Et'] # Derivatives
            
            logger.log(timestep, TTC, x0, y0, A, B, C,
                                distance_to_ground, velocity[1], desired_vel_y, unclipped_desired_vel_y)
            logger.snapshot(to_img(fig), Ex, Ey, Et)

            if foe_marker is not None:
                foe_marker.remove()

            foe_marker = ax.annotate('X', 
                                    (x0+(n)/2, y0+(m)/2), 
                                    textcoords="offset points", 
                                    xytext=(0,0), 
                                    color='r',
                                    ha='center')
            
        
        timestep += 1

        if distance_to_ground < 0.4:
            done = True
            logger.close_and_save()
