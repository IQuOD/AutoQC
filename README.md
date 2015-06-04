AutoQC
======

##Introduction

Recent studies suggest that changes to global climate as have been seen at the Earth's land and ocean surface are also making their way into the deep ocean, which is the largest active storage system for heat and carbon available on the timescale of a human lifetime. Historical measurements of subsurface ocean temperature are essential to the scientific research investigating the changes in the amount of heat stored in the ocean and also to other climate research activities such as combining observations with numerical models to provide estimates of the global ocean's and Earth's climate state  in the past and predictions for the future. Unfortunately, as with all observations, these measurements contain errors and biases that must be identified to prevent a negative impact on the applications and investigations that rely on them. Various groups from around the world have developed quality control tests to perform this important task. However, this has led to duplication of effort, code that is not easily available to other researchers and the introduction of climate model differences solely due to the varying performance of these software systems whose nuances relative to one another are poorly known.

Recently, an international team of researchers has decided to work together to break down the barriers between the various groups and countries through the formation of the IQuOD (International Quality Controlled Dataset) initiative. One of the key aims is to intercompare the performance of the various automatic quality control tests that are presently being run to determine a best performing set. This work has started. However, it currently involves individuals running test datasets through their own systems and is being confounded by complications associated with the differences in the file formats and systems that are in use in the various labs and countries.

The IQuOD proposal is to set up an open quality control benchmarking system.  Work will begin by implementing a battery of simple tests to run on some test data, and producing summary statistics and visualizations of the results.  Later goals include helping researchers either wrap their existing C, Fortran and Matlab test functions in Python for use in this test suite, or re-implementing those tests in native Python.

## Dependencies:

Uses `pyproj`, `shapely` and `geos` for geographical calculations.

Uses netcdf4 for data format handling.

The following assume an [Anaconda install](https://store.continuum.io/cshop/anaconda/) of Python

To install on OSX:

```
sudo pip install pyproj
sudo pip install shapely
brew install geos

brew tap Homebrew/homebrew-science
brew install hdf5
export HDF5_DIR=/usr/local/Cellar/hdf5/
conda install netcdf4
```

##Usage
To execute the quality control checks,
`python AutoQC.py`

##Structure
`AutoQC.py` performs the following:
 - automatically detects all quality control tests found in `/qctests`
 - takes the list of raw data files from `datafiles.json`, and decodes their contents into an array of profile objects
 - runs all the automatically detected tests over each of these profiles
 - return an array for each each test indicating which profiles excpetions were raised for, and an array indicating the expected result for each profile

###Testing
Each quality control test must be written as its own file in `/qctests`, of the form `def test(p)`, where `p` is a profile object; each test returns a bool, where `True` indicates the test has *failed*.

###Data
Each data file listed in `datafiles.json` is in the World Ocean Database (WOD; http://www.nodc.noaa.gov/OC5/WOD/pr_wod.html) ASCII format.

###Profile Objects Specification
[TBD]

##Contributing
Quality control checks waiting to be implemented are listed in the Issues. If you would like to work on coding up a check, please assign yourself to the issue to avoid others duplicating the effort.
