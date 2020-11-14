import sys
import matplotlib.pyplot as plt

mouse_position = None
def mouse_move(event):
    global mouse_position
    x, y = event.xdata, event.ydata
    mouse_position = [x, y]
    
def key_press(event):
    print(event.key)
    sys.stdout.flush()

fig, ax = plt.subplots()
fig.canvas.mpl_connect('motion_notify_event', mouse_move)
fig.canvas.mpl_connect('key_press_event', key_press)
plt.show()

print(mouse_position) # remember to place cursor in the window to get valid position
import pdb; pdb.set_trace()