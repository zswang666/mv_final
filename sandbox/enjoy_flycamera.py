import sys
import numpy as np
import matplotlib.pyplot as plt

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel


# setup environment
if sys.platform == 'win32':
    env_build = "../env/FlyCamera/windows/FlyCamera.exe"
elif sys.platform == 'linux':
    env_build = "../env/FlyCamera/linux/FlyCamera.x86_64"
elif sys.platform == "darwin":
    env_build = "../env/FlyCamera/mac.app"
else:
    raise AttributeError("{} platform is not supported.".format(sys.platform))
channel = EnvironmentParametersChannel()
unity_env = UnityEnvironment(env_build, side_channels=[channel])
channel.set_float_parameter("key_speed", 10.0)
channel.set_float_parameter("cam_sens", 0.25)
env = UnityToGymWrapper(unity_env, uint8_visual=True)

# interface
max_mouse_move = 10 # in pixel; to limit mouse "jump" due to slow in-loop process
mouse_position = np.zeros((2,))
def mouse_move(event):
    global mouse_position
    x, y = event.xdata, event.ydata
    mouse_position = np.array([x, y])

key_wasd = np.array([False] * 4)
def key_press(event): # NOTE: cannot handle multiple key press at the same time
    global key_wasd
    try:
        key = event.key.lower()
    except:
        key = event.key
    key_wasd[0] = True if key in ['w', 'up'] else False
    key_wasd[1] = True if key in ['a', 'left'] else False
    key_wasd[2] = True if key in ['s', 'down'] else False
    key_wasd[3] = True if key in ['d', 'right'] else False
    if key == 'q':
        env.close()
        sys.exit()
    sys.stdout.flush()

fig, ax = plt.subplots()
fig.canvas.mpl_connect('motion_notify_event', mouse_move)
fig.canvas.mpl_connect('key_press_event', key_press)

# helper
print("Select matplotlib window. Press arrow keys to move. Use mouse to rotate.\n" +
      "Don't use w/a/s/d since some keys are conflict with matplotlib default hotkey.\n" +
      "Press q to end game.")

# run
obs = env.reset()
im = ax.imshow(obs)
plt.tight_layout()
plt.show(block=False)
img_h, img_w = obs.shape[:2]
done = False
last_mouse = mouse_position
while not done:
    act = np.zeros((5,))

    # process mouse movement to get rotational action
    if np.all(mouse_position != None) and np.all(last_mouse != None):
        d_mouse = (mouse_position - last_mouse) * np.array([img_h, img_w])
        last_mouse = mouse_position
        d_mouse_norm = np.linalg.norm(d_mouse)
        if d_mouse_norm > max_mouse_move:
            d_mouse = d_mouse / d_mouse_norm * max_mouse_move
        act[2:4] = d_mouse
        act[3] *= -1 # axis upside down
    elif np.all(last_mouse == None): # in case mouse move out-of-bound and move in bound at different places
        last_mouse = mouse_position
    else:
        last_mouse = np.array([None, None])

    # process keyboard to get translational action
    if key_wasd[0]:
        act[1] = 1.0
    if key_wasd[1]:
        act[0] = -1.0
    if key_wasd[2]:
        act[1] = -1.0
    if key_wasd[3]:
        act[0] = 1.0
    key_wasd = np.array([False] * 4)

    # step in environment
    obs, _, _, _ = env.step(act)
    im.set_data(obs)

    # update mpl windows
    fig.canvas.draw()
    plt.pause(0.05)
