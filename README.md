# pygplates-usecases-Updated
"pygplates-usecases" repository, including the notebooks and codes, URL, python version (improved from 2.7 to 3.7), is modified for both Windows and Linux users.

The old python 2 version is kept in branch 20200729-backup.

In case of the notebook "Subduction_history_and_slab_flux", there are several points that could be helpfull:
### 1. The codes are based on Python 3.7
### 2. You may get some errors due to lack of some of the required libraries or so on. For example:
#### 2.1. ModuleNotFoundError: No module named 'mpl_toolkits.basemap'
You would need to install “basemap” using the below command through your notebook or Anaconda Powershell Prompt: conda install basemap
Also, then if you get such errors as following:
"EnvironmentNotWritableError: The current user does not have write permissions to the target environment.
  environment location: C:\ProgramData\Anaconda3"
This is an administrative error. You need to open this folder "C:\ProgramData\" and right-click on "\Anaconda3". Go to properties -> security and check all the boxes for each user.

#### 2.2. KeyError: 'PROJ_LIB'
You would need to get it fixed through your notebook or Anaconda Powershell Prompt:
For the conda version of basemap it needs the PROJ_LIB variable to be set so it can find the epsg data.
For example, if the epsg data is packaged with the proj4 package, and the epsg data is located in such as folder/directory:
C:\ProgramData\Anaconda3\pkgs\proj4-5.1.0-hfa6e2cd_1\Library\share
Therefore the following two lines in the python script that imports basemap solves the issue:
import os
os.environ['PROJ_LIB'] = r'C:\ProgramData\Anaconda3\pkgs\proj4-5.1.0-hfa6e2cd_1\Library\share'

#### 2.3. If you are on Windows, you can remove "tmp/" to run the codes.
#### 2.4. ModuleNotFoundError: No module named 'netCDF4' 
You would need to install 'netCDF4' using Conda or pip.

#### 2.5. OSError: [Errno -51] NetCDF: Unknown file format: b'muller_etal_2016_areps_v1.17_agegrid-0.nc'
For such errors, it is better to removed the files in downloaded from a URL, and downoad and execute them again. Otherwise, even by improving the codes, you cannot execute them correctly and you would get the same error.

### 3. "Healpy" module
It is a proper tool to generate the mesh. However, it is only compatible with Linux and Apple (OSX). To install this package using conda run one of the commands in this link: https://anaconda.org/conda-forge/healpy Windows users instead can use GPlates software to generate the mesh files. The other possibility is applying this code: https://github.sydney.edu.au/EarthByte/spatio-temporal-exploration/blob/master/python/icosahedron.ipynb
