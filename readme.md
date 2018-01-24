# _*_ under construction _*_

**this is not working yet**

### Analysis of Explosive Magma-Water Interaction Experiment Video Recordings

Compute explosive response ('activity') based on a simple brightness scale.

## Software Dependencies
- The `ffmpeg` video editing command line utility.
- Some scientifically enabled Python distribution. Let's assume `pip` or `conda`
 are available.  
**if not**:  
  - *Windows*: The easiest option is probably to download and install the
   Anaconda distribution (the 'Miniconda' version should be enough):
    https://www.anaconda.com/distribution/
  - *Mac*: See above
  - *Linux*: Either version, `pip` or `conda`, should work. When using `pip`,
   the `virtualenv` and `virtualenvwrapper` are recommended.

## Setup
Download or clone the package from github. Then create a new virtual
 environment.
```bash
cd "/home/of/my/workspace"
git clone https://github.com/isonder/luminance.git
mkvirtualenv -p /usr/bin/python3 lum
toggleglobalsitepackages
pip install -r requirements.txt
```
...