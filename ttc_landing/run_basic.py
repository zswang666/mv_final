from attrdict import AttrDict

from wrappers import make_unity_env
from experiments import run_experiment

#### Environment parameters (NOTE: can also be set across episode as they make effect at episode start)
config = AttrDict({
    "mass": 1.0,
    "control_multiplier": 1.0,
    "action_mode": [0.0, 1.0][1], # thrust control (0.0) / velocity control (1.0)
    "dust_storm": AttrDict({ # TODO: thicker dust storm not obvious
        "enable": 0.0, # float value other than 0.0 will enable
        "start_size_multiplier": 25.0 # particle size; larger value gives thicker dust storm
    }),
    "wind_zone": AttrDict({ # NOTE: remember to set freeze_position.x/y to false when enabling wind zone
        "enable": 0.0, # float value other than 0.0 will enable
        "force_low": AttrDict({ # random wind with force subject to uniform[low, high]
            "x": -10.0, 
            "y": 0.0, # y-axis wind force should always be zero as this is up-and-down direction
            "z": -10.0,
        }),
        "force_high": AttrDict({ # constant directional wind force over the object
            "x": 10.0, 
            "y": 0.0, # y-axis wind force should always be zero as this is up-and-down direction
            "z": 10.0,
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
    "cloud_shadow": AttrDict({
        "enable": 0.0, # float value other than 0.0 will enable
        "world_size": 300.0, # don't set to very small value otherwise cloud movement looks discrete
        "speed_multiplier": 5.0, # larger values give faster moving cloud (shadow)
        "coverage_modifier": 0.0, # -1.0 ~ 1.0, larger value gives larger coverage of shadow 
    }),
    "rotational_light": AttrDict({ # light rotates about x-axis within +-interval with fixed step size
        "enable": 0.0, # float value other than 0.0 will enable
        "interval": 10.0, # light rotate in the range of light_original_rotation +- interval
        "step": 1.0 # larger number gives faster rotating light source
    }),
    "position": AttrDict({ # starting position of the object
        "x": -120.9,
        "y": 27.4834, 
        "z": 792.7
    }),
    "landing_zone": AttrDict({
        "enable":  0.0, # float value other than 0.0 will enable
        "offset": AttrDict({
            "x": 31.5,
            "y": -47.4,
            "z": 23.5
        })
    })
})
####

env = make_unity_env(config)
run_experiment(env,
    logger_kwargs={'base_dir': './results_ver2/Basic'},
    controller_kwargs={'max_velocity': 24, 'smooth_window': 10})
