# Controlled Landing With TTC
Final project of 6.801/6.866 Machine Vision

## Quick Start
* Install packages
  * `pip install matplotlib`
  * `pip install mlagents-envs`
  * `pip install gym_unity`
  * `pip install attrdict`
  * Clone [williamd4112/py-ttc](https://github.com/williamd4112/py-ttc) and run `pip install -e .`
* Get Unity build
  * Download from [here](https://drive.google.com/drive/folders/1kw6Mc1XH4kpysUhAgfOJmEzQpdKhyrY7?usp=sharing) to `env/`
  * Decompress the file and it should look like
    ```
    env/
      |_FlyCamera/ (or whatever environment name)
            |_windows/
            |_linux/
    ```
* Go to `sandbox/` and run sample code `python enjoy_flycamera.py`
* Go to `ttc_landing/` and run `python run_basic.py`

## Work on Unity
* There are assets not included in the repo (since they are too large) but used in Unity development. You need to download them online.
  * [Standard Assets](https://assetstore.unity.com/packages/essentials/asset-packs/standard-assets-for-unity-2018-4-32351)
  * [3D Realistic Terrain Free](https://assetstore.unity.com/packages/3d/environments/landscapes/3d-realistic-terrain-free-182593)
  * [Unity Cloud Shadows](https://github.com/EntroPi-Games/Unity-Cloud-Shadows/)
  * [SciFi Enemies and Vehicles](https://assetstore.unity.com/packages/3d/characters/robots/scifi-enemies-and-vehicles-15159)

## Experiments on TTC landing control in different scenarios
- Basic
``` 
python run_basic.py
```
- Dust
``` 
python run_dust.py
```
- Cloudy
``` 
python run_cloudy.py
```
- RotationalLight
``` 
python run_rotaional_light.py
```
- Windy
``` 
python run_windy.py
```

## Plotting the results
```
python plot_all_results.py --logdir results/{Basic, Dust, Cloduy, Windy}
```

