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

    fig, ax = plt.subplots()
    for logfile, label in zip(logfiles, labels):
        sns.lineplot(x='Timestep', y='distance', data=logfile, ax=ax, label=label)
    ax.set_xlabel("Timestep", fontsize=16)
    ax.set_ylabel("Distance", fontsize=16)
    ax.xaxis.set_label_coords(0.5, -0.12)
    ax.yaxis.set_label_coords(-0.08, 0.5)
    ax.legend(prop={"size": 14})
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.tight_layout()
    plt.show(block=False)
    fig.savefig(os.path.join(root_dir, "compare_distance.pdf"))


if __name__ == "__main__":
    main()