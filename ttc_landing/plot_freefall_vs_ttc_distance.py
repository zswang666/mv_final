import os
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import pandas as pd
import numpy as np

from plot_util import plot_distance, load_log_csv

def main(args):
    ttc_logfile = load_log_csv(args.ttc_log_path)
    freefall_logfile = load_log_csv(args.freefall_log_path)

    ttc_logfile['legend'] = 'TTC'
    freefall_logfile['legend'] = 'Freefall'

    ax = plot_distance(pd.concat([ttc_logfile, freefall_logfile]), hue='legend')
    plt.show()
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Plotting the results of TTC landing')
    parser.add_argument('--ttc-log-path', help='The path of .csv files')
    parser.add_argument('--freefall-log-path', help='The path of .csv files')
    args = parser.parse_args()
    
    main(args)
