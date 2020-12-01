import sys
import numpy as np
import matplotlib.pyplot as plt
from attrdict import AttrDict

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel


GRAVITY = -9.81
UNITY_STEP_FREQ = 50 # hz
RAY_MAX = 1000
RAY_OFFSET = -0.1446


#### Environment parameters (NOTE: can also be set across episode as they make effect at episode start)
config = AttrDict({
    "mass": 1.0,
    "thrust_multiplier": 30.0,
    "action_mode": [0.0, 1.0][0], # thrust control (0.0) / velocity control (1.0)
    "dust_storm": AttrDict({ # TODO: thicker dust storm not obvious
        "enable": 0.0, # float value other than 0.0 will enable
        "start_size_multiplier": 25.0 # particle size; larger value gives thicker dust storm
    }),
    "wind_zone": AttrDict({ # NOTE: remember to set freeze_position.x/y to false when enabling wind zone
        "enable": 0.0, # float value other than 0.0 will enable
        "force": AttrDict({ # constant directional wind force over the object
            "x": 1.0, 
            "y": 0.0, # y-axis wind force should always be zero as this is up-and-down direction
            "z": 1.0,
        })
    }),
    "rigid_body": AttrDict({ 
        "freeze_position": AttrDict({ # float value other than 0.0 is true
            "x": 1.0,
            "y": 0.0, # never fix y translation as we are doing free fall
            "z": 1.0,
        }),
        "freeze_rotation": AttrDict({ # float value other than 0.0 is true
            "x": 1.0,
            "y": 1.0,
            "z": 1.0,
        })
    }),
    "cloud_shadow": AttrDict({ # TODO: cloud movement looks discrete
        "enable": 0.0, # float value other than 0.0 will enable
        "speed_multiplier": 5.0, # larger values give faster moving cloud (shadow)
        "coverage_modifier": 0.0, # -1.0 ~ 1.0, larger value gives larger coverage of shadow 
    }),
    "position": AttrDict({ # starting position of the object
        "x": -120.9,
        "y": 27.4834, 
        "z": 792.7
    })
})
####

def assign_config(_channel, _config, k_prefix=None):
    for k, v in _config.items():
        k = ".".join([k_prefix, k]) if k_prefix is not None else k
        if isinstance(v, AttrDict):    
            assign_config(_channel, v, k)
        else:
            _channel.set_float_parameter(k, v)

# setup environment
if sys.platform == "win32":
    env_build = "../env/FreeFall/windows/FreeFall.exe"
elif sys.platform == "linux":
    env_build = "../env/FlyCamera/linux/FreeFall.x86_64"
elif sys.platform == "darwin":
    env_build = "../env/FreeFall/mac.app"
else:
    raise AttributeError("{} platform is not supported.".format(sys.platform))
channel = EnvironmentParametersChannel()
unity_env = UnityEnvironment(env_build, side_channels=[channel])
env = UnityToGymWrapper(unity_env, uint8_visual=True, allow_multiple_obs=True)
assign_config(channel, config)

# interface
key_ws = np.array([False] * 2)
def key_press(event): # NOTE: cannot handle multiple key press at the same time
    global key_ws
    try:
        key = event.key.lower()
    except:
        key = event.key
    key_ws[0] = True if key in ['w', 'up'] else False
    key_ws[1] = True if key in ['s', 'down'] else False
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

# raycast
def process_ray(ray_obs):
     # idk what obs[1][:1] is
    return ray_obs[2] * RAY_MAX + RAY_OFFSET

# run
obs = env.reset()
dist_curr = process_ray(obs[1])
im = ax.imshow(obs[0])
plt.tight_layout()
fig.subplots_adjust(top=0.898)
plt.show(block=False)
img_h, img_w = obs[0].shape[:2]
done = False
i = 0
velo = np.zeros((3,))
while not done:
    # process keyboard to get action
    act = 0.0
    if key_ws[0]:
        act += 1.0
    if key_ws[1]:
        act -= 1.0
    key_ws = np.array([False] * 2)

    # step in environment
    obs, _, _, _ = env.step(act)
    img = obs[0]
    im.set_data(img)
    
    if False: # sanity check
        # current environment lock motion of x and z axes
        dt = 1. / UNITY_STEP_FREQ
        acc = act * thrust_multiplier / mass
        next_velo_y = velo[1] + (GRAVITY + acc) * dt
        velo_y_err = np.absolute(next_velo_y - obs[1][4])

        # use velocity to compute distance
        dist_curr = dist_curr + obs[1][4] * dt
        dist_err = np.absolute(dist_curr - process_ray(obs[1]))

        print("Velocity error (y-axis) = {}, Distance error = {}".format(velo_y_err, dist_err))
    
    velo = obs[1][3:]
    distance_to_ground = process_ray(obs[1])
    ax.set_title("Velocity = ({:.2f}, {:.2f}, {:.2f})\n Distance to Ground: {:.8f}".format(\
        *velo, distance_to_ground))

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
