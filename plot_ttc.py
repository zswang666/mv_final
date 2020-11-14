import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

sns.set_style("darkgrid")
with open('T.npy', 'rb') as f:
    Ts = np.load(f)
df = pd.DataFrame(Ts)
plt.plot(df)
plt.show()
