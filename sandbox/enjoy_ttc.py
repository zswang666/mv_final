import sys
import numpy as np
import matplotlib.pyplot as plt

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel

from ttc import solve_ttc_multiscale, solve_ttc
from ttc.util import rgb2gray, uniform_blur, restrict

from PIL import Image
import io

def to_img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

GRAVITY = -9.81
UNITY_STEP_FREQ = 50 # hz


# setup environment
mass = 1.0
thrust_multiplier = 30.0
if sys.platform == "win32":
    env_build = "../env/FreeFall/windows/FreeFall.exe"
elif sys.platform == "linux":
    env_build == "../env/FlyCamera/linux/FreeFall.x86_64"
else:
    raise AttributeError("{} platform is not supported.".format(sys.platform))
channel = EnvironmentParametersChannel()
unity_env = UnityEnvironment(env_build, side_channels=[channel])
env = UnityToGymWrapper(unity_env, uint8_visual=True, allow_multiple_obs=True)
channel.set_float_parameter("mass", mass)
channel.set_float_parameter("thrust_multiplier", thrust_multiplier)
# NOTE: you can also set agent's starting position through position.x, position.y, position.z

# interface
key_ws = np.array([False] * 2)
def key_press(event): # NOTE: cannot handle multiple key press at the same time
    global key_ws
    try:
        key = event.key.lower()
    except:
        key = event.key
    key_ws[0] = True if key in ['w', 'up'] else False
    key_ws[1] = True if key in ['x', 'down'] else False
    if key == 'q':
        env.close()
        sys.exit()
    sys.stdout.flush()

fig, ax = plt.subplots()
fig.canvas.mpl_connect('key_press_event', key_press)

# helper
print("Select matplotlib window. Press arrow keys to move (only up and down). \n" +
      "Don't use w/s since some keys are conflict with matplotlib default hotkey.\n" +
      "Press q to end game.")

# run
obs = env.reset()
im = ax.imshow(obs[0])
plt.tight_layout()
fig.subplots_adjust(top=0.93)
plt.show(block=False)
img_h, img_w = obs[0].shape[:2]
m, n = img_h, img_w
done = False
i = 0
velo = np.zeros((3,))

# TTC
prev_frame = None
foe_marker = None
landing_threshold = 40

from collections import deque
ttcs = deque(maxlen=10)
has_landed = False
imgs = []

while not done:
    T = 0
    # process keyboard to get action
    act = 0.0
    if key_ws[0]:
        act += 1.0
    if key_ws[1]:
        act -= 1.0
    key_ws = np.array([False] * 2)

    # step in environment
    frame = uniform_blur(restrict(rgb2gray(obs[0])), 5)
    if not has_landed:
        #print('Landed')
        if prev_frame is not None:
            try:
                T, x0, y0, Ex, Ey, Et, v = solve_ttc_multiscale(prev_frame, frame)
                ttcs.append(T)
                dt = 1. / UNITY_STEP_FREQ
                if abs(np.mean(ttcs)) < landing_threshold:
                    next_velo_y = 0
                    has_landed = True
                    imgs[0].save(fp='animation.gif', format='GIF', append_images=imgs,
                            save_all=True, duration=200, loop=0)
                else:
                    next_velo_y = -2 * 0.01 * T
                acc = (next_velo_y - velo[1]) / dt - GRAVITY
                act = (acc * mass) / thrust_multiplier

                print('TTC={}, act={}, V*={}'.format(T, act, next_velo_y))
            except:
                pass
    else:
        next_velo_y = 0
        acc = (next_velo_y - velo[1]) / dt - GRAVITY
        act = (acc * mass) / thrust_multiplier
        print('Hover, act=',act)
        
    obs, _, _, _ = env.step(act)
    img = obs[0]
    im.set_data(img)
    
    if prev_frame is not None:
        if foe_marker is not None:
            foe_marker.remove()
            
        foe_marker = ax.annotate('X', 
                                (x0+(n)/2, y0+(m)/2), 
                                textcoords="offset points", 
                                xytext=(0,0), 
                                color='r',
                                ha='center') 
    
    prev_frame = frame
    
    dt = 1. / UNITY_STEP_FREQ
    acc = act * thrust_multiplier / mass
    next_velo_y = velo[1] + (GRAVITY + acc) * dt

    velo_y_err = np.absolute(next_velo_y - obs[1][1])
    
    #print("Velocity error (y-axis) = {}".format(velo_y_err))
    velo = obs[1]
    
    ax.set_title("Velocity = ({:.2f}, {:.2f}, {:.2f}), TTC = {:.2f}".format(*velo, T))
    

    # example of resetting environment
    if False:
        i += 1
        if i > 10:
            channel.set_float_parameter("end_episode", 1.0)
            i = 0
        else:
            channel.set_float_parameter("end_episode", 0.0)

    # update mpl windows
    fig.canvas.draw()
    plt.pause(0.05)
    
    if not has_landed:
        imgs.append(to_img(fig))
