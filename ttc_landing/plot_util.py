import os
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import pandas as pd
import numpy as np

from img_util import to_img

def load_log_csv(path):
    logfile = pd.read_csv(path)
    return logfile

def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def plot_distance(logfile, ax=None, hue=None):
    ax = sns.lineplot(x='Timestep', y='distance', hue=hue, data=logfile, ax=None)
    ax.set_title('Distance (t)')
    return ax

def plot_ttc(logfile, ylim=None, ax=None):
    ax = sns.lineplot(x='Timestep', y='TTC', data=logfile, ax=None)
    ax.set_title('TTC (t)')
    ax.set_ylim(ylim)
    return ax    

def plot_vel(logfile, ax=None):
    ax = sns.lineplot(x='Timestep', y='actual_velocity_y', data=logfile, ax=None)
    ax.set_title('Actual Vel y')
    return ax

def plot_desired_vel(logfile, ax=None):
    ax = sns.lineplot(x='Timestep', y='desired_velocity_y', data=logfile, ax=None)
    ax.set_title('Desired Vel y')
    return ax

def plot_derivative_animation(Exs, Eys, Ets, axes=None, output_path=None):
    if axes is None or len(axes) < 3:
        fig = plt.figure()
        plt.gray()
        axes = [fig.add_subplot(i) for i in [131, 132, 133]]
    
    imgs = []      
    for t in range(min(len(Exs), len(Eys), len(Ets))):
        for ax, imgs, ax_title in zip(axes, [Exs, Eys, Ets], ['Ex', 'Ey', 'Et']):
            ax.imshow(imgs[t])
            ax.set_title(ax_title)
            ax.set_axis_off()
        plt.draw()
        plt.pause(0.000001)
        imgs.append(to_img(fig))
    
    if output_path is not None:
        imgs[0].save(fp=output_path, format='GIF', append_images=imgs,
                            save_all=True, duration=200, loop=0) 
