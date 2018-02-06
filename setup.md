## Software Dependencies

1. The code depends on the command line of the `ffmpeg` utility. In order to convert the videos to image sequences, it needs to be available on the command line system wide.
  - On *Linux* this should be available as a standard package.
  - On *MacOS* [this guide](https://superuser.com/questions/624561) shows several ways to set it up. The second choice seems to be the easiest.
  - On *Windows* [this is a nice setup guide on StackExchange](https://video.stackexchange.com/questions/20495).
2. The code is written in Python, and depends on a number of scientific packages. If a Python distribution with the `pip` tool is available this should work. Otherwise the [Anaconda distribution](https://www.anaconda.com/distribution/) is recommended for use. If using Anaconda make sure to install the Python 3 version. The **code will not run under Python 2**. It may be useful to run things in a virtual environment; but this is not strictly necessary.
3. The following packages are necessary, and can be installed with
  ```bash
  pip install packagenames
  ```
  or for the `conda`case
  ```bash
  conda install packagenames
  ```
  `packagenames` has to be replaced with the following package names, separated by spaces:
  - jupyter
  - matplotlib
  - numpy
  - scipy
  - pillow
  - slicerator
  - PIMS
  
  The `jupyter` and `matplotlib` packages are not mandatory, but recommended. To run the example notebook they are required, though. When using `conda` the last (`pims`) package has to be installed from the conda-forge repository:
  ```bash
  conda install -c conda-forge pims
  ```

## Setup

Download or clone this package from GitHub using the above green button, and unzip the contents into a location with write access. Then start a local jupyter notebook server either from the menu or from the command line.
```bash
jupyter notebook
```
From the notebook file browser open the `Luminance-example.ipynb` notebook and enjoy.

If `git` is available the package can be cloned directly from github:
```bash
git clone https://github.com/isonder/luminance.git
```
This will create a local compy of the upstream repository in a local folder
named 'luminance'.


## Quickstart

All of the above can be skipped if `pip`, `virtualenvwrapper`, and `git` are available. Then the following commands will clone the package in the current directory, create a virtual environment called `lum`, and install the necessary dependencies:
```bash
git clone https://github.com/isonder/luminance.git
mkvirtualenv -p /usr/bin/python3 lum
toggleglobalsitepackages
cd luminance
pip install -r requirements.txt
```
