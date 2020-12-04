import os
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import pandas as pd
import numpy as np

from plot_util import plot_distance, load_log_csv

def main(args):
    logfile = load_log_csv(args.log_path)
    ax = plot_distance(logfile)
    plt.show()
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Plotting the results of TTC landing')
    parser.add_argument('--log-path', help='The path of .csv files')
    args = parser.parse_args()
    
    main(args)
