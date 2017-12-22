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
Download or clone the package from github.  
If `git` is available the package can be cloned directly from github:
```commandline
git clone https://github.com/isonder/luminance.git
```
This will create a local compy of the upstream repository in a local folder
named 'luminance'.

Otherwise the package can be downloaded as a zip file, and should be unpacked.

### Using `pip`
Then create a new virtual  environment.
```commandline
cd "/home/of/my/workspace"
git clone https://github.com/isonder/luminance.git
mkvirtualenv -p /usr/bin/python3 lum
toggleglobalsitepackages
cd luminance
pip install -r requirements.txt
```
Once all dependencies are installed, start a jupyter notebook (server) process
on your local machine
```commandline
jupyter notebook
```

### Using `conda`
We need all packages listed in the requirements.txt file installed. This can be
done either in a terminal that knows the `conda` command with
```commandline
conda install --yes 'packagename'
``` 
for each listed package (replace 'packagename' with the packages name). Or the
packages can be installed using the graphical installer that comes with the
Anaconda distribution.