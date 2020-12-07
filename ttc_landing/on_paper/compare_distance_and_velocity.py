import os
import sys
sys.path.insert(0, "..")
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import pandas as pd

from plot_util import load_log_csv


def main():
    root_dir = "../results_ver2"
    variants = ["Basic", "Dust", "Cloudy", "Windy", "RotationalLight"]
    labels = ["Basic", "Duststorm", "Cloudy", "Windy", "Rotational Light"]

    logfiles = []
    for var in variants:
        fpath = os.path.join(root_dir, var, "log.csv")
        logfiles.append(load_log_csv(fpath))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for i, (logfile, label) in enumerate(zip(logfiles, labels)):
        for j, ax in enumerate(axes):
            if j == 0:
                sns.lineplot(x='Timestep', y='distance', data=logfile, ax=ax, label=label)
            else:
                logfile['actual_velocity_y'] *= -1
                sns.lineplot(x='Timestep', y='actual_velocity_y', data=logfile, ax=ax, label=label, zorder=len(labels)-i)
    for i, ax in enumerate(axes):
        if i == 0:
            ax.set_ylabel("Distance", fontsize=16)
            ax.set_xlabel("Timestep", fontsize=16)
            ax.legend(prop={"size": 14})
            ax.yaxis.set_label_coords(-0.08, 0.5)
        else:
            ax.set_yscale("log")
            ax.set_xlabel("Timestep", fontsize=16)
            ax.set_ylabel("Vertical Velocity (log-scale)", fontsize=16)
            ax.yaxis.set_label_coords(-0.12, 0.5)
            ax.get_legend().remove()
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.xaxis.set_label_coords(0.5, -0.12)
    plt.tight_layout()
    plt.show(block=False)
    fig.savefig(os.path.join(root_dir, "compare_distance_and_velocity.pdf"))


if __name__ == "__main__":
    main()