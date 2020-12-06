import os
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import pandas as pd
import numpy as np

from plot_util import plot_derivative_animation, load_log_csv, load_pickle
from plot_util import plot_distance, plot_vel, plot_ttc, plot_desired_vel

def main(args):
    Exs = load_pickle(os.path.join(args.logdir, 'Exs.npy'))
    Eys = load_pickle(os.path.join(args.logdir, 'Eys.npy'))
    Ets = load_pickle(os.path.join(args.logdir, 'Ets.npy'))
    logfile = load_log_csv(os.path.join(args.logdir, 'log.csv'))

    # Plot distance
    fig_distance, ax_distance = plt.subplots()
    plot_distance(logfile, ax=ax_distance)
    fig_distance.savefig(os.path.join(args.logdir, 'distance.jpg'))

    # Plot velocity
    fig_vel, ax_vel = plt.subplots()
    plot_vel(logfile, ax=ax_vel)
    fig_vel.savefig(os.path.join(args.logdir, 'actual_vel.jpg'))
    
    # Plot desired velocity
    fig_desired_vel, ax_desired_vel = plt.subplots()
    plot_desired_vel(logfile, ax=ax_desired_vel)
    fig_desired_vel.savefig(os.path.join(args.logdir, 'actual_desired_vel.jpg'))

    # Plot ttc
    fig_ttc, ax_ttc = plt.subplots()
    plot_ttc(logfile, ax=ax_ttc, ylim=(0, 1000))
    fig_ttc.savefig(os.path.join(args.logdir, 'ttc.jpg'))

    # Plot derivatives
    if args.derivative_gif:
        plot_derivative_animation(Exs, Eys, Ets, output_path=os.path.join(args.logdir, 'derivatives.gif')) 
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Plotting the results of TTC landing')
    parser.add_argument('--logdir', help='The directory that contains Exs.npy, Eys.npy, and Ets.npy')
    parser.add_argument('--derivative-gif', help='Whether or not store gif (time consuming)', action='store_true', default=False)
    args = parser.parse_args()
    
    main(args)
