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
    variants = ["Basic", "Oracle"]
    labels = ["Estimated TTC Control", "Oracle TTC Control"]

    logfiles = []
    for var in variants:
        fpath = os.path.join(root_dir, var, "log.csv")
        logfiles.append(load_log_csv(fpath))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for logfile, label in zip(logfiles, labels):
        for i, ax in enumerate(axes):
            ax.set_xlabel("Timestep", fontsize=16)
            if i == 0:
                sns.lineplot(x='Timestep', y='distance', data=logfile, ax=ax, label=label)
                ax.set_ylabel("Distance", fontsize=16)
                ax.yaxis.set_label_coords(-0.08, 0.5)
            else:
                logfile['actual_velocity_y'] *= -1
                sns.lineplot(x='Timestep', y='actual_velocity_y', data=logfile, ax=ax, label=label)
                ax.set_ylabel("Vertical Velocity", fontsize=16)
                ax.set_ylim(0, 2)
                ax.yaxis.set_label_coords(-0.12, 0.5)
            ax.xaxis.set_label_coords(0.5, -0.12)
            ax.legend(prop={"size": 14})
            ax.tick_params(axis='both', which='major', labelsize=12)
    plt.tight_layout()
    fig.subplots_adjust(left=0.057, wspace=0.193)
    plt.show(block=False)
    fig.savefig(os.path.join(root_dir, "compare_oracle.png"))


if __name__ == "__main__":
    main()