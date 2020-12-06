#####################################################
################                   ##################
################    NOT WORKING    ##################
################                   ##################
#####################################################
import os
import sys
sys.path.insert(0, "..")
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
import pandas as pd

from plot_util import load_log_csv


def main():
    root_dir = "../results_ver2"
    variants = ["Basic", "Dust", "Cloudy", "Windy", "RotationalLight"]
    labels = ["Basic", "Duststorm", "Cloudy", "Windy", "Rotational Light"]
    avg_window_size = 20
    dt = 1. / 50

    logfiles = []
    for var in variants:
        fpath = os.path.join(root_dir, var, "log.csv")
        logfiles.append(load_log_csv(fpath))

    fig, ax = plt.subplots()
    for logfile, label in zip(logfiles, labels):
        N = len(logfile['Timestep']) - 1
        reach_time = logfile['Timestep'][N]
        velo = logfile['actual_velocity_y'][N-avg_window_size-1:N].to_numpy()
        acc = (velo[1:] - velo[:-1]) / dt
        #acc_mean, acc_std = acc.mean(), acc.std()
        #ax.scatter(reach_time, acc_mean, s=np.sqrt(acc_std*1E5), label=label)
        velo_mean, velo_std = velo.mean(), velo.std()
        ax.scatter(reach_time, velo_mean, s=np.sqrt(velo_std*1E5), label=label)
    ax.set_xlabel("Landing Time", fontsize=16)
    ax.set_ylabel("Landing Strength", fontsize=16)
    ax.xaxis.set_label_coords(0.5, -0.12)
    ax.yaxis.set_label_coords(-0.08, 0.5)
    ax.legend(prop={"size": 14})
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.tight_layout()
    plt.show(block=False)
    import pdb; pdb.set_trace()
    


if __name__ == "__main__":
    main()