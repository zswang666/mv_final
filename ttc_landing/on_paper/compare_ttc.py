import os
import sys
sys.path.insert(0, "..")
import pickle
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
import pandas as pd

from plot_util import load_log_csv


def main():
    root_dir = "../results_ver2"
    variants = ["Basic", "Dust", "Cloudy", "Windy", "RotationalLight"]
    labels = ["Basic", "Duststorm", "Cloudy", "Windy", "Rotational Light"]
    running_window_size = 50
    time_interval = 50

    logfiles = []
    for var in variants:
        fpath = os.path.join(root_dir, var, "log.csv")
        logfiles.append(load_log_csv(fpath))

    fig, axes = plt.subplots(1, 5, figsize=(20,4), sharey=True)
    running_window_low = running_window_size // 2
    running_window_high = running_window_size - running_window_low
    for i, (logfile, label, ax) in enumerate(zip(logfiles, labels, axes)):
        ttc = logfile['TTC'].to_numpy() / time_interval
        N = len(logfile['Timestep'])
        running_mean, running_std = [], []
        for n in range(N):
            low = max(0, n-running_window_low)
            high = min(N, n+running_window_high)
            running_mean.append(np.mean(ttc[low:high]))
            running_std.append(np.std(ttc[low:high]))
        running_mean, running_std = np.array(running_mean), np.array(running_std)
        gt_ttc = logfile['distance'].to_numpy() / -logfile['actual_velocity_y'].to_numpy()
        ax.plot(logfile['Timestep'], gt_ttc, color='gray', label='Ground Truth')
        ax.plot(logfile['Timestep'], running_mean, color=sns.color_palette()[i])
        ax.fill_between(logfile['Timestep'], running_mean - running_std, running_mean + running_std, 
                        alpha=.3, color=sns.color_palette()[i])
        
        ax.set_title(label, fontsize=16)
        ax.set_xlabel("Timestep", fontsize=16)
        if i == 0:
            ax.set_ylabel("TTC", fontsize=16)
            ax.yaxis.set_label_coords(-0.12, 0.5)
            ax.legend(prop={"size": 12})
        ax.xaxis.set_label_coords(0.5, -0.12)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.set_ylim(0, 30)
    plt.tight_layout()
    fig.subplots_adjust(left=0.043)
    plt.show(block=False)
    fig.savefig(os.path.join(root_dir, "compare_ttc.pdf"))


if __name__ == "__main__":
    main()