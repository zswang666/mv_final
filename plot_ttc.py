import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_style("darkgrid")
with open('T.npy', 'rb') as f:
    Ts = np.load(f)
plt.plot(Ts)
plt.show()
