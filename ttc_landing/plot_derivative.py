import os
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import pandas as pd
import numpy as np

from plot_util import plot_derivative_animation, load_pickle

def main(args):
    Exs = load_pickle(os.path.join(args.logdir, 'Exs.npy'))
    Eys = load_pickle(os.path.join(args.logdir, 'Eys.npy'))
    Ets = load_pickle(os.path.join(args.logdir, 'Ets.npy'))
    plot_derivative_animation(Exs, Eys, Ets) 
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Plotting the results of TTC landing')
    parser.add_argument('--logdir', help='The directory that contains Exs.npy, Eys.npy, and Ets.npy')
    args = parser.parse_args()
    
    main(args)
