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

    logfiles = []
    for var in variants:
        fpath = os.path.join(root_dir, var, "log.csv")
        logfiles.append(load_log_csv(fpath))

    fig, ax = plt.subplots()
    for i, (logfile, label) in enumerate(zip(logfiles, labels)):
        logfile['actual_velocity_y'] *= -1
        sns.lineplot(x='Timestep', y='actual_velocity_y', data=logfile, ax=ax, label=label, zorder=len(labels)-i)
    ax.set_yscale("log")
    #ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("Timestep", fontsize=16)
    ax.set_ylabel("Vertical Velocity (log-scale)", fontsize=16)
    ax.xaxis.set_label_coords(0.5, -0.12)
    ax.yaxis.set_label_coords(-0.08, 0.5)
    ax.legend(prop={"size": 14})
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.tight_layout()
    plt.show(block=False)
    fig.savefig(os.path.join(root_dir, "compare_velocity.pdf"))


if __name__ == "__main__":
    main()