# Controlled Landing With TTC
Final project of 6.801/6.866 Machine Vision

## Quick Start
* Install packages
  * `pip install matplotlib`
  * `pip install mlagents-envs`
  * `pip install gym_unity`
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